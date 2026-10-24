"""Native integration checks using owned windows, fake clipboard and temporary data."""
import ctypes as c
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kai'))
from PySide6.QtCore import QObject,Signal,QMimeData,QUrl,Qt,QEvent
from PySide6.QtGui import QImage,QColor,QCursor
from PySide6.QtWidgets import QApplication,QWidget,QLineEdit
from PySide6.QtTest import QTest
from storage import Store
from clipboard_service import ClipboardHistory
from capture_shelf import ScreenshotShelf,ShelfIntake
from desktop_shortcuts import DesktopShortcuts
from panel import ControlPanel
from island import Island


class FakeClipboard(QObject):
    dataChanged=Signal()
    def __init__(self):super().__init__();self.value=QMimeData(self)
    def mimeData(self):return self.value
    def setMimeData(self,value):
        old=self.value;self.value=value;value.setParent(self);old.deleteLater();self.dataChanged.emit()
    def text(self,value):
        mime=QMimeData();mime.setText(value);self.setMimeData(mime)


def wait_for(predicate,seconds=5):
    deadline=time.monotonic()+seconds
    while not predicate() and time.monotonic()<deadline:QTest.qWait(30)
    assert predicate(),'Timed out'


def main():
    app=QApplication([]);output=ROOT/'artifacts/productivity';output.mkdir(parents=True,exist_ok=True);report={}
    user=c.WinDLL('user32');user.GetForegroundWindow.restype=w.HWND
    previous=user.GetForegroundWindow();shortcuts=None
    with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'LOCALAPPDATA':directory}):
        store=Store(Path(directory)/'Kai/kai.sqlite3');fake=FakeClipboard();history=ClipboardHistory(fake,store);intake=ShelfIntake(store)
        history.image_received.connect(intake.image);history.files_received.connect(intake.files)
        fake.text('https://example.com/kai');QTest.qWait(160)
        fake.text('def hello():\n    return "Kai"');QTest.qWait(160)
        fake.text('Bawa ide kecil ini ke proyek berikutnya.');QTest.qWait(160)
        assert {row['kind'] for row in store.clips()}=={'text','link','code'}
        identifier=store.clips()[0]['id'];assert history.restore(identifier);QTest.qWait(120);assert len(store.clips())==3
        history.set_enabled(False);fake.text('Should not be recorded');QTest.qWait(140);assert len(store.clips())==3
        history.set_enabled(True)
        excluded=QMimeData();excluded.setText('not a real password');excluded.setData('application/x-kde-passwordManagerHint',b'secret');history.capture(excluded);assert len(store.clips())==3
        image=QImage(720,420,QImage.Format_RGB32);image.fill(QColor('#c2b0ce'));mime=QMimeData();mime.setImageData(image);fake.setMimeData(mime)
        wait_for(lambda:len(store.files())==1)
        assert len(store.clips())==3 and all(row['kind']!='image' for row in store.clips())
        image_path=store.files()[0]['path'];assert Path(image_path).is_file()
        screenshot_folder=Path(directory)/'Screenshots';screenshot_folder.mkdir();watch=ScreenshotShelf(store,screenshot_folder,intake=intake)
        for index,color in enumerate(('#bfa9d2','#c3cbb4','#c4a5ad','#aaaec8','#d4be9b')):
            image.fill(QColor(color));image.save(str(screenshot_folder/f'Screenshot {index+1}.png'))
        wait_for(lambda:len(store.files())==6)
        store.remove_file(image_path);assert Path(image_path).exists()
        report['clipboard']={'text_link_only':True,'code_as_text':True,'restored_without_duplicate':True,'pause':True,'password_hint_excluded':True,'images_only_in_shelf':True}
        report['screenshots']={'five_native_folder_events':True,'originals_kept':True}
        background=QWidget();background.setGeometry(app.primaryScreen().geometry().adjusted(0,0,0,-250));background.setStyleSheet('background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #50505e,stop:.5 #8b7a86,stop:1 #3e414c);');background.show()
        island=Island(reduced_motion=True,interactive=True);island._timer.stop();island.show();island.open_island()
        island.grab(island.body_rect().toRect()).save(str(output/'hover-clock.png'))
        media=SimpleNamespace(snapshot={},set_active=lambda active:None,command=lambda name:None)
        audio=SimpleNamespace(snapshot={'level':48,'mute':False},set_volume=lambda value:None,toggle_mute=lambda:None)
        with patch('panel.settings',return_value={}):panel=ControlPanel(media,audio,store,parent=island,clipboard=history,initial_page='Shelf')
        island.attach_deck(panel);QTest.qWait(400)
        assert not panel.isWindow() and panel.tabs.count()==6
        assert not any(name in panel._pages for name in ('Timer','Fokus','Jadwal','Cuaca','Sistem'))
        for index in range(panel.files.count()):panel.files.item(index).setSelected(True)
        assert len(panel.files.mimeData(panel.files.selectedItems()).urls())==5
        report['shelf']={'five_file_drag_payload':True,'six_embedded_pages':True,'legacy_and_system_pages_removed':True}
        for name in ('Shelf','Clipboard','Notes','Transform','Media','Atur'):
            panel.open_page(name)
            if name=='Notes':
                notes=panel._built['Notes'];notes.create();notes.input.setText('Kai, ruang kecil untuk ide.')
                QTest.qWait(450);note_id=notes.draft;assert store.note(note_id)['body'].startswith('Kai, ruang')
            if name=='Media':
                media.snapshot={'title':'Paper Sky','artist':'Lumen Coast · ilustrasi pengujian','duration':240,'position':68,'playing':True};panel._refresh()
            island._sync_deck();QTest.qWait(400)
            rectangle=island.geometry();app.primaryScreen().grabWindow(0,rectangle.x(),rectangle.y(),rectangle.width(),rectangle.height()).save(str(output/f'{name.lower()}.png'))
        panel.open_page('Notes');notes.input.setText('Simpan juga sebelum debounce ketika island ditutup.');island.collapse_deck();app.processEvents()
        assert store.note(note_id)['body']=='Simpan juga sebelum debounce ketika island ditutup.'
        report['notes']={'autosave':True,'flush_on_close':True}
        island.on_event('shelf','5 screenshot masuk Shelf');assert round(island.body_rect().height())==56
        island.grab().save(str(output/'adaptive-toast.png'));report['adaptive_toast']={'width':round(island.body_rect().width()),'height':round(island.body_rect().height())}
        island.close();background.close();watch.stop();history.stop();intake.stop()
        # Register/release the actual native hotkey; deliver only a test message.
        called=[];shortcuts=DesktopShortcuts(app,lambda:called.append(True))
        if shortcuts.available:
            kernel=c.WinDLL('kernel32');user.PostThreadMessageW(kernel.GetCurrentThreadId(),0x312,0x4B41,0);QTest.qWait(100)
            assert called==[True];report['native_hotkey']='registered and dispatched'
        else:report['native_hotkey']='unavailable (another instance may own it)'
        class PasteReceiver(QObject):
            def __init__(self):super().__init__();self.count=0
            def eventFilter(self,watched,event):
                if event.type()==QEvent.KeyPress and event.key()==Qt.Key_V and event.modifiers()&Qt.ControlModifier:
                    self.count+=1;return True  # Never read the real system clipboard.
                return False
        receiver=QWidget();field=QLineEdit(receiver);receiver.setGeometry(100,150,340,80);receiver.show();receiver.activateWindow();field.setFocus()
        intercepted=PasteReceiver();field.installEventFilter(intercepted);QTest.qWait(100)
        cursor=QCursor.pos();QCursor.setPos(field.mapToGlobal(field.rect().center()))
        user.mouse_event(2,0,0,0,0);user.mouse_event(4,0,0,0,0);QTest.qWait(100)
        shortcuts.target=int(receiver.winId());sent=shortcuts.paste();QTest.qWait(100)
        QCursor.setPos(cursor)
        assert sent and intercepted.count==1,(sent,intercepted.count)
        report['native_paste']='Ctrl+V delivered once to owned test target; system clipboard untouched'
        receiver.close()
        shortcuts.stop()
    user.SetForegroundWindow.argtypes=[w.HWND]
    if previous:user.SetForegroundWindow(previous)
    (output/'productivity-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
