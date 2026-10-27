"""Small painted island controls: no browser, timers or media libraries."""
from pathlib import Path
import math
import time
from PySide6.QtCore import QPointF, QRectF, Qt, Signal, QBuffer, QByteArray, QIODevice, QSize,QVariantAnimation,QEasingCurve,QEvent
from PySide6.QtGui import QColor, QFont, QFontMetrics, QImageReader, QPainter, QPainterPath, QPen, QPixmap,QTextLayout,QTextOption
from PySide6.QtWidgets import QWidget,QScrollBar,QPushButton
import config

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


class PageNavigation(QWidget):
    """Five accessible hit areas and one painted, interruptible accent indicator.

    Kai 4.0: the marker takes the page accent, blends colour while travelling and
    stretches mid-flight like an iOS page control."""
    selected=Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent);self.setFixedHeight(28);self.position=0.;self.buttons={};self.current='Transform'
        self.animation=QVariantAnimation(self);self.animation.setDuration(200);curve=QEasingCurve(QEasingCurve.OutBack);curve.setOvershoot(1.1);self.animation.setEasingCurve(curve)
        self.animation.valueChanged.connect(self._position_changed)
        for name,label in [('Transform','Fast Transform'),('Clipboard','Clipboard'),('Notes','Notes'),('Shelf','Shelf'),('Media','Music')]:
            button=QPushButton('',self);button.setToolTip(label);button.setAccessibleName(label);button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet('QPushButton {background:transparent;border:0;padding:0;} QPushButton:hover {background:rgba(255,255,255,10);border-radius:12px;} QPushButton:focus {background:rgba(255,255,255,12);border-radius:12px;}')
            button.clicked.connect(lambda checked=False,key=name:self.selected.emit(key));button.installEventFilter(self);self.buttons[name]=button

    def _position_changed(self,value):self.position=float(value);self.update()

    def select(self,name,animate=True):
        if name not in self.buttons:return
        target=list(self.buttons).index(name);self.current=name;self.animation.stop()
        for key,button in self.buttons.items():button.setAccessibleDescription('Current page' if key==name else '')
        if animate and self.isVisible() and abs(self.position-target)>.001:
            self.animation.setStartValue(self.position);self.animation.setEndValue(float(target));self.animation.start()
        else:self._position_changed(target)

    def resizeEvent(self,event):
        width=min(300,self.width());left=(self.width()-width)/2
        for index,button in enumerate(self.buttons.values()):button.setGeometry(round(left+index*width/5),0,round(width/5),self.height())
        super().resizeEvent(event)

    def eventFilter(self,watched,event):
        if event.type()==QEvent.KeyPress and event.key() in (Qt.Key_Left,Qt.Key_Right):
            values=list(self.buttons.values());index=values.index(watched);target=max(0,min(len(values)-1,index+(-1 if event.key()==Qt.Key_Left else 1)))
            values[target].setFocus();values[target].click();return True
        return super().eventFilter(watched,event)

    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing);painter.setPen(Qt.NoPen)
        width=min(300,self.width());left=(self.width()-width)/2;step=width/5;y=self.height()/2
        names=list(self.buttons);position=max(0.,min(len(names)-1.,self.position))
        lower=min(len(names)-1,int(math.floor(position)));upper=min(len(names)-1,lower+1);fraction=position-lower
        painter.setBrush(QColor(255,255,255,48))
        for index in range(5):painter.drawEllipse(QPointF(left+(index+.5)*step,y),2.6,2.6)
        a,b=QColor(config.ACCENTS[names[lower]]),QColor(config.ACCENTS[names[upper]])
        color=QColor.fromRgbF(*(x+(y_-x)*fraction for x,y_ in zip(a.getRgbF()[:3],b.getRgbF()[:3])))
        stretch=1-abs(fraction-.5)*2 if 0<fraction<1 else 0.
        marker=26+30*stretch
        painter.setBrush(color);painter.drawRoundedRect(QRectF(left+(self.position+.5)*step-marker/2,y-3,marker,6),3,3)


