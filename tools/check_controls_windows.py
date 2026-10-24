"""Verify native interactive hit testing and capture only Kai-owned widgets."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'kai'))
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget
from island import Island
from panel import ControlPanel
from storage import Store


def main():
    app = QApplication([])
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.WindowFromPoint.argtypes = [wintypes.POINT]
    user.WindowFromPoint.restype = wintypes.HWND
    user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user.GetAncestor.restype = wintypes.HWND
    saved = QCursor.pos()
    behind = QWidget()
    behind.setGeometry(app.primaryScreen().geometry().adjusted(0, 0, 0, -400))
    behind.setStyleSheet('background:#293d51')
    behind.show()
    island = Island(interactive=True)
    requests = []
    island.requested.connect(requests.append)
    output = ROOT / 'artifacts/island'
    output.mkdir(parents=True, exist_ok=True)
    try:
        QCursor.setPos(behind.geometry().bottomLeft() + QPoint(50, -50))
        island.show()
        QTest.qWait(100)
        assert not island._input_enabled
        island.open_island()
        QTest.qWait(500)
        assert island._input_enabled
        point = island.mapToGlobal(island.body_rect().center().toPoint())
        dpr = island.devicePixelRatioF()
        hit = user.GetAncestor(user.WindowFromPoint(wintypes.POINT(round(point.x()*dpr), round(point.y()*dpr))), 2)
        assert hit == int(island.winId()), 'Expanded controls must receive native mouse input'
        QTest.mouseClick(island, Qt.LeftButton, pos=island.body_rect().center().toPoint())
        assert requests == ['panel']
        island.grab().save(str(output / 'current-expanded.png'))
        island.on_event('volume', 'Volume 60%', {'level': 60, 'mute': False})
        QTest.qWait(100)
        island.grab().save(str(output / 'current-volume.png'))
        with tempfile.TemporaryDirectory() as directory:
            panel = ControlPanel(store=Store(Path(directory) / 'test.sqlite3'))
            panel.show()
            QTest.qWait(150)
            for name in ('Transform', 'Clipboard', 'Notes', 'Shelf', 'Media', 'Atur'):
                panel.open_page(name)
                QTest.qWait(30)
                assert panel.tabs.currentWidget() is panel._pages[name]
            panel.grab().save(str(output / 'current-panel.png'))
            panel.close()
            app.processEvents()
        report = {'checks': ['collapsed click-through', 'expanded native hit test', 'click opens panel', 'six productivity pages; system removed'],
                  'scope': 'Own widgets and temporary database; no microphone, model, media mutation, login or network'}
        (output / 'controls-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report, indent=2))
    finally:
        island.close()
        behind.close()
        QCursor.setPos(saved)


if __name__ == '__main__':
    main()
