"""Kai island: v2 event/hover foundation, native Qt with a stable canvas."""
import datetime as dt
import math
from pathlib import Path
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
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
TONES = {'idle': '#e0c8de', 'listen': '#e0c8de', 'busy': '#e7c999',
         'ok': '#78dfb4', 'err': '#ff9f9f'}


def lerp(a, b, t):
    return a + (b - a) * t


def body_path(rect,radius,expansion):
    top=radius*(1-max(0,min(1,expansion)));bottom=radius
    x,y,w,h=rect.x(),rect.y(),rect.width(),rect.height();path=QPainterPath(QPointF(x+top,y))
    path.lineTo(x+w-top,y);path.quadTo(x+w,y,x+w,y+top);path.lineTo(x+w,y+h-bottom);path.quadTo(x+w,y+h,x+w-bottom,y+h)
    path.lineTo(x+bottom,y+h);path.quadTo(x,y+h,x,y+h-bottom);path.lineTo(x,y+top);path.quadTo(x,y,x+top,y);path.closeSubpath();return path


class Spring:
    """Exact critically damped solution. Retargeting preserves velocity."""
    def __init__(self, value=0.0, frequency=24.0):
        self.value = self.target = value
        self.velocity = 0.0
        self.frequency = frequency

    def step(self, seconds):
        seconds = max(0.0, seconds)
        w = self.frequency
        offset = self.value - self.target
        b = self.velocity + w * offset
        decay = math.exp(-w * seconds)
        self.value = self.target + (offset + b * seconds) * decay
        self.velocity = (self.velocity - w * b * seconds) * decay
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
        self._mark = QPixmap(str(Path(__file__).resolve().parents[1] / 'assets/kai-128.png'))
        self._media, self._audio = {}, {}
        self._job = None
        self._cover, self._cover_key = QPixmap(), None
        self._album_color=None
        self._card, self._card_until = 'default', 0.0
        self._context={}
        self._motion = Spring(frequency=config.ISLAND_SPRING_FREQUENCY)
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
        p = min(1.0, max(0.0, self._p))
        compact_width=lerp(self._panel_width,min(self._panel_width,290),self._notice_motion.value)
        compact_height=lerp(config.ISLAND_EXPANDED_HEIGHT,56,self._notice_motion.value)
        expanded_width = lerp(compact_width,self._deck_width,self._detail)
        expanded_height = lerp(compact_height,self._height_motion.value,self._detail)
        width = lerp(config.ISLAND_COLLAPSED_WIDTH, expanded_width, p)
        height = lerp(config.ISLAND_COLLAPSED_HEIGHT, expanded_height, p)
        return QRectF((self.width() - width) / 2, lerp(config.ISLAND_TOP,0,p), width, height)

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
        if expanded != self._open:
            self.open_island() if expanded else self.close_island()

    def _wake_frames(self):
        if not self._frames.isActive():
            self._last_frame = time.perf_counter()
            self._frames.start()

    def _target(self, target):
        self._motion.target = target
        self._notice_motion.target=float(self._card in ('shelf','result','error','context') and not self._deck_open)
        if self.reduced_motion:
            self._motion.value, self._motion.velocity = target, 0.0
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
        self._detail = self._detail_motion.step(now - self._last_frame)
        self._height_motion.step(now - self._last_frame)
        self._notice_motion.step(now-self._last_frame)
        self._last_frame = now
        self._sync_input()
        self._sync_glass()
        self._sync_deck()
        self.update()
        if self._motion.settled and self._detail_motion.settled and self._height_motion.settled and self._notice_motion.settled:
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
        x = round((self.width()-self._deck_width)/2)+20
        self._deck.setGeometry(x,round(self.body_rect().top())+15,self._deck_width-40,round(self._height_motion.target)-30)
        self._deck.setVisible(self._detail>.96 and self._p>.96 and self._height_motion.settled)

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
            radius = lerp(config.ISLAND_COLLAPSED_HEIGHT / 2, 23, min(1, max(0, self._p)))
            path = body_path(self.body_rect(),radius,self._p)
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
        radius = lerp(config.ISLAND_COLLAPSED_HEIGHT / 2, 23, p)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setRenderHint(QPainter.SmoothPixmapTransform)
        qp.setPen(Qt.NoPen)
        for spread in range(8,0,-2):
            qp.setBrush(QColor(0,0,0,int(5*p)))
            qp.drawRoundedRect(rect.adjusted(-spread,-spread*.2,spread,spread*.6),radius+spread,radius+spread)
        qp.setBrush(Qt.black);qp.drawPath(body_path(rect,radius,p))
        color=self._album_color if (self._deck_open and self._deck is not None and self._deck.current_page()=='Media' and self._media.get('playing')) else None
        if color is not None:
            qp.save();qp.setClipPath(body_path(rect,radius,p))
            tint=QLinearGradient(rect.topLeft(),rect.bottomRight())
            tint.setColorAt(0,QColor(0,0,0));tint.setColorAt(1,color)
            qp.fillRect(rect,tint);qp.restore()
        if p>.02:
            qp.setPen(QPen(QColor(255,255,255,int(30*p)),1));qp.setBrush(Qt.NoBrush)
            qp.drawPath(body_path(rect.adjusted(.5,.5,-.5,-.5),radius,p))
        if p<.45:
            qp.save();qp.setOpacity(1-p/.45);qp.setPen(Qt.NoPen);qp.setBrush(Qt.white)
            for offset in (-6.5,6.5):
                qp.drawRoundedRect(QRectF(rect.center().x()+offset-2,rect.center().y()-5,4,10),2,2)
            qp.restore()
        alpha = min(1.0, max(0.0, (p - 0.55) / 0.4))
        alpha *= max(0,1-self._detail*2)
        if alpha:
            qp.save()
            clip = QPainterPath()
            clip.addRoundedRect(rect.adjusted(1, 1, -1, -1), radius, radius)
            qp.setClipPath(clip)
            qp.setOpacity(alpha)
            self._draw_content(qp, rect)
            qp.restore()
        qp.end()

    @staticmethod
    def _draw_spark(qp, center, size):
        glow = QRadialGradient(center, size * 3.5)
        glow.setColorAt(0, QColor('#fff2df'))
        glow.setColorAt(0.25, QColor('#d4bddb'))
        glow.setColorAt(1, QColor(194,160,208,0))
        qp.setPen(Qt.NoPen)
        qp.setBrush(glow)
        qp.drawEllipse(center, size * 3.5, size * 3.5)
        qp.setBrush(QColor('#fff2df'))
        qp.drawEllipse(center, size * 0.45, size * 0.45)

    def _text(self, qp, rect, text, size=14, color='#eef5ff', weight=QFont.Normal):
        font = QFont(FONT)
        font.setPixelSize(size)
        font.setWeight(weight)
        qp.setFont(font)
        qp.setPen(QColor(color))
        qp.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter,
                    QFontMetrics(font).elidedText(text, Qt.ElideRight, int(rect.width())))

    def _orb(self,qp,center):
        if not self._mark.isNull():
            path = QPainterPath(); path.addRoundedRect(QRectF(center.x()-19,center.y()-19,38,38),11,11)
            qp.save(); qp.setClipPath(path)
            qp.drawPixmap(QRectF(center.x()-19,center.y()-19,38,38),self._mark,QRectF(self._mark.rect()))
            qp.restore()

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
            self._text(qp,QRectF(18,9,92,29),now.strftime('%H:%M'),23,weight=QFont.Medium)
            self._text(qp,QRectF(19,37,92,18),f'{DAYS[now.weekday()]}, {now.day} {MONTHS[now.month-1]}',11,'#aaa4b2')
            qp.setPen(QPen(QColor(232,211,236,30),1));qp.drawLine(QPointF(112,17),QPointF(112,h-17))
            self._orb(qp,QPointF(141,h/2))
            self._text(qp,QRectF(174,12,w-192,24),'Kai',15,weight=QFont.DemiBold)
            self._text(qp,QRectF(174,36,w-190,19),'Ctrl+Alt+Space',9,'#aaa4b2')
        else:
            self._orb(qp, QPointF(32, h / 2))
            label = {'listen': 'KAI LISTENING', 'busy': 'KAI WORKING',
                     'ok': 'DONE', 'err': 'NEEDS ATTENTION', 'idle': 'KAI READY'}[self._tone]
            if self._card=='context':label=self._context.get('label','OPEN SHELF →')
            if self.demo and self._tone == 'listen':
                label = 'LISTENING PREVIEW'
            self._text(qp, QRectF(62, 8, w - 80, 15), label, 9, TONES[self._tone], QFont.Medium)
            self._text(qp, QRectF(62, 24, w - 80, 22), self._main, 14, weight=QFont.Medium)
            if self._dim:
                detail = 'Voice assistant preview' if self.demo and self._tone == 'listen' else self._dim
                self._text(qp, QRectF(62, 46, w - 80, 16), detail, 10, '#b5becd')
        qp.restore()

    def _control(self, qp, center, symbol):
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(238,218,242,20))
        qp.drawEllipse(center, 12, 12)
        qp.setPen(QPen(QColor('#e8f2ff'), 1.6, Qt.SolidLine, Qt.RoundCap))
        x, y = center.x(), center.y()
        if symbol == 'pause':
            qp.drawLine(QPointF(x-3,y-4), QPointF(x-3,y+4))
            qp.drawLine(QPointF(x+3,y-4), QPointF(x+3,y+4))
        elif symbol == 'cancel':
            qp.drawLine(QPointF(x-3,y-3), QPointF(x+3,y+3))
            qp.drawLine(QPointF(x+3,y-3), QPointF(x-3,y+3))
        else:
            sign = -1 if symbol == 'prev' else 1
            path = QPainterPath(QPointF(x-sign*3,y-4))
            path.lineTo(x+sign*3,y); path.lineTo(x-sign*3,y+4); path.closeSubpath()
            qp.setBrush(QColor('#e8f2ff')); qp.drawPath(path)
            if symbol in ('prev','next'):
                qp.drawLine(QPointF(x+sign*5,y-4), QPointF(x+sign*5,y+4))

    def _draw_card(self, qp, w, h, mode):
        self._orb(qp, QPointF(32, h/2))
        if mode == 'volume':
            level = self._audio.get('level', 0)
            self._text(qp, QRectF(62, 10, w-82, 22), 'Muted' if self._audio.get('mute') else f'Volume {level}%', 14)
            qp.setPen(QPen(QColor('#3a333e'), 5, Qt.SolidLine, Qt.RoundCap))
            qp.drawLine(QPointF(64,48),QPointF(w-20,48))
            qp.setPen(QPen(QColor('#dfc8e5'), 5, Qt.SolidLine, Qt.RoundCap))
            qp.drawLine(QPointF(64,48),QPointF(64+(w-84)*level/100,48))
            return
        if mode == 'job':
            job = self._job
            seconds = job['remaining'] if job['state']=='paused' else max(0, job['due']-time.time())
            minutes, seconds = divmod(int(seconds), 60)
            self._text(qp, QRectF(62,8,w-138,20), job['kind'].title() + (' · paused' if job['state']=='paused' else ''), 11, '#aaa1b0')
            self._text(qp, QRectF(62,29,w-138,29), f'{minutes:02}:{seconds:02}', 23, weight=QFont.Medium)
            self._control(qp,QPointF(w-49,34),'play' if job['state']=='paused' else 'pause')
            self._control(qp,QPointF(w-21,34),'cancel')
            return
        if not self._cover.isNull():
            path=QPainterPath(); path.addRoundedRect(QRectF(13,15,38,38),8,8)
            qp.save(); qp.setClipPath(path)
            qp.drawPixmap(QRectF(13,15,38,38),self._cover,QRectF(self._cover.rect()))
            qp.restore()
        self._text(qp,QRectF(62,9,w-156,25),self._media.get('title','Media'),13,weight=QFont.Medium)
        self._text(qp,QRectF(62,34,w-156,19),self._media.get('artist',''),10,'#aaa1b0')
        for i,symbol in enumerate(('prev','pause' if self._media.get('playing') else 'play','next')):
            self._control(qp,QPointF(w-77+i*28,31),symbol)
        duration=self._media.get('duration',0)
        position=self._media.get('position',0)
        if self._media.get('playing'):
            position+=max(0,time.monotonic()-self._media.get('updated',time.monotonic()))
        qp.setPen(QPen(QColor('#3a333e'),2,Qt.SolidLine,Qt.RoundCap))
        qp.drawLine(QPointF(64,59),QPointF(w-20,59))
        if duration:
            qp.setPen(QPen(QColor('#dfc8e5'),2,Qt.SolidLine,Qt.RoundCap))
            qp.drawLine(QPointF(64,59),QPointF(64+(w-84)*min(1,position/duration),59))

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
