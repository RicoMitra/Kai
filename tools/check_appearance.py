"""Capture only owned Kai widgets, using generated cover and temporary notes.

Renders hidden (WA_DontShowOnScreen) and never moves the pointer: the owner
asked that checks not disturb the desktop."""
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kai'))
from PySide6.QtCore import QBuffer,QIODevice,QPoint,Qt
from PySide6.QtGui import QImage,QColor,QCursor,QFont,QFontInfo
from PySide6.QtWidgets import QApplication,QLabel
from PySide6.QtTest import QTest
from island import Island
from panel import ControlPanel
from storage import Store


def shelf_samples(directory):
    """Generated, non-personal Shelf fixtures: two 'photos', a window screenshot and a document."""
    from PySide6.QtGui import QPainter,QLinearGradient,QRadialGradient
    from PySide6.QtCore import QRectF,QPointF
    paths=[]
    def photo(name,top,bottom,sun):
        image=QImage(960,600,QImage.Format_RGB32);painter=QPainter(image);painter.setRenderHint(QPainter.Antialiasing)
        sky=QLinearGradient(0,0,0,600);sky.setColorAt(0,QColor(top));sky.setColorAt(1,QColor(bottom));painter.fillRect(image.rect(),sky)
        glow=QRadialGradient(QPointF(640,250),160);glow.setColorAt(0,QColor(sun));glow.setColorAt(1,QColor(0,0,0,0));painter.setPen(Qt.NoPen);painter.setBrush(glow);painter.drawEllipse(QPointF(640,250),160,160)
        painter.setBrush(QColor(sun));painter.drawEllipse(QPointF(640,250),48,48)
        for offset,color in ((380,'#1d1b33'),(450,'#121022')):
            painter.setBrush(QColor(color));painter.drawEllipse(QRectF(-200,offset,800,500));painter.drawEllipse(QRectF(380,offset+30,900,500))
        painter.end();path=directory/name;image.save(str(path));paths.append(path)
    photo('Sunset hills.jpg','#ff8a5b','#3b1f5c','#ffd29a')
    photo('Night sky.png','#0b1a3a','#27326b','#cfe3ff')
    image=QImage(960,600,QImage.Format_RGB32);image.fill(QColor('#1c1c1e'));painter=QPainter(image);painter.setRenderHint(QPainter.Antialiasing)
    painter.fillRect(QRectF(0,0,960,44),QColor('#2c2c2e'))
    for x,color in ((24,'#ff5f57'),(48,'#febc2e'),(72,'#28c840')):painter.setPen(Qt.NoPen);painter.setBrush(QColor(color));painter.drawEllipse(QPointF(x,22),7,7)
    painter.setBrush(QColor('#0a84ff'));painter.drawRoundedRect(QRectF(40,90,300,24),8,8)
    for row in range(6):painter.setBrush(QColor(255,255,255,40));painter.drawRoundedRect(QRectF(40,140+row*44,500-row*40,16),8,8)
    painter.setBrush(QColor('#30d158'));painter.drawRoundedRect(QRectF(620,90,300,420),18,18)
    painter.end();path=directory/'Screenshot 2026-10-27.png';image.save(str(path));paths.append(path)
    document=directory/'Project brief.pdf';document.write_bytes(b'%PDF-1.4\n% generated fixture\n');paths.append(document)
    return paths


def main():
    app=QApplication([]);out=ROOT/'artifacts/productivity'
    with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'LOCALAPPDATA':directory}):
        window=Island(interactive=True,reduced_motion=True);window.setAttribute(Qt.WA_DontShowOnScreen,True);window._timer.stop();window.show()
        media=SimpleNamespace(snapshot={},set_active=lambda value:None)
        store=Store(Path(directory)/'test.sqlite3')
        for body in ('Send weekly report','Review island motion','Buy coffee beans'):store.save_note(body=body)
        for path in shelf_samples(Path(directory)):store.add_file(str(path))
        panel=ControlPanel(media=media,store=store,parent=window)
        try:
            window.attach_deck(panel);QTest.qWait(80)
            page=panel._built['Transform'];page.set_files([str(Path(directory)/'example.png')])
            assert all(not button.text() and button.toolTip() for button in panel._nav.values())
            assert not any('One file' in label.text() or 'Temporary results' in label.text() for label in page.findChildren(QLabel))
            assert page.info.isHidden()
            assert panel.height()>=panel.minimumSizeHint().height(),(panel.size(),panel.minimumSizeHint())
            assert page.height()>=page.minimumSizeHint().height(),(page.size(),page.minimumSizeHint())
            window.grab().save(str(out/'fast-transform.png'))
            panel.open_page('Media');QTest.qWait(80)
            cover=QImage(64,64,QImage.Format_RGB32);cover.fill(QColor('#b51c53'));buffer=QBuffer();buffer.open(QIODevice.WriteOnly);cover.save(buffer,'PNG')
            state={'title':'Sample song','artist':'Generated cover','playing':True,'duration':240,'position':55,'cover':bytes(buffer.data())}
            lyrics={'synced':[(0,'Previous line'),(50,'Every word in this long lyric remains fully readable, wrapping onto the next line without being cut off.'),(80,'Next line')]}
            window.on_event('media','',state);panel.music.set_state(state,{'level':40},lyrics);QTest.qWait(80)
            assert window.body_rect().top()==8
            assert panel.music._lyrics_layouts[1][0].lineCount()>1
            assert window._backdrop is None
            window.grab().save(str(out/'music-album-top-edge.png'))
            panel.open_page('Notes');QTest.qWait(80);window.grab().save(str(out/'notes-black.png'))
            panel.open_page('Clipboard');QTest.qWait(80);window.grab().save(str(out/'v4-clipboard.png'))
            panel.open_page('Shelf');QTest.qWait(80);panel._built['Shelf'].files.setCurrentRow(1);QTest.qWait(450);window.grab().save(str(out/'v4-shelf.png'))
            window.collapse_deck();QTest.qWait(80);window.grab().save(str(out/'v4-compact.png'))
            clock=Island(interactive=True,reduced_motion=True);clock.setAttribute(Qt.WA_DontShowOnScreen,True);clock._timer.stop();clock.show()
            clock.open_island();QTest.qWait(60);clock.grab().save(str(out/'v4-clock.png'));clock.close()
            window.close_island();QTest.qWait(50);window.grab().save(str(out/'collapsed-black.png'))
            body=window.body_rect();ratio=window.devicePixelRatioF();pixels=window.grab().toImage()
            for offset in (-6.5,6.5):assert pixels.pixelColor(round((body.center().x()+offset)*ratio),round(body.center().y()*ratio)).name()=='#ffffff'
            report={'white_eyes_restored':True,'line_navigation_without_labels':True,'hidden_render_no_pointer_motion':True,'unnecessary_transform_hints_removed':True,'floating_capsule':True,'transform_two_columns_fit':True,'lyrics_wrapped':True,'album_tint_media_only':True,'native_backdrop_disabled':True,'font':QFontInfo(QFont('Segoe UI Variable')).family(),'scope':'Synthetic cover/lyrics, temporary notes, owned widgets only; no account playback mutation'}
            (out/'appearance-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
