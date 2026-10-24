"""Real Qt events, owned files/clipboard/windows. No account, download or private data."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kai'))
from PySide6.QtCore import Qt,QMimeData,QUrl,QPoint
from PySide6.QtGui import QImage,QColor,QCursor
from PySide6.QtWidgets import QApplication,QWidget,QLineEdit
from PySide6.QtTest import QTest
from storage import Store
from clipboard_service import ClipboardHistory
from capture_shelf import ShelfIntake,ScreenshotShelf
from product_pages import NotesPage,ShelfPage
from island import Island
from panel import ControlPanel
from check_productivity import FakeClipboard,wait_for


def main():
    app=QApplication([]);report={};out=ROOT/'artifacts/productivity';out.mkdir(exist_ok=True)
    user=ctypes.WinDLL('user32');user.GetForegroundWindow.restype=wintypes.HWND;prior=user.GetForegroundWindow();cursor=QCursor.pos()
    with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'LOCALAPPDATA':directory}):
        root=Path(directory);store=Store(root/'Kai/kai.sqlite3');fake=FakeClipboard();history=ClipboardHistory(fake,store);intake=ShelfIntake(store)
        history.image_received.connect(intake.image);history.files_received.connect(intake.files)
        shots=root/'Screenshots';shots.mkdir();downloads=root/'Downloads';downloads.mkdir()
        (downloads/'old.txt').write_text('old');watch=ScreenshotShelf(store,shots,intake=intake);dl=ScreenshotShelf(store,downloads,intake=intake,downloads=True)
        try:
            image=QImage(640,360,QImage.Format_RGB32);image.fill(QColor('#927bae'))
            mime=QMimeData();mime.setImageData(image);fake.setMimeData(mime);wait_for(lambda:len(store.files())==1)
            original=shots/'Screenshot original.png';image.save(str(original),'PNG',0)
            wait_for(lambda:len(store.files())==1 and store.files()[0]['path']==str(original.resolve()))
            assert store.clips()==[];assert original.exists()
            # Reverse order and different encoding: same pixels, exactly one row.
            image.fill(QColor('#9ab4a6'));second=shots/'Screenshot second.png';image.save(str(second),'PNG',100)
            wait_for(lambda:len(store.files())==2)
            mime=QMimeData();mime.setImageData(image);fake.setMimeData(mime);wait_for(lambda:intake.job is None and not intake.queue)
            assert len(store.files())==2
            urls=QMimeData();urls.setUrls([QUrl.fromLocalFile(str(second))]);fake.setMimeData(urls);QTest.qWait(400)
            assert len(store.files())==2 and not store.clips()
            report['dedupe']={'clipboard_then_folder':True,'folder_then_clipboard':True,'compression_independent':True,'original_path_preserved':True,'images_and_files_absent_from_clipboard':True}
            # Existing pre-upgrade duplicates are consolidated when Shelf is first opened.
            image.fill(QColor('#a3b08d'));oldcopy=intake.folder/'legacy.png';image.save(str(oldcopy));oldoriginal=shots/'legacy-original.png';image.save(str(oldoriginal))
            store.add_file(oldcopy,'Clipboard');store.add_file(oldoriginal,'Screenshot');intake.reconcile()
            wait_for(lambda:intake.job is None and not intake.queue);assert len(store.files())==3
            assert oldoriginal.exists() and not oldcopy.exists();report['legacy_duplicates_repaired']=True
            partial=downloads/'report.pdf.crdownload';partial.write_bytes(b'not a real pdf')
            QTest.qWait(1700);assert not any('crdownload' in row['path'] or row['path'].endswith('old.txt') for row in store.files())
            completed=downloads/'report.pdf';partial.rename(completed)
            wait_for(lambda:any(row['path']==str(completed.resolve()) for row in store.files()),6)
            report['downloads']={'partial_ignored':True,'completed_rename_added':True,'old_files_ignored':True}
            notes=NotesPage(store);notes.resize(500,215);notes.show();notes.create();identifier=notes.identifier
            notes.input.setText('Release Kai');QTest.qWait(450);identifier=notes.draft
            assert store.note(identifier)['body']=='Release Kai'
            notes.commit();notes.items.item(0).setCheckState(Qt.Checked);assert store.note(identifier)['done']
            notes.pin();store.save_note(body='Newer, unpinned');notes.refresh();assert notes.items.item(0).data(Qt.UserRole)==identifier
            notes.grab().save(str(out/'v3-notes.png'));notes.close();report['notes']={'clickable_checklist':True,'pin_first':True,'autosave':True,'simple_add_without_search_or_editor':True}
            # Reference-style list is painted natively; capture owned example data only.
            for note in store.notes():store.remove_note(note['id'])
            for body in ('Build Kai v1','BBCA analysis','MBA research','Gym\n13:00 - 14:00','Study DSP (DFT)\n10:00 - 12:00'):
                note_id=store.save_note(body=body)
                if body.startswith('Gym'):store.set_note_done(note_id,True)
            host=QWidget();host.resize(540,356);host.setStyleSheet('background:#111016;')
            panel=ControlPanel(store=store,parent=host,initial_page='Notes');panel.setGeometry(20,15,500,326);host.show();QTest.qWait(150)
            page=panel._built['Notes'];assert not hasattr(page,'search') and not hasattr(page,'editor')
            first=page.items.item(0);rectangle=page.items.visualItemRect(first)
            QTest.mouseClick(page.items.viewport(),Qt.LeftButton,pos=rectangle.topLeft()+QPoint(24,rectangle.height()//2))
            assert store.note(first.data(Qt.UserRole))['done']
            page.toggle_done();QTest.qWait(100);host.grab().save(str(out/'notes-list-reference.png'))
            panel.close();host.close();report['notes']['reference_list_and_circle']=True;report['notes']['no_subheading_search_detail_or_editor']=True
            shelf=ShelfPage(store);shelf.resize(500,215);shelf.show();QTest.qWait(650)
            index=next(i for i in range(shelf.files.count()) if shelf.files.item(i).data(Qt.UserRole)==str(original.resolve()))
            item=shelf.files.item(index);shelf.files.setCurrentItem(item);QTest.qWait(150)
            assert not shelf.preview.pixmap().isNull()
            assert item.icon().cacheKey()!=shelf.icons[2].cacheKey(),'Real screenshot thumbnail missing'
            shelf.grab().save(str(out/'v3-shelf.png'));item.setSelected(True);shelf.remove();assert original.exists();shelf.close()
            report['shelf']={'real_thumbnail':True,'inline_preview':True,'remove_keeps_original':True}
            # Context popups do not activate the island and do not replace an open page.
            receiver=QWidget();receiver.setWindowFlag(Qt.WindowStaysOnTopHint,True);receiver.resize(350,100);receiver.move(100,180);field=QLineEdit(receiver);receiver.show();receiver.activateWindow();field.setFocus();QTest.qWait(100)
            before=user.GetForegroundWindow();island=Island(reduced_motion=True,interactive=True);island._timer.stop();island.show()
            island.on_event('context','Tautan disalin',{'action':'url','target':'https://example.com','label':'BUKA DI BROWSER ↗'});QTest.qWait(150)
            assert user.GetForegroundWindow()==before and QApplication.focusWidget() is field
            assert round(island.body_rect().width())==290 and round(island.body_rect().height())==56
            emitted=[];island.requested.connect(emitted.append);QTest.mouseClick(island,Qt.LeftButton,pos=island.body_rect().center().toPoint());assert emitted==['context']
            island.grab(island.body_rect().toRect()).save(str(out/'v3-context.png'))
            island._deck_open=True;island.on_event('context','Should not interrupt',{});assert island._main=='Tautan disalin';island._deck_open=False
            island.dismiss();island.grab(island.body_rect().toRect()).save(str(out/'v3-capsule.png'));island.close();receiver.close()
            report['context']={'foreground_unchanged':True,'typing_focus_unchanged':True,'mini_290x56':True,'click_action':True,'active_page_not_interrupted':True}
        finally:
            watch.stop();dl.stop();history.stop();intake.stop();QTest.qWait(100)
    QCursor.setPos(cursor);user.SetForegroundWindow.argtypes=[wintypes.HWND]
    if prior:user.SetForegroundWindow(prior)
    (out/'shelf-v3-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