def text(painter, rect, value, size=12, color='#f5f3f0', weight=QFont.Normal):
    font = QFont('Segoe UI Variable'); font.setPixelSize(size); font.setWeight(weight)
    painter.setFont(font); painter.setPen(QColor(color))
    painter.drawText(rect, Qt.AlignVCenter | Qt.AlignLeft,
                     QFontMetrics(font).elidedText(str(value), Qt.ElideRight, int(rect.width())))


def symbol(painter, center, kind, size=5, color='#ffffff'):
    x, y = center.x(), center.y()
    painter.setPen(QPen(QColor(color), 1.8, Qt.SolidLine, Qt.RoundCap))
    if kind == 'pause':
        painter.drawLine(QPointF(x-3,y-size), QPointF(x-3,y+size))
        painter.drawLine(QPointF(x+3,y-size), QPointF(x+3,y+size))
    else:
        sign = -1 if kind == 'prev' else 1
        path = QPainterPath(QPointF(x-sign*size*.65,y-size))
        path.lineTo(x+sign*size*.8,y); path.lineTo(x-sign*size*.65,y+size); path.closeSubpath()
        painter.setBrush(QColor(color)); painter.drawPath(path)
        if kind in ('prev','next'):
            painter.drawLine(QPointF(x+sign*(size+2),y-size), QPointF(x+sign*(size+2),y+size))


def small_image(data, size=72):
    buffer = QBuffer(); buffer.setData(QByteArray(data)); buffer.open(QIODevice.ReadOnly)
    reader = QImageReader(buffer); reader.setScaledSize(QSize(size, size)); reader.setAllocationLimit(32)
    return QPixmap.fromImage(reader.read())


