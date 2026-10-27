"""Kai 4.0 island: floating Dynamic Island capsule, native Qt with a stable canvas."""
import datetime as dt
import math
from pathlib import Path
import random
import sys
import threading
import time

from PySide6.QtCore import QObject, QPointF, QRect, QRectF, Qt, QTimer, Signal, QBuffer, QByteArray, QIODevice, QSize, QLockFile
from PySide6.QtGui import (QAction, QBrush, QColor, QCursor, QFont, QFontMetrics,
    QGuiApplication, QIcon, QLinearGradient, QPainter, QPainterPath, QPen,
    QPixmap, QRadialGradient, QRegion, QImageReader, QConicalGradient, QPixmapCache)
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget, QLineEdit, QAbstractSpinBox, QPlainTextEdit
import config
import events

FONT = 'Segoe UI Variable'
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
TONES = {'idle': '#ffffff', 'listen': '#0a84ff', 'busy': '#ff9f0a',
         'ok': '#30d158', 'err': '#ff453a'}
LABEL2 = '#9b9ba1'


def lerp(a, b, t):
    return a + (b - a) * t


def body_path(rect,radius):
    """Floating capsule: every corner rounded, never wider than a full pill."""
    radius=min(radius,rect.height()/2,rect.width()/2)
    path=QPainterPath();path.addRoundedRect(rect,radius,radius);return path


class Spring:
    """Exact damped-spring solution. Retargeting preserves velocity.

    damping=1 is critically damped (no overshoot); below 1 settles with a soft bounce."""
    def __init__(self, value=0.0, frequency=24.0, damping=1.0):
        self.value = self.target = value
        self.velocity = 0.0
        self.frequency = frequency
        self.damping = damping

    def step(self, seconds):
        seconds = max(0.0, seconds)
        w, z = self.frequency, self.damping
        offset = self.value - self.target
        if z >= 1:
            b = self.velocity + w * offset
            decay = math.exp(-w * seconds)
            self.value = self.target + (offset + b * seconds) * decay
            self.velocity = (self.velocity - w * b * seconds) * decay
        else:
            wd = w * math.sqrt(1 - z * z)
            decay = math.exp(-z * w * seconds)
            c, s = math.cos(wd * seconds), math.sin(wd * seconds)
            v0 = self.velocity
            self.value = self.target + decay * (offset * c + (v0 + z * w * offset) / wd * s)
            self.velocity = decay * (v0 * c - (z * w * v0 + w * w * offset) / wd * s)
        if self.settled:
            self.value, self.velocity = self.target, 0.0
        return self.value

    @property
    def settled(self):
        return abs(self.value - self.target) < 0.0005 and abs(self.velocity) < 0.005


class Presence:
    """Monotonic hover hysteresis and event hold."""
    def __init__(self, delay=0.7):
        self.delay = delay
        self.leave_since = None
        self.pin_until = 0.0
        self.expanded = False

    def update(self, hovered, now):
        if hovered:
            self.leave_since = None
        elif self.leave_since is None:
            self.leave_since = now
        self.expanded = (hovered or now < self.pin_until or
                         (self.expanded and now - self.leave_since < self.delay))
        return self.expanded


class Bridge(QObject):
    sig = Signal(str, str, object)


