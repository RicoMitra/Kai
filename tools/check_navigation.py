"""Keep a shrinking page open under a stationary pointer, then allow normal leave."""
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch
import os

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kai'))
from PySide6.QtCore import Qt,QPoint
from PySide6.QtGui import QCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget
from island import Island
from panel import ControlPanel
from storage import Store


def main():
    app=QApplication([]);cursor=QCursor.pos();background=QWidget();background.setWindowFlag(Qt.WindowStaysOnTopHint,True)
    background.setGeometry(app.primaryScreen().geometry().adjusted(0,0,0,-200));background.show()
    island=Island(interactive=True,reduced_motion=True);island.show();island.open_island()
    try:
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'LOCALAPPDATA':directory}):
            media=SimpleNamespace(snapshot={},set_active=lambda value:None)
            panel=ControlPanel(media,store=Store(Path(directory)/'test.sqlite3'),parent=island,initial_page='Clipboard')
            island.attach_deck(panel);QTest.qWait(50)
            button=panel._nav['Media'];point=button.mapToGlobal(button.rect().center());QCursor.setPos(point)
            QTest.mouseClick(button,Qt.LeftButton);island._presence.pin_until=time.monotonic()-.1
            QTest.qWait(1100)
            assert island._deck_open,'Music collapsed after the navigation button moved away from the stationary cursor'
            assert panel.current_page()=='Media'
            QCursor.setPos(background.geometry().bottomLeft()+QPoint(30,-30));QTest.qWait(1200)
            assert not island._deck_open,'Moving away should still close the island'
        result={'music_stays_open_after_shrink':True,'intentional_pointer_leave_closes':True,'scope':'Owned island, fake media, temporary DB; no account or playback mutation'}
        output=ROOT/'artifacts/productivity/navigation-verification.json';output.parent.mkdir(exist_ok=True);output.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    finally:island.close();background.close();QCursor.setPos(cursor);app.processEvents()


if __name__=='__main__':main()
