"""Bounded four-case DWM probe over a checkerboard owned by this process."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtTest import QTest


class Pattern(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        for x in range(0, self.width(), 90):
            painter.fillRect(x, 0, 45, self.height(), QColor('#fff5e8'))
            painter.fillRect(x+45, 0, 45, self.height(), QColor('#962840'))
        painter.end()


class Surface(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        painter.end()


def main():
    app = QApplication([])
    output = Path('artifacts/redesign'); output.mkdir(parents=True, exist_ok=True)
    pattern = Pattern(); pattern.setGeometry(100, 150, 650, 350); pattern.show()
    QTest.qWait(150)
    user = ctypes.WinDLL('user32'); dwm = ctypes.WinDLL('dwmapi')
    dwm.DwmSetWindowAttribute.argtypes = [wintypes.HWND, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    dwm.DwmExtendFrameIntoClientArea.argtypes = [wintypes.HWND, ctypes.c_void_p]
    class Accent(ctypes.Structure):
        _fields_ = [('state', ctypes.c_int), ('flags', ctypes.c_int), ('color', ctypes.c_uint32), ('animation', ctypes.c_int)]
    class Data(ctypes.Structure):
        _fields_ = [('attribute', ctypes.c_int), ('data', ctypes.c_void_p), ('size', ctypes.c_size_t)]
    user.SetWindowCompositionAttribute.argtypes = [wintypes.HWND, ctypes.POINTER(Data)]
    results = []
    for translucent in (True,):
        for mode in ('baseline', 'aero', 'accent'):
            surface = Surface()
            surface.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
            surface.setAttribute(Qt.WA_TranslucentBackground, translucent)
            surface.setGeometry(170, 220, 400, 160)
            surface.show(); QTest.qWait(80)
            hwnd = int(surface.winId())
            margins = (ctypes.c_int * 4)(-1, -1, -1, -1)
            if mode == 'dwm': dwm.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))
            dark = ctypes.c_int(1); kind = ctypes.c_int(3)
            dwm.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark), 4)
            if mode == 'baseline':
                result = 0
            elif mode == 'dwm':
                result = dwm.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(kind), 4)
            else:
                accent = Accent(3 if mode == 'aero' else 4, 0, 0x44101010, 0)
                data = Data(19, ctypes.addressof(accent), ctypes.sizeof(accent))
                result = user.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
            surface.update(); QTest.qWait(350)
            app.primaryScreen().grabWindow(0, 170, 220, 400, 160).save(str(output / f'glass-{mode}-{translucent}.png'))
            results.append({'translucent': translucent, 'mode': mode, 'return': result})
            surface.close(); app.processEvents()
    pattern.close()
    (output / 'glass-api.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(results)


if __name__ == '__main__': main()