class Island(QWidget):
    requested = Signal(str)

    def __init__(self, reduced_motion=False, demo=False, interactive=False):
        super().__init__()
        self.setWindowTitle('Kai Island')
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        self.setWindowFlags((flags & ~Qt.WindowDoesNotAcceptFocus) if interactive else flags | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAccessibleName('Kai desktop island')
        self.reduced_motion = reduced_motion
        self.demo = demo
        self.interactive = interactive
        self.setAcceptDrops(interactive)
        self.setMouseTracking(interactive)
        self._input_enabled = None
        self._backdrop = None
        self._glass_failed = False
        self._detail_motion = Spring(frequency=28)
        self._height_motion = Spring(value=280,frequency=28)
        self._notice_motion = Spring(frequency=28)
        self._detail = 0.0
        self._deck = None
        self._deck_open = False
        self._navigation_anchor = None
        self._media, self._audio = {}, {}
        self._job = None
        self._cover, self._cover_key = QPixmap(), None
        self._album_color=None
        self._card, self._card_until = 'default', 0.0
        self._context={}
        self._motion = Spring(frequency=config.ISLAND_SPRING_FREQUENCY, damping=config.ISLAND_SPRING_DAMPING)
        self._tall = Spring(frequency=20, damping=.85)  # height trails width, like the iPhone island
        self._look = Spring(frequency=16)   # eyes follow the pointer
        self._pull = Spring(frequency=14)   # magnetic stretch as the pointer approaches
        self._ph = 0.0
        self._blink_started = -1.0
        self._presence = Presence(config.ISLAND_COLLAPSE_DELAY)
        self._p, self._open = 0.0, False
        self._dim, self._main, self._tone = '', 'Kai is ready', 'idle'
        self._last_frame = time.perf_counter()
        self._screen = None
        self._position()
        self._frames = QTimer(self)
        self._frames.setTimerType(Qt.PreciseTimer)
        self._frames.setInterval(8)
        self._frames.timeout.connect(self._frame)
        self._timer = QTimer(self)
        self._timer.setInterval(config.ISLAND_CURSOR_INTERVAL_MS)
        self._timer.timeout.connect(self._poll)
        self._timer.start()
        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self._tick_clock)
        self._clock.start()
        self._blink = QTimer(self)
        self._blink.setSingleShot(True)
        self._blink.timeout.connect(self._start_blink)
        self._blink.start(random.randint(5000, 9000))
        QGuiApplication.instance().primaryScreenChanged.connect(self._position)

    def _position(self, *_):
        if getattr(self,'_backdrop',None): self._backdrop.close();self._backdrop=None
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        if self._screen is not screen:
            if self._screen is not None:
                try:
                    self._screen.geometryChanged.disconnect(self._position)
                except (RuntimeError, TypeError):
                    pass
            self._screen = screen
            screen.geometryChanged.connect(self._position)
        geometry = screen.geometry()
        self._panel_width = min(config.ISLAND_EXPANDED_WIDTH, max(200, geometry.width() - 64))
        # ponytail: fixed canvas; interactive regions arrive with real media controls.
        self._deck_width = min(540, max(300, geometry.width()-64))
        width = self._deck_width + 64
        self.setGeometry(geometry.center().x() - width // 2, geometry.y(), width, 420)

    def body_rect(self):
        # Springs may overshoot slightly above 1; the canvas leaves room for it.
        p, ph = max(0.0, self._p), max(0.0, self._ph)
        pull = max(0.0, self._pull.value) * max(0.0, 1 - p)
        compact_width=lerp(self._panel_width,min(self._panel_width,290),self._notice_motion.value)
        compact_height=lerp(config.ISLAND_EXPANDED_HEIGHT,56,self._notice_motion.value)
        expanded_width = lerp(compact_width,self._deck_width,self._detail)
        expanded_height = lerp(compact_height,self._height_motion.value,self._detail)
        width = lerp(config.ISLAND_COLLAPSED_WIDTH + 12 * pull, expanded_width, p)
        height = lerp(config.ISLAND_COLLAPSED_HEIGHT + 2 * pull, expanded_height, ph)
        return QRectF((self.width() - width) / 2, config.ISLAND_TOP, width, height)

    def _radius(self, rect):
        p = min(1.0, max(0.0, self._p))
        compact = lerp(config.ISLAND_COMPACT_RADIUS, 28, self._notice_motion.value)
        return min(rect.height() / 2, lerp(rect.height() / 2, lerp(compact, config.ISLAND_DECK_RADIUS, self._detail), p))

    def _hot_rect(self):
        if self._open or self._p > 0.15:
            rect = self.body_rect().adjusted(-16,-config.ISLAND_TOP,16,16)
        else:
            rect = QRectF((self.width() - config.ISLAND_HOT_WIDTH) / 2, 0,
                          config.ISLAND_HOT_WIDTH, config.ISLAND_TOP + 34)
        return QRect(self.mapToGlobal(rect.topLeft().toPoint()), rect.size().toSize())

    def _poll(self):
        now = time.monotonic()
        if getattr(self,'_desktop_actions',None) and now>=getattr(self,'_target_checked',0):
            self._desktop_actions.remember();self._target_checked=now+.25
        if self._card != 'default' and now >= self._card_until:
            self._card = 'default'
            self._context={}
            self._dim, self._main, self._tone = '', 'Kai is ready', 'idle'
            self._target(float(self._open))
        focused = QApplication.focusWidget()
        owns_focus = self._deck_open and ((isinstance(focused,(QLineEdit,QAbstractSpinBox,QPlainTextEdit)) and self.isAncestorOf(focused)) or QApplication.mouseButtons()!=Qt.NoButton or QApplication.activePopupWidget() is not None or QApplication.activeModalWidget() is not None)
        cursor=QCursor.pos()
        navigation_hold=self._deck_open and self._navigation_anchor is not None and (cursor-self._navigation_anchor).manhattanLength()<=8
        if not navigation_hold:self._navigation_anchor=None
        expanded = self._presence.update(bool(owns_focus) or navigation_hold or self._hot_rect().contains(cursor), now)
        self._attend(cursor, expanded)
        if expanded != self._open:
            self.open_island() if expanded else self.close_island()

    def _attend(self, cursor, expanded):
        """Eyes look toward the pointer; the pill leans in as it approaches."""
        look = pull = 0.0
        if not expanded and not self.reduced_motion:
            center = self.mapToGlobal(self.body_rect().center().toPoint())
            dx, dy = cursor.x() - center.x(), cursor.y() - center.y()
            distance = math.hypot(dx, dy)
            pull = max(0.0, 1 - distance / config.ISLAND_MAGNET_DISTANCE)
            look = max(-1.0, min(1.0, dx / 140)) if distance < 420 else 0.0
        if abs(pull - self._pull.target) > .01 or abs(look - self._look.target) > .02:
            self._pull.target, self._look.target = pull, look
            self._wake_frames()

    def _start_blink(self):
        if not self.reduced_motion and self._p < .3 and self.isVisible() and not self._frames.isActive():
            self._blink_started = time.perf_counter()
            self._wake_frames()
        self._blink.start(random.randint(4000, 9000))

    def _blinking(self):
        return 0 <= time.perf_counter() - self._blink_started < .14

    def _wake_frames(self):
        if not self._frames.isActive():
            self._last_frame = time.perf_counter()
            self._frames.start()

    def _target(self, target):
        self._motion.target = self._tall.target = target
        # Open with a soft bounce; shrink back crisply without one.
        opening = target > .5
        self._motion.damping = config.ISLAND_SPRING_DAMPING if opening else 1.0
        self._motion.frequency = config.ISLAND_SPRING_FREQUENCY if opening else 26.0
        self._tall.damping, self._tall.frequency = (.85, 20.0) if opening else (1.0, 26.0)
        self._notice_motion.target=float(self._card in ('shelf','result','error','context') and not self._deck_open)
        if self.reduced_motion:
            self._motion.value, self._motion.velocity = target, 0.0
            self._tall.value, self._tall.velocity = target, 0.0
            for spring in (self._look, self._pull):
                spring.value = spring.target = spring.velocity = 0.0
            self._ph = target
            self._detail_motion.value, self._detail_motion.velocity = self._detail_motion.target,0.0
            self._detail = self._detail_motion.value
            self._height_motion.value = self._height_motion.target
            self._notice_motion.value=self._notice_motion.target;self._notice_motion.velocity=0
            self._p = target
            self._after_anim()
            self._sync_input()
            self._sync_glass()
            self._sync_deck()
            self.update()
        else:
            self._frames.setInterval(8)
            self._wake_frames()

    def open_island(self):
        self._open = self._presence.expanded = True
        self._target(1.0)

    def close_island(self):
        self._hide_deck()
        self._open = self._presence.expanded = False
        self._target(0.0)

    def _frame(self):
        now = time.perf_counter()
        # Exact integration stays stable across delayed frames; clamping elapsed
        # time here makes the whole animation run slowly when Windows is busy.
        self._p = self._motion.step(now - self._last_frame)
        self._ph = self._tall.step(now - self._last_frame)
        self._look.step(now - self._last_frame)
        self._pull.step(now - self._last_frame)
        self._detail = self._detail_motion.step(now - self._last_frame)
        self._height_motion.step(now - self._last_frame)
        self._notice_motion.step(now-self._last_frame)
        self._last_frame = now
        self._sync_input()
        self._sync_glass()
        self._sync_deck()
        self.update()
        springs = (self._motion, self._tall, self._detail_motion, self._height_motion, self._notice_motion, self._look, self._pull)
        if all(spring.settled for spring in springs) and not self._blinking():
            self._after_anim()
            if self.reduced_motion or self._tone != 'listen' or not self._open:
                self._frames.stop()
            else:
                self._frames.setInterval(33)

    def _after_anim(self):
        if not self._open and self._p < 0.001:
            if self._backdrop: self._backdrop.close();self._backdrop=None
            self._dim, self._main, self._tone = '', 'Kai is ready', 'idle'
            self._card = 'default'

    def _tick_clock(self):
        if self._p > 0.5:
            self.update()

    def attach_deck(self, panel):
        if self._deck is not panel:
            panel.dismissed.connect(self.collapse_deck)
            panel.resized.connect(self.resize_deck)
        self._deck = panel
        panel.setParent(self)
        self._height_motion.target = panel.preferred_height()
        self._deck_open = True
        self._detail_motion.target = 1.0
        self._presence.pin_until = time.monotonic()+1
        self.open_island()
        self._sync_deck()

    def resize_deck(self,height):
        if self._deck_open and height<self._height_motion.value and self._hot_rect().contains(QCursor.pos()):
            self._navigation_anchor=QCursor.pos()
        self._height_motion.target = height
        self._target(1.0)
        self._sync_deck()

    def _sync_deck(self):
        if self._deck is None: return
        # Generous inset so content never crowds the 30 DIP rounded corners.
        x = round((self.width()-self._deck_width)/2)+28
        self._deck.setGeometry(x,round(self.body_rect().top())+18,self._deck_width-56,round(self._height_motion.target)-34)
        # Stay visible while the capsule morphs; the window mask clips it like a curtain.
        self._deck.setVisible(self._detail>.7 and self._p>.7)

    def _hide_deck(self):
        self._navigation_anchor=None
        self._deck_open = False
        self._detail_motion.target = 0.0
        if self._deck is not None:
            self._deck.close(); self._deck = None

    def collapse_deck(self):
        self._hide_deck()
        self._presence.pin_until = time.monotonic()+0.8
        self._target(1.0)
        if getattr(self,'_desktop_actions',None):self._desktop_actions.restore_focus()

    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Escape:
            self.dismiss(); return
        super().keyPressEvent(event)

    def set_reduced_motion(self, enabled):
        self.reduced_motion = enabled
        self._target(float(self._open))

    def dismiss(self):
        self._presence.pin_until = 0.0
        self._dim, self._main, self._tone = '', 'Kai is ready', 'idle'
        self._card = 'default'
        self.close_island()
        if getattr(self,'_desktop_actions',None):self._desktop_actions.restore_focus()

    def on_event(self, kind, text, data=None):
        if kind=='context':
            if self._deck_open:return  # Never replace a page while the user is working.
            self._context=data or {}
        if kind == 'media':
            self._media = data or {}
            key = (self._media.get('title'), self._media.get('artist'),bool(self._media.get('cover')))
            if key != self._cover_key:
                self._cover_key, self._cover = key, QPixmap()
                self._album_color=None
                if self._media.get('cover'):
                    buffer = QBuffer()
                    buffer.setData(QByteArray(self._media['cover']))
                    buffer.open(QIODevice.ReadOnly)
                    reader = QImageReader(buffer)
                    reader.setScaledSize(QSize(64, 64))
                    reader.setAllocationLimit(8)
                    self._cover = QPixmap.fromImage(reader.read())
                    if not self._cover.isNull():
                        image=self._cover.toImage().scaled(8,8)
                        colors=[image.pixelColor(x,y) for y in range(image.height()) for x in range(image.width())]
                        # One tiny average per cover change; no full-image blur/cache.
                        self._album_color=QColor(*(round(sum(c.getRgb()[i] for c in colors)/len(colors)*.42) for i in range(3)))
            if self._open: self.update()
            return
        if kind in ('audio_state', 'volume'):
            self._audio = data or {}
            if kind == 'audio_state': return
        if kind == 'timer_started':
            self._job = data
        if self._card == 'timer_done' and kind not in ('listening', 'error', 'timer_done'):
            return
        if kind == 'device' and data:
            text = data.get('name', text) + (' connected' if data.get('connected') else ' disconnected')
        if kind in ('info', 'intent'):
            return
        duration = {'loading': 120, 'ready': 2.5, 'listening': 30, 'processing': 30,
                    'heard': 10, 'result': 3.5, 'timer_done': float('inf'), 'error': 5,
                    'volume': 1.8, 'device': 3, 'timer_started': 3, 'weather': 5,
                    'shelf': 3,'context':4}.get(kind)
        if duration is None:
            return
        if kind == 'listening':
            self._main, self._dim, self._tone = 'Listening...', 'Release Ctrl + Space to process', 'listen'
        elif kind in ('processing', 'heard'):
            invalid = kind == 'heard' and text.startswith('(')
            self._main = text if invalid else 'Working...'
            self._dim = '' if invalid else text
            self._tone = 'err' if invalid else 'busy'
        else:
            self._dim = ''
            self._main = text or 'Kai is ready'
            self._tone = {'loading': 'busy', 'ready': 'idle', 'result': 'ok',
                          'timer_done': 'ok', 'error': 'err'}.get(kind, 'idle')
            if kind == 'result' and text.casefold().startswith(('failed', 'unable', 'no ', 'gagal', 'belum', 'tidak')):
                self._tone = 'err'
        self._presence.pin_until = time.monotonic() + duration
        self._card, self._card_until = kind, self._presence.pin_until
        self.open_island()
        self.update()

    def _sync_input(self):
        if not self.interactive:
            return
        enabled = self._open and self._p > 0.6
        if enabled != self._input_enabled or getattr(self,"_last_deck_input",None) != self._deck_open:
            self._last_deck_input = self._deck_open
            self._input_enabled = enabled
            self.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
            if sys.platform == 'win32' and QGuiApplication.platformName() == 'windows':
                import ctypes
                from ctypes import wintypes
                user = ctypes.WinDLL('user32', use_last_error=True)
                user.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
                user.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
                handle = int(self.winId())
                style = user.GetWindowLongW(handle, -20)
                user.SetWindowLongW(handle, -20, (style & ~0x20 if enabled else style | 0x20) & ~0x08000000 if self._deck_open else (style & ~0x20 if enabled else style | 0x20) | 0x08000000)
        if QGuiApplication.platformName() == 'windows':
            # 1.5 DIP margin keeps the antialiased edge; the region itself is aliased.
            rect = self.body_rect()
            path = body_path(rect.adjusted(-1.5,-1.5,1.5,1.5),self._radius(rect)+1.5)
            self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def _sync_glass(self):
        # Opaque black/album tint needs no native backdrop or blur surface.
        if self._backdrop:
            self._backdrop.close();self._backdrop=None

    def _mode(self):
        if self._card == 'volume': return 'volume'
        if self._card != 'default': return 'status'
        if self._job: return 'job'
        if self._media: return 'media'
        return 'default'

    def mousePressEvent(self, event):
        if not self.interactive or not self._open: return
        if event.button() == Qt.RightButton:
            self.requested.emit('settings'); return
        if self._card=='context':self.requested.emit('context');return
        position = event.position() - self.body_rect().topLeft()
        mode = self._mode()
        if self._card == 'timer_done':
            self.dismiss(); return
        if mode == 'volume':
            if position.x() < 50:
                self.requested.emit('mute')
            else:
                self.requested.emit('volume:' + str(round(max(0, min(1, (position.x() - 62) / (self._panel_width - 82))) * 100)))
        elif mode == 'media' and position.x() > self._panel_width - 86:
            index = min(2, max(0, int((position.x() - (self._panel_width - 86)) / 28)))
            self.requested.emit(('prev', 'toggle', 'next')[index])
        elif mode == 'job' and position.x() > self._panel_width - 62:
            self.requested.emit(('cancel_job:' if position.x() > self._panel_width - 30 else 'toggle_job:') + self._job['id'])
        else:
            if mode=='status' and self._card=='shelf':self.requested.emit('shelf')
            else:self.requested.emit('panel')

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._mode() == 'volume':
            position = event.position() - self.body_rect().topLeft()
            self.requested.emit('volume:' + str(round(max(0, min(1, (position.x() - 62) / (self._panel_width - 82))) * 100)))
        self.update()

    def showEvent(self, event):
        self._sync_input()
        super().showEvent(event)

    def dragEnterEvent(self, event):
        if self.interactive and event.mimeData().hasUrls():
            self._presence.pin_until = time.monotonic() + 15
            self.open_island()
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        from storage import get_store
        count = 0
        for url in event.mimeData().urls()[:100]:
            if url.isLocalFile():
                try:
                    get_store().add_file(url.toLocalFile()); count += 1
                except ValueError:
                    pass
        event.acceptProposedAction()
        self._card = 'default'
        self._card_until = 0.0
        self.requested.emit('shelf')

    def paintEvent(self, _):
        p = max(0.0, min(1.0, self._p))
        rect = self.body_rect()
        radius = self._radius(rect)
        body = body_path(rect, radius)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setRenderHint(QPainter.SmoothPixmapTransform)
        qp.setPen(Qt.NoPen)
        qp.setBrush(Qt.black);qp.drawPath(body)
        color=self._album_color if (self._deck_open and self._deck is not None and self._deck.current_page()=='Media' and self._media.get('playing')) else None
        if color is not None:
            qp.save();qp.setClipPath(body)
            tint=QLinearGradient(rect.topLeft(),rect.bottomRight())
            tint.setColorAt(0,QColor(0,0,0));tint.setColorAt(1,color)
            qp.fillRect(rect,tint);qp.restore()
        if p>.02:
            # Hairline keeps the black capsule legible on dark wallpapers.
            qp.setPen(QPen(QColor(255,255,255,int(22*p)),1));qp.setBrush(Qt.NoBrush)
            qp.drawPath(body_path(rect.adjusted(.5,.5,-.5,-.5),radius-.5))
        if p<.45:
            self._draw_eyes(qp, rect, 1-p/.45)
        alpha = min(1.0, max(0.0, (p - 0.55) / 0.4))
        alpha *= max(0,1-self._detail*2)
        if alpha:
            qp.save()
            qp.setClipPath(body)
            qp.setOpacity(alpha)
            # Content settles in: slight rise and scale, like a live activity.
            center = rect.center(); scale = .92 + .08 * alpha
            qp.translate(center.x(), center.y() + 6 * (1 - alpha)); qp.scale(scale, scale); qp.translate(-center.x(), -center.y())
            self._draw_content(qp, rect)
            qp.restore()
        qp.end()

    def _draw_eyes(self, qp, rect, opacity):
        t = (time.perf_counter() - self._blink_started) / .14
        height = 10 * (1 - .85 * math.sin(math.pi * t)) if 0 <= t < 1 else 10
        look = self._look.value * 2.5
        spread = 1 + .12 * max(0.0, self._pull.value)
        qp.save();qp.setOpacity(opacity);qp.setPen(Qt.NoPen);qp.setBrush(Qt.white)
        for offset in (-6.5,6.5):
            qp.drawRoundedRect(QRectF(rect.center().x()+offset*spread+look-2,rect.center().y()-height/2,4,height),2,min(2,height/2))
        qp.restore()

    def _text(self, qp, rect, text, size=14, color='#ffffff', weight=QFont.Normal, align=Qt.AlignLeft, spacing=0):
        font = QFont(FONT)
        font.setPixelSize(size)
        font.setWeight(weight)
        if spacing: font.setLetterSpacing(QFont.AbsoluteSpacing, spacing)
        qp.setFont(font)
        qp.setPen(QColor(color))
        qp.drawText(rect, align | Qt.AlignVCenter,
                    QFontMetrics(font).elidedText(text, Qt.ElideRight, int(rect.width())))

    def _glyph(self, qp, center, kind, color):
        """Tinted circle with a simple stroked glyph, like iPhone status icons."""
        tone = QColor(color); fill = QColor(tone); fill.setAlpha(46)
        qp.setPen(Qt.NoPen); qp.setBrush(fill); qp.drawEllipse(center, 17, 17)
        qp.setPen(QPen(tone, 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); qp.setBrush(Qt.NoBrush)
        x, y = center.x(), center.y()
        if kind == 'ok':
            path = QPainterPath(QPointF(x-6,y)); path.lineTo(x-2,y+4); path.lineTo(x+6,y-5); qp.drawPath(path)
        elif kind == 'err':
            qp.drawLine(QPointF(x,y-6),QPointF(x,y+1)); qp.drawPoint(QPointF(x,y+5.5))
        elif kind == 'link':
            qp.drawLine(QPointF(x-5,y+5),QPointF(x+5,y-5)); qp.drawLine(QPointF(x-1,y-5),QPointF(x+5,y-5)); qp.drawLine(QPointF(x+5,y-5),QPointF(x+5,y+1))
        elif kind == 'shelf':
            path = QPainterPath(QPointF(x-7,y-1)); path.lineTo(x-7,y+5); path.lineTo(x+7,y+5); path.lineTo(x+7,y-1); qp.drawPath(path)
            qp.drawLine(QPointF(x-3,y-1),QPointF(x+3,y-1)); qp.drawLine(QPointF(x,y-7),QPointF(x,y-1))
        else:
            for dx in (-5,0,5): qp.drawPoint(QPointF(x+dx,y))

    def _chip(self, qp, rect, label, color, text_color='#000000'):
        qp.setPen(Qt.NoPen); qp.setBrush(QColor(color)); qp.drawRoundedRect(rect, rect.height()/2, rect.height()/2)
        self._text(qp, rect, label, 11, text_color, QFont.DemiBold, Qt.AlignHCenter)

    def _draw_content(self, qp, rect):
        qp.save()
        qp.translate(rect.topLeft())
        w, h = rect.width(), rect.height()
        mode = self._mode()
        if mode in ('media', 'volume', 'job'):
            self._draw_card(qp, w, h, mode)
            qp.restore()
            return
        default = self._tone == 'idle' and self._main == 'Kai is ready'
        if default:
            now=dt.datetime.now()
            # Classy, logo-free: large clock left, date right; the colon breathes once a second.
            hours, minutes = now.strftime('%H'), now.strftime('%M')
            font = QFont(FONT); font.setPixelSize(28); font.setWeight(QFont.DemiBold); metrics = QFontMetrics(font)
            x = 28.0
            for part, alpha in ((hours, 255), (':', 255 if now.second % 2 == 0 else 90), (minutes, 255)):
                qp.setFont(font); qp.setPen(QColor(255, 255, 255, alpha))
                qp.drawText(QRectF(x, 0, metrics.horizontalAdvance(part) + 2, h), Qt.AlignLeft | Qt.AlignVCenter, part)
                x += metrics.horizontalAdvance(part)
            if not self._cover.isNull():
                path=QPainterPath(); path.addRoundedRect(QRectF(w-58,h/2-18,36,36),10,10)
                qp.save(); qp.setClipPath(path); qp.drawPixmap(QRectF(w-58,h/2-18,36,36),self._cover,QRectF(self._cover.rect())); qp.restore()
            else:
                self._text(qp,QRectF(w-190,h/2-17,162,14),WEEKDAYS[now.weekday()].upper(),10,LABEL2,QFont.DemiBold,Qt.AlignRight,spacing=1.2)
                self._text(qp,QRectF(w-190,h/2-1,162,20),f'{now.day} {MONTH_NAMES[now.month-1]}',14,'#ffffff',QFont.Medium,Qt.AlignRight)
        else:
            tone = TONES[self._tone]
            kind = {'ok':'ok','err':'err'}.get(self._tone,'busy')
            label = {'listen': 'LISTENING', 'busy': 'WORKING', 'ok': 'DONE', 'err': 'ATTENTION', 'idle': 'KAI'}[self._tone]
            chip = None
            if self._card == 'shelf':
                tone, kind, label = '#bf5af2', 'shelf', 'SHELF'
            if self._card == 'context':
                url = self._context.get('action') == 'url'
                tone, kind, label = ('#0a84ff','link','LINK') if url else ('#bf5af2','shelf','SHELF')
                chip = 'Open' if url else 'View'
            if self.demo and self._tone == 'listen':
                label = 'LISTENING PREVIEW'
            self._glyph(qp, QPointF(32, h / 2), kind, tone)
            right = w - (86 if chip else 24)
            self._text(qp, QRectF(60, h/2-19, right-60, 14), label, 9, tone, QFont.DemiBold, spacing=.8)
            self._text(qp, QRectF(60, h/2-5, right-60, 22), self._main, 14, weight=QFont.DemiBold)
            if self._dim:
                detail = 'Voice assistant preview' if self.demo and self._tone == 'listen' else self._dim
                self._text(qp, QRectF(60, h/2+15, right-60, 16), detail, 10, LABEL2)
            if chip:
                self._chip(qp, QRectF(w-76, h/2-14, 58, 28), chip, tone, '#ffffff')
        qp.restore()

    def _control(self, qp, center, symbol):
        primary = symbol in ('play', 'pause')
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor('#ffffff') if primary else QColor(255,255,255,24))
        qp.drawEllipse(center, 12, 12)
        ink = QColor('#000000') if primary else QColor('#ffffff')
        qp.setPen(QPen(ink, 1.8, Qt.SolidLine, Qt.RoundCap))
        x, y = center.x(), center.y()
        if symbol == 'pause':
            qp.drawLine(QPointF(x-2.5,y-4), QPointF(x-2.5,y+4))
            qp.drawLine(QPointF(x+2.5,y-4), QPointF(x+2.5,y+4))
        elif symbol == 'cancel':
            qp.drawLine(QPointF(x-3,y-3), QPointF(x+3,y+3))
            qp.drawLine(QPointF(x+3,y-3), QPointF(x-3,y+3))
        else:
            sign = -1 if symbol == 'prev' else 1
            path = QPainterPath(QPointF(x-sign*3,y-4))
            path.lineTo(x+sign*3,y); path.lineTo(x-sign*3,y+4); path.closeSubpath()
            qp.setBrush(ink); qp.drawPath(path)
            if symbol in ('prev','next'):
                qp.drawLine(QPointF(x+sign*5,y-4), QPointF(x+sign*5,y+4))

    def _draw_card(self, qp, w, h, mode):
        if mode == 'volume':
            self._glyph(qp, QPointF(32, h/2), 'busy', '#ffffff')
            level = self._audio.get('level', 0)
            self._text(qp, QRectF(62, 10, w-82, 22), 'Muted' if self._audio.get('mute') else f'Volume {level}%', 14, weight=QFont.DemiBold)
            qp.setPen(QPen(QColor(255,255,255,40), 6, Qt.SolidLine, Qt.RoundCap))
            qp.drawLine(QPointF(64,46),QPointF(w-24,46))
            qp.setPen(QPen(QColor('#ffffff'), 6, Qt.SolidLine, Qt.RoundCap))
            qp.drawLine(QPointF(64,46),QPointF(64+(w-88)*level/100,46))
            return
        if mode == 'job':
            job = self._job
            seconds = job['remaining'] if job['state']=='paused' else max(0, job['due']-time.time())
            minutes, seconds = divmod(int(seconds), 60)
            self._text(qp, QRectF(62,8,w-138,20), job['kind'].upper() + (' · PAUSED' if job['state']=='paused' else ''), 10, '#ff9f0a', QFont.DemiBold)
            self._text(qp, QRectF(62,27,w-138,30), f'{minutes:02}:{seconds:02}', 24, weight=QFont.DemiBold)
            self._control(qp,QPointF(w-49,34),'play' if job['state']=='paused' else 'pause')
            self._control(qp,QPointF(w-21,34),'cancel')
            return
        if not self._cover.isNull():
            path=QPainterPath(); path.addRoundedRect(QRectF(14,13,40,40),11,11)
            qp.save(); qp.setClipPath(path)
            qp.drawPixmap(QRectF(14,13,40,40),self._cover,QRectF(self._cover.rect()))
            qp.restore()
        else:
            qp.setPen(Qt.NoPen); qp.setBrush(QColor(255,255,255,26)); qp.drawRoundedRect(QRectF(14,13,40,40),11,11)
        self._text(qp,QRectF(64,9,w-156,24),self._media.get('title','Media'),13,weight=QFont.DemiBold)
        self._text(qp,QRectF(64,32,w-156,18),self._media.get('artist',''),11,LABEL2)
        for i,symbol in enumerate(('prev','pause' if self._media.get('playing') else 'play','next')):
            self._control(qp,QPointF(w-77+i*28,31),symbol)
        duration=self._media.get('duration',0)
        position=self._media.get('position',0)
        if self._media.get('playing'):
            position+=max(0,time.monotonic()-self._media.get('updated',time.monotonic()))
        qp.setPen(QPen(QColor(255,255,255,36),3,Qt.SolidLine,Qt.RoundCap))
        qp.drawLine(QPointF(64,57),QPointF(w-24,57))
        if duration:
            accent = self._album_color.lighter(260) if self._album_color is not None else QColor('#30d158')
            qp.setPen(QPen(accent,3,Qt.SolidLine,Qt.RoundCap))
            qp.drawLine(QPointF(64,57),QPointF(64+(w-88)*min(1,position/duration),57))

    def closeEvent(self, event):
        if self._backdrop:self._backdrop.close();self._backdrop=None
        self._hide_deck()
        self._timer.stop()
        self._clock.stop()
        self._frames.stop()
        if self._screen:
            try:
                self._screen.geometryChanged.disconnect(self._position)
                QGuiApplication.instance().primaryScreenChanged.disconnect(self._position)
            except (RuntimeError, TypeError):
                pass
        super().closeEvent(event)


def tray_icon():
    return QIcon(str(Path(__file__).resolve().parents[1] / 'assets/kai.ico'))


def run_island(demo=False, reduced_motion=False, media_on_demand=None):
    app = QApplication.instance() or QApplication(sys.argv)
    from storage import data_dir, settings, get_store
    lock = QLockFile(str(data_dir() / 'kai.lock'))
    if not lock.tryLock(0):
        return 0
    app.setApplicationName('Kai')
    app.setApplicationVersion(config.APP_VERSION)
    QPixmapCache.setCacheLimit(512)
    app.setQuitOnLastWindowClosed(False)
    window = Island(reduced_motion=reduced_motion or settings().get('reduced_motion',False),
                    demo=demo, interactive=not demo)
    services, panels = [], {}
    closing = threading.Event()
    busy = threading.Lock()
    media, audio = None, None
    desktop = None
    if media_on_demand is None:
        media_on_demand = bool(settings().get('media_on_demand', True))
    if not demo:
        if media_on_demand:
            from desktop_worker import DesktopServices
            desktop = DesktopServices()
            media, audio = desktop.media, desktop.audio
        else:
            from native import MediaService, AudioService
            media, audio = MediaService(), AudioService()
            services.extend([media, audio])
    clipboard = None
    shortcuts = None
    intake = None
    def show_panel(page='Transform',instant=False):
        from panel import ControlPanel
        if shortcuts: shortcuts.remember()
        panel = panels.get('panel')
        if panel is None or panel._closed:
            panel = ControlPanel(media,audio,parent=window,clipboard=clipboard,initial_page=page)
            panel.paste_requested.connect(paste_clip)
            if intake:panel.shelf_opened.connect(intake.reconcile)
            panels['panel'] = panel
            panel.destroyed.connect(lambda unused=None,p=panel:panels.pop('panel',None) if panels.get('panel') is p else None)
        window.attach_deck(panel)
        panel.open_page(page)
        if page=='Shelf' and intake:intake.reconcile()
        if instant:
            window._motion.value=window._motion.target=1;window._motion.velocity=0;window._p=1
            window._detail_motion.value=window._detail_motion.target=1;window._detail_motion.velocity=0;window._detail=1
            window._height_motion.value=window._height_motion.target;window._height_motion.velocity=0
            window._sync_input();window._sync_glass();window.update()
            window.activateWindow()
            if shortcuts:shortcuts.user.SetForegroundWindow(int(window.winId()))
        window._sync_deck()
    def paste_clip(identifier):
        if clipboard and clipboard.restore(identifier):
            window.dismiss()
            def paste():
                if not shortcuts or not shortcuts.paste():events.emit('result','Copied. Select a destination and press Ctrl+V.')
            QTimer.singleShot(80,paste)
    def background(function):
        if not busy.acquire(blocking=False):
            return
        def work():
            try:
                result = function()
                if isinstance(result,str): events.emit('result',result)
            except Exception as exc:
                events.emit('error',str(exc))
            finally:
                busy.release()
        threading.Thread(target=work,daemon=True,name='Kai action').start()
    def requested(command):
        if command=='context':
            action=window._context.copy();window._context={};window.dismiss()
            if action.get('action')=='url':
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                value=QUrl(action.get('target',''))
                if value.isValid() and value.scheme() in ('http','https') and value.host():QDesktopServices.openUrl(value)
            else:show_panel('Shelf')
        elif command in ('panel','shelf','settings','clipboard','notes'):
            show_panel({'shelf':'Shelf','settings':'Atur','clipboard':'Clipboard','notes':'Notes'}.get(command,'Transform'))
        elif command.startswith('volume:') and audio:
            audio.set_volume(int(command.split(':')[1]))
        elif command=='mute' and audio:
            audio.toggle_mute()
        elif command in ('prev','toggle','next'):
            if hasattr(media, 'command'):
                media.command(command)
            else:
                from native import transport
                background(lambda: 'Media command sent' if transport(command) else 'No active media session')
    if not demo:
        from clipboard_service import ClipboardHistory
        from capture_shelf import ShelfIntake
        from desktop_shortcuts import DesktopShortcuts
        clipboard=ClipboardHistory(app.clipboard(),get_store(),window)
        intake=ShelfIntake(get_store(),window)
        clipboard.image_received.connect(intake.image);clipboard.files_received.connect(intake.files)
        shortcuts=DesktopShortcuts(app,lambda:show_panel('Transform',instant=True))
        window._desktop_actions=shortcuts
        clipboard.message.connect(lambda text:events.emit('error',text))
        def image_added():
            panel=panels.get('panel')
            if panel is not None:panel._refresh_files()
        intake.changed.connect(image_added)
        intake.error.connect(lambda text:events.emit('error','Shelf: '+text))
        intake.offered.connect(lambda path:events.emit('context','Image ready in Shelf' if Path(path).suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp') else 'File added to Shelf',{'action':'shelf','label':'VIEW IN SHELF →'}))
        def offer_url(value):
            from urllib.parse import urlsplit
            try:valid=urlsplit(value).hostname
            except ValueError:valid=False
            if valid and len(value)<=2048 and not any(char.isspace() for char in value):events.emit('context','Link copied',{'action':'url','target':value,'label':'OPEN IN BROWSER ↗'})
        clipboard.url_copied.connect(offer_url)
        try:
            import json,os
            log=data_dir()/'logs';log.mkdir(exist_ok=True)
            (log/'session.json').write_text(json.dumps({'version':config.APP_VERSION,'pid':os.getpid(),'features':['Transform','Clipboard','Notes','Shelf','Media'],'hover_clock':True,'hotkey_available':shortcuts.available}),encoding='utf-8')
        except OSError:pass
    window.requested.connect(requested)
    bridge = Bridge(window)
    bridge.sig.connect(window.on_event, Qt.QueuedConnection)
    def receive(ev):
        bridge.sig.emit(ev.kind, ev.text, ev.data)
    events.subscribe(receive)
    from capture_shelf import ScreenshotShelf
    captures = ScreenshotShelf(get_store(),parent=window,intake=intake) if not demo else None
    downloads = ScreenshotShelf(get_store(),parent=window,intake=intake,downloads=True) if not demo else None
    if captures:
        def capture_added(count):
            panel = panels.get('panel')
            if panel is not None: panel._refresh_files()
        captures.added.connect(capture_added)
        captures.error.connect(lambda message:events.emit('error','Shelf: '+message))
        downloads.error.connect(lambda message:events.emit('error','Download: '+message))
    icon = tray_icon()
    app.setWindowIcon(icon)
    tray = QSystemTrayIcon(icon, window)
    tray.setToolTip('Kai - island preview' if demo else 'Kai - desktop mode')
    menu = QMenu()
    menu.addAction('Show Kai', window.open_island)
    if not demo:
        for page in ('Transform','Clipboard','Notes','Shelf','Media','Atur'):
            menu.addAction({'Atur':'Settings','Media':'Music'}.get(page,page), lambda checked=False, p=page: show_panel(p))
        menu.addSeparator()
    if demo:
        examples = menu.addMenu('Preview states')
        for label, kind, text in (
            ('Action result', 'result', 'Note saved'),
            ('New screenshot', 'shelf', 'Screenshot added to Shelf'),
            ('Error message', 'error', 'Device unavailable'),
        ):
            examples.addAction(label, lambda k=kind, t=text: window.on_event(k, t))
    menu.addAction('Dismiss popup', window.dismiss)
    reduced = QAction('Reduce motion', menu)
    reduced.setCheckable(True)
    reduced.setChecked(window.reduced_motion)
    def reduce_motion(enabled):
        from storage import save_settings
        window.set_reduced_motion(enabled)
        if not demo: save_settings({'reduced_motion':enabled})
    reduced.toggled.connect(reduce_motion)
    menu.addAction(reduced)
    menu.addSeparator()
    menu.addAction('Quit Kai', app.quit)
    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: window.open_island()
                           if reason == QSystemTrayIcon.Trigger else None)
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray.show()
    else:
        app.setQuitOnLastWindowClosed(True)
    def cleanup():
        closing.set()
        if captures: captures.stop()
        if downloads: downloads.stop()
        if shortcuts: shortcuts.stop()
        if clipboard: clipboard.stop()
        if intake: intake.stop()
        for service in services:
            service.stop()
        if desktop:
            desktop.stop()
        if panels.get('panel'):
            panels['panel'].close()
        events.unsubscribe(receive)
        tray.hide()
        window.close()
        lock.unlock()
    app.aboutToQuit.connect(cleanup)
    window.show()
    for service in services:
        service.start()
    return app.exec()


if __name__ == '__main__':
    sys.exit(run_island(demo=True))
