import ctypes
from ctypes import wintypes
from pathlib import Path
import sys
import subprocess
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtTest import QTest

class Accent(ctypes.Structure):
    _fields_=[('state',ctypes.c_int),('flags',ctypes.c_int),('color',ctypes.c_uint32),('animation',ctypes.c_int)]
class Data(ctypes.Structure):
    _fields_=[('attribute',ctypes.c_int),('data',ctypes.c_void_p),('size',ctypes.c_size_t)]
class Pattern(QWidget):
    def paintEvent(self,event):
        p=QPainter(self)
        for i in range(self.width()//150+1):
            p.fillRect(i*150,0,150,self.height(),QColor(['#ffffff','#000000','#0064ff','#ff0064'][i%4]))
        p.end()
class Glass(QWidget):
    def paintEvent(self,event):
        p=QPainter(self)
        p.fillRect(self.rect(),QColor(10,17,26,40))
        p.end()
app=QApplication([])
out=Path('artifacts/island'); out.mkdir(parents=True,exist_ok=True)
back=Pattern(); back.setGeometry(100,200,600,240)
if '--background' in sys.argv:
    back.show(); QTest.qWait(10000); sys.exit(0)
child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--background'],creationflags=subprocess.CREATE_NO_WINDOW)
QTest.qWait(500)
glass=Glass(); glass.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool); glass.setAttribute(Qt.WA_TranslucentBackground); glass.setAttribute(Qt.WA_ShowWithoutActivating); glass.setGeometry(150,250,400,130); glass.show(); QTest.qWait(400)
screen=app.primaryScreen()
screen.grabWindow(0,150,250,400,130).save(str(out/'blur-before.png'))
func=ctypes.WinDLL('user32').SetWindowCompositionAttribute
func.argtypes=[wintypes.HWND,ctypes.POINTER(Data)]; func.restype=wintypes.BOOL
dwm=ctypes.WinDLL('dwmapi'); margins=(ctypes.c_int*4)(-1,-1,-1,-1); dwm.DwmExtendFrameIntoClientArea.argtypes=[wintypes.HWND,ctypes.c_void_p]; dwm.DwmExtendFrameIntoClientArea(int(glass.winId()),ctypes.byref(margins))
class Blur(ctypes.Structure):
    _fields_=[('flags',ctypes.c_uint),('enable',wintypes.BOOL),('region',wintypes.HRGN),('transition',wintypes.BOOL)]
b=Blur(1,True,None,False)
dwm.DwmEnableBlurBehindWindow.argtypes=[wintypes.HWND,ctypes.POINTER(Blur)]
print('enable',dwm.DwmEnableBlurBehindWindow(int(glass.winId()),ctypes.byref(b)))
accent=Accent(4,0,0x3315100C,0); data=Data(19,ctypes.addressof(accent),ctypes.sizeof(accent))
print('accent',bool(func(int(glass.winId()),ctypes.byref(data))))
dwm.DwmExtendFrameIntoClientArea(int(glass.winId()),ctypes.byref(margins))
glass.update(); QTest.qWait(600)
screen.grabWindow(0,150,250,400,130).save(str(out/'blur-enabled.png'))
glass.close(); back.close(); child.terminate(); child.wait()
