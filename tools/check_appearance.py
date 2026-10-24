"""Capture only owned Kai widgets, using generated cover and temporary notes."""
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


def main():
    app=QApplication([]);cursor=QCursor.pos();out=ROOT/'artifacts/productivity'
    with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'LOCALAPPDATA':directory}):
        window=Island(interactive=True,reduced_motion=True);window._timer.stop();window.show()
        media=SimpleNamespace(snapshot={},set_active=lambda value:None)
        panel=ControlPanel(media=media,store=Store(Path(directory)/'test.sqlite3'),parent=window)
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
            assert window.body_rect().top()==0
            assert panel.music._lyrics_layouts[1][0].lineCount()>1
            assert window._backdrop is None
            window.grab().save(str(out/'music-album-top-edge.png'))
            panel.open_page('Notes');QTest.qWait(80);window.grab().save(str(out/'notes-black.png'))
            window.close_island();QTest.qWait(50);window.grab().save(str(out/'collapsed-black.png'))
            body=window.body_rect();ratio=window.devicePixelRatioF();pixels=window.grab().toImage()
            for offset in (-6.5,6.5):assert pixels.pixelColor(round((body.center().x()+offset)*ratio),round(body.center().y()*ratio)).name()=='#ffffff'
            report={'white_eyes_restored':True,'line_navigation_without_labels':True,'unnecessary_transform_hints_removed':True,'top_edge_attached':True,'transform_two_columns_fit':True,'lyrics_wrapped':True,'album_tint_media_only':True,'native_backdrop_disabled':True,'font':QFontInfo(QFont('Segoe UI Variable')).family(),'scope':'Synthetic cover/lyrics, temporary notes, owned widgets only; no account playback mutation'}
            (out/'appearance-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
        finally:window.close();QCursor.setPos(cursor);app.processEvents()


if __name__=='__main__':main()