class MusicCard(QWidget):
    transport = Signal(str)
    lyrics_requested = Signal()
    volume_changed = Signal(int)
    mute_requested = Signal()
    seek_requested = Signal(float)

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(166)
        self.setMouseTracking(True)
        self.data, self.audio, self.lyrics = {}, {}, None
        self.cover = QPixmap()  # Logo stays on the app icon only; empty art is a quiet tile.
        self.accent = QColor(config.ACCENTS['Media'])
        self.key = None
        self._drag_volume=False
        self._lyrics_key=None;self._lyrics_layouts=[];self._lyrics_scroll=QScrollBar(Qt.Vertical,self);self._lyrics_scroll.hide();self._lyrics_scroll.valueChanged.connect(self.update)
        self.setToolTip('Click progress to seek · −/+ volume 5% · VOL to mute')

    def set_state(self, data, audio, lyrics):
        key = (data.get('title'), data.get('artist'))
        if key != self.key:
            self.key = key
            self.cover = small_image(data['cover']) if data.get('cover') else QPixmap()
            self.accent = QColor(config.ACCENTS['Media'])
            if data.get('cover') and not self.cover.isNull():
                # One averaged pixel, brightened: progress takes the album's colour.
                average = self.cover.toImage().scaled(1, 1, Qt.IgnoreAspectRatio, Qt.SmoothTransformation).pixelColor(0, 0)
                hue, saturation, _, _ = average.getHsv()
                if saturation > 40: self.accent = QColor.fromHsv(max(0, hue), max(150, saturation), 245)
        self.data, self.audio, self.lyrics = data, audio, lyrics
        self.update()

    @staticmethod
    def stamp(seconds):
        minutes, seconds = divmod(max(0, int(seconds)), 60)
        return f'{minutes:02}:{seconds:02}'

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        width, height = self.width(), self.height()
        left = int(width * .46); right = left + 25
        clip = QPainterPath(); clip.addRoundedRect(QRectF(0,7,62,62),15,15)
        p.save(); p.setClipPath(clip)
        if not self.cover.isNull(): p.drawPixmap(QRectF(0,7,62,62), self.cover, QRectF(self.cover.rect()))
        else:
            p.fillRect(QRectF(0,7,62,62),QColor(255,255,255,26))
            symbol(p,QPointF(31,38),'play',7,'#6e6e73')
        p.restore()
        text(p,QRectF(75,9,left-80,25),self.data.get('title') or 'Music for your day',15,weight=QFont.DemiBold)
        text(p,QRectF(75,35,left-80,19),self.data.get('artist') or 'Play a song in Spotify',12,'#9b9ba1')
        text(p,QRectF(75,54,left-80,16),('NOW PLAYING' if self.data.get('playing') else 'PAUSED') if self.data else 'KAI',9,self.accent.name() if self.data.get('playing') else '#6e6e73',QFont.DemiBold)
        duration = self.data.get('duration',0)
        position = self.data.get('position',0)
        if self.data.get('playing'): position += max(0,time.monotonic()-self.data.get('updated',time.monotonic()))
        position = min(position,duration) if duration else 0
        y = 91
        p.setPen(QPen(QColor(255,255,255,40),5,Qt.SolidLine,Qt.RoundCap)); p.drawLine(QPointF(3,y),QPointF(left-5,y))
        if duration:
            p.setPen(QPen(self.accent,5,Qt.SolidLine,Qt.RoundCap)); p.drawLine(QPointF(3,y),QPointF(3+(left-8)*position/duration,y))
        text(p,QRectF(0,98,70,16),self.stamp(position),10,'#9b9ba1')
        text(p,QRectF(left-48,98,48,16),'-'+self.stamp(duration-position),10,'#9b9ba1')
        center_y = 130
        for x, kind in ((left*.22,'prev'),(left*.5,'pause' if self.data.get('playing') else 'play'),(left*.78,'next')):
            primary = kind in ('play','pause')
            if primary:
                p.setPen(Qt.NoPen); p.setBrush(QColor('#ffffff')); p.drawEllipse(QPointF(x,center_y),19,19)
            symbol(p,QPointF(x,center_y),kind,6 if primary else 5,'#000000' if primary else '#ffffff')
        p.setPen(QPen(QColor(255,255,255,22),1)); p.drawLine(QPointF(left+12,12),QPointF(left+12,height-14))
        if self.lyrics and (self.lyrics.get('synced') or self.lyrics.get('plain')):
            synced = self.lyrics.get('synced',[])
            if synced:
                index = max(0,next((i-1 for i,row in enumerate(synced) if row[0]>position),len(synced)-1))
                values = [(synced[i][1], i==index) for i in range(max(0,index-1),min(len(synced),index+2))]
            else:values=[(self.lyrics.get('plain',''),True)]
            self.draw_lyrics(p,values,QRectF(right,12,width-right-12,height-47))
            text(p,QRectF(right,height-26,width-right,18),'LRCLIB  ·  '+('Synced lyrics' if synced else 'Plain lyrics'),9,'#6e6e73')
        else:
            self._lyrics_scroll.hide();self._lyrics_layouts=[];self._lyrics_key=None
            state = (self.lyrics or {}).get('status')
            title, detail = {
                'unavailable': ('Lyrics unavailable', 'No matching lyrics in LRCLIB.'),
                'instrumental': ('Instrumental track', 'No sung lyrics for this track.'),
                'retry': ('Lyrics temporarily unavailable', 'Try again in a minute.'),
            }.get(state, ('Every song, a story.', 'Lyrics will appear here.'))
            text(p,QRectF(right,31,width-right,25),title,15,weight=QFont.DemiBold)
            text(p,QRectF(right,62,width-right,22),detail,11,'#9b9ba1')
            action = 'Check later  ↗' if state == 'unavailable' else 'Retry lyrics  ↗' if state == 'retry' else '' if state == 'instrumental' else 'Load lyrics  ↗'
            text(p,QRectF(right,105,width-right,28),action,12,self.accent.name(),QFont.DemiBold)
        # A quiet volume rail; native audio lives only while this page is open.
        if height >= 166:
            rail_y = height-8
            text(p,QRectF(0,rail_y-9,40,18),'VOL',8,'#9b9ba1',QFont.DemiBold)
            for x,label in ((44,'−'),(left-9,'+')):
                p.setPen(Qt.NoPen);p.setBrush(QColor(255,255,255,26));p.drawEllipse(QPointF(x,rail_y),10,10)
                text(p,QRectF(x-4,rail_y-10,15,20),label,13)
            p.setPen(QPen(QColor(255,255,255,40),4,Qt.SolidLine,Qt.RoundCap)); p.drawLine(QPointF(64,rail_y),QPointF(left-33,rail_y))
            p.setPen(QPen(QColor('#ffffff'),4,Qt.SolidLine,Qt.RoundCap)); p.drawLine(QPointF(64,rail_y),QPointF(64+(left-97)*self.audio.get('level',0)/100,rail_y))
        p.end()

    def draw_lyrics(self,painter,values,viewport):
        key=(tuple(values),round(viewport.width()))
        if key!=self._lyrics_key:
            self._lyrics_key=key;self._lyrics_layouts=[];total=0;active_start=0;active_height=0
            option=QTextOption();option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            for value,active in values:
                font=QFont('Segoe UI Variable');font.setPixelSize(16 if active else 12);font.setWeight(QFont.Bold if active else QFont.Medium)
                layout=QTextLayout(value,font);layout.setTextOption(option);layout.beginLayout();height=0
                while True:
                    line=layout.createLine()
                    if not line.isValid():break
                    line.setLineWidth(max(1,viewport.width()));line.setPosition(QPointF(0,height));height+=line.height()+2
                layout.endLayout();self._lyrics_layouts.append((layout,height,active))
                if active:active_start=total;active_height=height
                total+=height+10
            self._lyrics_scroll.setRange(0,max(0,round(total-10-viewport.height())));self._lyrics_scroll.setPageStep(max(1,round(viewport.height())))
            self._lyrics_scroll.setValue(max(0,round(active_start-max(0,(viewport.height()-active_height)/2))))
        self._lyrics_scroll.setGeometry(self.width()-6,round(viewport.y()),5,round(viewport.height()));self._lyrics_scroll.setVisible(self._lyrics_scroll.maximum()>0)
        painter.save();painter.setClipRect(viewport);y=viewport.y()-self._lyrics_scroll.value()
        for layout,height,active in self._lyrics_layouts:
            painter.setPen(QColor('#ffffff' if active else '#6e6e73'));layout.draw(painter,QPointF(viewport.x(),y));y+=height+10
        painter.restore()

    def wheelEvent(self,event):
        if event.position().x()>self.width()*.46 and self._lyrics_scroll.maximum()>0:
            self._lyrics_scroll.setValue(self._lyrics_scroll.value()-round(event.angleDelta().y()/120*32));event.accept()
        else:super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button()!=Qt.LeftButton:return
        x,y = event.position().x(),event.position().y()
        left = self.width()*.46
        if x > left+20:
            self.lyrics_requested.emit()
        elif self.height()>=166 and y>self.height()-20:
            if x<30: self.mute_requested.emit()
            elif x<56:self._change_volume(max(0,self.audio.get('level',0)-5))
            elif x>left-22:self._change_volume(min(100,self.audio.get('level',0)+5))
            else:self._drag_volume=True;self._change_volume(round(max(0,min(1,(x-64)/max(1,left-97)))*100))
        elif 79<=y<=103 and 0<=x<=left and self.data.get('duration',0)>0:
            self.seek_requested.emit(max(0,min(1,(x-3)/max(1,left-8))))
        elif y>116:
            self.transport.emit('prev' if x<left*.35 else 'next' if x>left*.65 else 'toggle')

    def mouseMoveEvent(self,event):
        if self._drag_volume and event.buttons() & Qt.LeftButton:
            left=self.width()*.46;self._change_volume(round(max(0,min(1,(event.position().x()-64)/max(1,left-97)))*100))

    def _change_volume(self,value):
        self.audio={**self.audio,'level':value};self.update();self.volume_changed.emit(value)

    def mouseReleaseEvent(self,event):self._drag_volume=False
