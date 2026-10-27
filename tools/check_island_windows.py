"""Native Windows hover/focus/hit-test smoke check of our own test windows.

Captures only Kai's widget, not the user's desktop or other applications.
Run from project root: python tools/check_island_windows.py
"""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'kai'))
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLineEdit, QWidget
from island import Island


def main():
    if sys.platform != 'win32':
        raise SystemExit('This check requires Windows.')
    app = QApplication([])
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.WindowFromPoint.argtypes = [wintypes.POINT]
    user32.WindowFromPoint.restype = wintypes.HWND
    user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetAncestor.restype = wintypes.HWND
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongW.restype = wintypes.LONG
    user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    saved_cursor = QCursor.pos()
    output = ROOT / 'artifacts/island'
    output.mkdir(parents=True, exist_ok=True)
    receiver = QWidget()
    receiver.setWindowFlag(Qt.WindowStaysOnTopHint,True)
    receiver.setWindowTitle('Kai verification background')
    receiver.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #713d52, stop:0.5 #344f61, stop:1 #182c30);')
    receiver.setGeometry(app.primaryScreen().geometry().adjusted(0, 0, 0, -400))
    field = QLineEdit('Kai focus verification', receiver)
    field.move(32, 80)
    receiver.show()
    receiver.activateWindow()
    field.setFocus()
    QTest.qWait(150)
    foreground_before = user32.GetForegroundWindow()
    window = Island(demo=True)
    samples = []
    window._frames.timeout.connect(lambda: samples.append(time.perf_counter()))
    try:
        QCursor.setPos(receiver.geometry().bottomLeft() + QPoint(60, -60))
        window.show()
        QTest.qWait(100)
        assert user32.GetForegroundWindow() == foreground_before, 'Overlay took foreground focus'
        assert not window._open
        assert window.grab().save(str(output / 'collapsed.png'))
        hwnd = int(window.winId())
        extended = user32.GetWindowLongW(hwnd, -20)
        assert extended & 0x20, 'Missing native WS_EX_TRANSPARENT'
        assert extended & 0x08000000, 'Missing native WS_EX_NOACTIVATE'

        QCursor.setPos(window.mapToGlobal(QPoint(window.width() // 2, 22)))
        QTest.qWait(450)
        assert window._open and window._p > 0.98, f'Real cursor did not open island: open={window._open}, p={window._p}, cursor={QCursor.pos()}, hot={window._hot_rect()}'
        assert window.grab().save(str(output / 'expanded.png'))
        assert app.primaryScreen().grabWindow(0, window.x(), window.y(), window.width(), window.height()).save(
            str(output / 'expanded-composited.png'))
        cursor = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(cursor))
        hit = user32.WindowFromPoint(cursor)
        hit_root = user32.GetAncestor(hit, 2)
        assert hit_root == int(receiver.winId()), f'Overlay intercepted hit testing: hit={hit}, root={hit_root}, receiver={int(receiver.winId())}, island={hwnd}, glass={getattr(window._backdrop,"hwnd",None)}'
        assert user32.GetForegroundWindow() == foreground_before, 'Hover took foreground focus'

        # Leave, then reenter before timeout: the collapse must be canceled.
        QCursor.setPos(receiver.geometry().bottomLeft() + QPoint(60, -60))
        QTest.qWait(400)
        assert window._open, 'Collapse happened before 700 ms'
        QCursor.setPos(window.mapToGlobal(QPoint(window.width() // 2, 22)))
        QTest.qWait(400)
        assert window._open, 'Reentry failed to cancel collapse'
        QCursor.setPos(receiver.geometry().bottomLeft() + QPoint(60, -60))
        QTest.qWait(1250)
        assert not window._open and window._p < 0.001, 'Island failed to collapse'
        assert not window._frames.isActive(), 'Idle animation timer is still running'

        # Retarget a closing animation using a real pointer move.
        QCursor.setPos(window.mapToGlobal(QPoint(window.width() // 2, 22)))
        QTest.qWait(450)
        QCursor.setPos(receiver.geometry().bottomLeft() + QPoint(60, -60))
        QTest.qWait(800)
        before_reentry = window._p
        assert 0 < before_reentry < 1, f'Expected collapse in progress: {before_reentry} open={window._open}'
        QCursor.setPos(window.mapToGlobal(QPoint(window.width() // 2, 22)))
        QTest.qWait(450)
        assert window._open and window._p > 0.98, 'Retarget failed'
        window.on_event('listening', '')
        QTest.qWait(150)
        assert window.grab().save(str(output / 'listening.png'))
        window.on_event('result', 'Timer 25 menit dimulai')
        QTest.qWait(150)
        assert window.grab().save(str(output / 'result.png'))

        # Idle CPU sample: no capture or rendering loop during measurement.
        window.dismiss()
        QCursor.setPos(receiver.geometry().bottomLeft() + QPoint(60, -60))
        QTest.qWait(600)
        cpu_start, wall_start = time.process_time(), time.perf_counter()
        QTest.qWait(2000)
        idle_cpu = 100 * (time.process_time() - cpu_start) / (time.perf_counter() - wall_start)
        gaps = [(b - a) * 1000 for a, b in zip(samples, samples[1:]) if b - a < 0.1]
        gaps.sort()
        report = {
            'platform': 'Windows native Qt', 'qt_platform': app.platformName(),
            'device_pixel_ratio': window.devicePixelRatioF(),
            'checks': ['hover opens', '700ms delay', 'reentry cancels collapse',
                       'mid-collapse retarget', 'idle animation timer stopped',
                       'foreground unchanged', 'native click-through hit testing',
                       'native transparent/noactivate styles'],
            'timer_interval_ms_p50': round(gaps[len(gaps) // 2], 2) if gaps else None,
            'timer_interval_ms_p95': round(gaps[int(len(gaps) * .95)], 2) if gaps else None,
            'idle_cpu_one_core_percent_2s': round(idle_cpu, 3),
            'limits': 'Timer intervals are not displayed frame times. CPU sample is short. DPI and monitor match current desktop only.',
        }
        (output / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report, indent=2))
    finally:
        window.close()
        receiver.close()
        QCursor.setPos(saved_cursor)
        app.processEvents()


if __name__ == '__main__':
    main()
