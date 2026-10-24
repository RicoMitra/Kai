"""Test a compositor backdrop over this tool's own colored stripes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'kai'))
from glass import Backdrop
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter,QColor
from PySide6.QtTest import QTest

class Pattern(QWidget):
    def paintEvent(self,event):
        p=QPainter(self)
        for x in range(0,self.width(),90):
            p.fillRect(x,0,45,self.height(),QColor('#fff5e8'));p.fillRect(x+45,0,45,self.height(),QColor('#962840'))
        p.end()

def main():
    app=QApplication([])
    pattern=Pattern();pattern.setGeometry(100,150,650,350);pattern.show()
    overlay=QWidget();overlay.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool|Qt.WindowStaysOnTopHint)
    overlay.setAttribute(Qt.WA_TranslucentBackground);overlay.setGeometry(170,220,400,160);overlay.show()
    QTest.qWait(150)
    baseline=app.primaryScreen().grabWindow(0,170,220,400,160).toImage()
    dpr=overlay.devicePixelRatioF()
    glass=None
    try:
        glass=Backdrop(int(overlay.winId()),round(170*dpr),round(220*dpr),round(400*dpr),round(160*dpr),test_color='--color' in sys.argv)
        glass.clip(0,0,round(400*dpr),round(160*dpr),24)
        QTest.qWait(650)
        captured=app.primaryScreen().grabWindow(0,170,220,400,160)
        captured.save('artifacts/redesign/host-glass.png')
        if '--color' not in sys.argv:
            import json
            from pathlib import Path
            def edge(image):
                values=[image.pixelColor(x,image.height()//2).red() for x in range(30,image.width()-30)]
                return max(abs(a-b) for a,b in zip(values,values[1:])),max(values)-min(values)
            sharp,_=edge(baseline);soft,contrast=edge(captured.toImage())
            assert sharp>40 and soft<sharp/2 and contrast>30,(sharp,soft,contrast)
            Path('artifacts/redesign/glass-verification.json').write_text(json.dumps({'native_compositor':True,'baseline_edge':sharp,'blurred_edge':soft,'retained_contrast':contrast,'scope':'Owned cream/maroon test pattern; no desktop capture used by production blur.'},indent=2),encoding='utf-8')
        print('Host backdrop created and captured; queue HRESULT:',glass.queue_result)
    finally:
        if glass:glass.close()
        overlay.close();pattern.close()

if __name__=='__main__':main()
