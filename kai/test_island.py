"""Checks for motion and actual Qt window behavior; no microphone or network."""
import math
import os
import time
import unittest
import subprocess
import sys
from pathlib import Path
import tempfile
from unittest.mock import patch

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

import island


APP = QApplication.instance() or QApplication([])


class CliTests(unittest.TestCase):
    def test_default_launch_has_no_voice_entry_point(self):
        import builtins
        import main
        original = builtins.__import__
        def guarded(name, *args, **kwargs):
            if name.split('.')[0] in ('stt', 'speech_worker', 'keyboard', 'sounddevice', 'faster_whisper'):
                raise AssertionError('Voice import attempted: ' + name)
            return original(name, *args, **kwargs)
        with patch.object(sys, 'argv', ['main.py']), patch.object(island, 'run_island', return_value=0) as run, patch('builtins.__import__', guarded):
            main.main()
            run.assert_called_once_with(demo=False, reduced_motion=False, media_on_demand=None)

    def test_island_modes_are_discoverable_without_loading_voice(self):
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('main.py')), '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for flag in ('--island', '--demo', '--reduced-motion'):
            self.assertIn(flag, result.stdout)


class MotionTests(unittest.TestCase):
    def spring(self):
        self.assertTrue(hasattr(island, 'Spring'), 'Missing interruptible spring')
        return island.Spring()

    def test_reversal_keeps_position_and_velocity(self):
        spring = self.spring()
        spring.target = 1.0
        spring.step(0.08)
        position, velocity = spring.value, spring.velocity
        self.assertGreater(position, 0)
        self.assertGreater(velocity, 0)
        spring.target = 0.0
        self.assertEqual((spring.value, spring.velocity), (position, velocity))
        spring.step(0.001)
        self.assertLess(abs(spring.value - position), 0.02)
        for _ in range(90):
            spring.step(1 / 120)
        self.assertAlmostEqual(spring.value, 0, places=3)

    def test_spring_stable_across_frame_rates(self):
        for fps in (30, 60, 144):
            spring = self.spring()
            spring.target = 1
            samples = [spring.step(1 / fps) for _ in range(fps)]
            self.assertTrue(all(math.isfinite(v) and 0 <= v <= 1 for v in samples))
            self.assertAlmostEqual(spring.value, 1, places=3)

    def test_underdamped_spring_overshoots_softly_and_settles(self):
        for fps in (30, 60, 144):
            spring = island.Spring(frequency=22, damping=.78)
            spring.target = 1
            samples = [spring.step(1 / fps) for _ in range(fps * 2)]
            self.assertTrue(all(math.isfinite(v) for v in samples))
            self.assertLess(max(samples), 1.06)
            self.assertGreater(max(samples), 1.0)
            self.assertTrue(spring.settled)
            self.assertEqual(spring.value, 1)

    def test_hover_delay_cancels_on_reentry_and_respects_pin(self):
        self.assertTrue(hasattr(island, 'Presence'), 'Missing hover state controller')
        state = island.Presence(delay=0.7)
        self.assertTrue(state.update(True, 10))
        self.assertTrue(state.update(False, 11))
        self.assertTrue(state.update(False, 11.6))
        self.assertTrue(state.update(True, 11.65))
        self.assertTrue(state.update(False, 12))
        self.assertFalse(state.update(False, 12.71))
        state.pin_until = 20
        self.assertTrue(state.update(False, 18))
        self.assertFalse(state.update(False, 21))


class WindowTests(unittest.TestCase):
    def test_missing_lyrics_replaces_previous_lyric_layout(self):
        from widgets import MusicCard
        from unittest.mock import patch
        import widgets
        card=MusicCard();card.resize(500,180);card.show()
        try:
            card.set_state({}, {}, {'plain':'Synthetic fixture lyrics'})
            card.grab();self.assertTrue(card._lyrics_layouts)
            for state, heading in [('unavailable','Lyrics unavailable'),('instrumental','Instrumental track'),('retry','Lyrics temporarily unavailable')]:
                with patch('widgets.text', wraps=widgets.text) as draw:
                    card.set_state({}, {}, {'status':state,'plain':'','synced':[]});card.grab()
                    self.assertIn(heading,[call.args[2] for call in draw.call_args_list])
                self.assertFalse(card._lyrics_layouts)
                self.assertFalse(card._lyrics_scroll.isVisible())
        finally:card.close()

    def test_lyrics_wrap_and_open_island_floats_as_capsule(self):
        from widgets import MusicCard
        from PySide6.QtCore import QPointF
        card=MusicCard();card.resize(500,180)
        lyrics={'synced':[(0,'Tiap detik masih merindukanmu dan kata yang panjang tetap terbaca utuh tanpa elipsis di ujung baris berikutnya'),(30,'Baris berikutnya')]}
        card.set_state({'duration':240,'position':0,'updated':time.monotonic()},{},lyrics);card.show();card.grab()
        try:
            self.assertGreater(card._lyrics_layouts[0][0].lineCount(),1)
            self.window.set_reduced_motion(True);self.window.open_island();rect=self.window.body_rect()
            # Kai 4.0: floating capsule with every corner rounded (docs/20).
            self.assertEqual(rect.top(),island.config.ISLAND_TOP)
            path=island.body_path(rect,self.window._radius(rect))
            self.assertFalse(path.contains(QPointF(rect.left()+1,rect.top()+1)))
            self.assertTrue(path.contains(rect.center()))
        finally:card.close()

    def test_black_surface_and_album_color_only_in_playing_media(self):
        from PySide6.QtCore import QBuffer,QIODevice
        from PySide6.QtGui import QImage,QColor
        from types import SimpleNamespace
        image=QImage(8,8,QImage.Format_RGB32);image.fill(QColor('#ff0000'))
        buffer=QBuffer();buffer.open(QIODevice.WriteOnly);image.save(buffer,'PNG')
        self.window.on_event('media','',{'title':'Owned sample','artist':'Test','cover':bytes(buffer.data()),'playing':True})
        self.assertGreater(self.window._album_color.red(),90)
        self.window._p=0;self.window._deck_open=False
        rect=self.window.body_rect();pixel=self.window.grab().toImage().pixelColor(round(rect.center().x()*self.window.devicePixelRatioF()),round(rect.center().y()*self.window.devicePixelRatioF()))
        self.assertEqual(pixel.name(),'#000000')
        self.window._p=1;self.window._deck_open=True;self.window._detail=1
        self.window._deck=SimpleNamespace(current_page=lambda:'Media')
        try:
            rect=self.window.body_rect();ratio=self.window.devicePixelRatioF();point=rect.bottomRight()-island.QPointF(25,12)
            pixel=self.window.grab().toImage().pixelColor(round(point.x()*ratio),round(point.y()*ratio))
            self.assertGreater(pixel.red(),pixel.blue()+30)
            self.window._media['playing']=False
            pixel=self.window.grab().toImage().pixelColor(round(point.x()*ratio),round(point.y()*ratio))
            self.assertEqual(pixel.name(),'#000000')
            self.window._sync_glass();self.assertIsNone(self.window._backdrop)
        finally:self.window._deck=None;self.window._deck_open=False

    def test_collapsed_eyes_are_white_and_navigation_uses_lines(self):
        from widgets import PageNavigation
        self.window._p=0
        rect=self.window.body_rect();ratio=self.window.devicePixelRatioF();image=self.window.grab().toImage()
        for offset in (-6.5,6.5):
            color=image.pixelColor(round((rect.center().x()+offset)*ratio),round(rect.center().y()*ratio))
            self.assertEqual(color.name(),'#ffffff')
        nav=PageNavigation();nav.resize(500,28);nav.show();APP.processEvents();selected=[];nav.selected.connect(selected.append)
        try:
            nav.select('Transform',animate=False)
            self.assertTrue(all(button.text()=='' and button.toolTip() for button in nav.buttons.values()))
            QTest.mouseClick(nav.buttons['Notes'],Qt.LeftButton)
            self.assertEqual(selected,['Notes'])
            nav.select('Notes');QTest.qWait(230)
            self.assertAlmostEqual(nav.position,2)
            self.assertEqual(nav.animation.state(),nav.animation.State.Stopped)
            nav.select('Shelf',animate=False);self.assertEqual(nav.position,3)
            nav.buttons['Shelf'].setFocus();QTest.keyClick(nav.buttons['Shelf'],Qt.Key_Left)
            self.assertEqual(selected[-1],'Notes')
        finally:nav.close()

    def test_music_seek_click_and_explicit_volume_buttons(self):
        from widgets import MusicCard
        from native import seek_position
        import datetime as dt
        from types import SimpleNamespace
        card=MusicCard();card.resize(500,180);card.set_state({'title':'Owned test','duration':240,'position':0},{'level':50},None)
        seeks=[];volumes=[];card.seek_requested.connect(seeks.append);card.volume_changed.connect(volumes.append);card.show()
        try:
            left=card.width()*.46
            for fraction in (.25,.75):QTest.mouseClick(card,Qt.LeftButton,pos=QPoint(round(3+(left-8)*fraction),91))
            self.assertAlmostEqual(seeks[0],.25,places=2);self.assertAlmostEqual(seeks[1],.75,places=2)
            QTest.mouseClick(card,Qt.LeftButton,pos=QPoint(44,card.height()-8))
            QTest.mouseClick(card,Qt.LeftButton,pos=QPoint(round(left-9),card.height()-8))
            self.assertEqual(volumes,[45,50])
            timeline=SimpleNamespace(start_time=dt.timedelta(seconds=10),end_time=dt.timedelta(seconds=250))
            self.assertEqual(seek_position(timeline,.5),1_300_000_000)
            with self.assertRaises(ValueError):seek_position(timeline,float('nan'))
        finally:card.close()

    def test_notes_simple_add_check_delete_and_autosave(self):
        from storage import Store
        from product_pages import NotesPage
        with tempfile.TemporaryDirectory() as folder:
            store=Store(Path(folder)/'notes.sqlite3')
            identifier=store.save_note(body='Study DSP (DFT)\n10:00 - 12:00')
            page=NotesPage(store);page.resize(500,230);page.show();APP.processEvents()
            try:
                self.assertFalse(hasattr(page,'search'))
                self.assertFalse(hasattr(page,'editor'))
                item=page.items.item(0);rect=page.items.visualItemRect(item)
                QTest.mouseClick(page.items.viewport(),Qt.LeftButton,pos=rect.topLeft()+QPoint(24,rect.height()//2))
                self.assertTrue(store.note(identifier)['done'])
                self.assertEqual(item.checkState(),Qt.Checked)
                QTest.mouseClick(page.items.viewport(),Qt.LeftButton,pos=rect.topLeft()+QPoint(24,rect.height()//2))
                self.assertFalse(store.note(identifier)['done'])
                page.pin();self.assertTrue(store.note(identifier)['pinned'])
                page.create();page.input.setText('Review UI');page.commit()
                self.assertEqual(store.notes()[0]['id'],identifier)
                created=store.notes('Review UI')[0]['id'];page.identifier=created;page.remove()
                self.assertIsNone(store.note(created))
                rect=page.items.visualItemRect(page.items.item(0))
                QTest.mouseClick(page.items.viewport(),Qt.LeftButton,pos=QPoint(rect.right()-24,rect.center().y()))
                self.assertIsNone(store.note(identifier))
            finally:page.close();APP.processEvents()

    def setUp(self):
        self.window = island.Island()
        self.window._timer.stop()  # Cursor polling is tested in the Windows smoke test.
        self.window.show()
        APP.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        APP.processEvents()

    def test_native_window_does_not_resize_during_morph(self):
        before = self.window.geometry()
        self.window.open_island()
        QTest.qWait(120)
        self.assertEqual(self.window.geometry(), before)
        self.window.close_island()
        QTest.qWait(500)
        self.assertEqual(self.window.geometry(), before)

    def test_compact_expanded_size(self):
        self.window.set_reduced_motion(True)
        self.window.open_island()
        self.assertLessEqual(self.window.body_rect().width(), 320)
        self.assertLessEqual(self.window.body_rect().height(), 68)

    def test_event_opens_without_waiting_for_cursor_poll(self):
        self.window.on_event('listening', 'Mendengarkan...')
        self.assertTrue(self.window._open)
        QTest.qWait(420)
        self.assertGreater(self.window._p, 0.95)
        self.assertEqual(self.window._tone, 'listen')
        self.window.on_event('result', 'Gagal: perangkat tidak tersedia')
        self.assertEqual(self.window._tone, 'err')

    def test_overlay_does_not_take_focus_or_mouse_input(self):
        self.assertTrue(self.window.windowFlags() & Qt.WindowDoesNotAcceptFocus)
        self.assertTrue(self.window.windowFlags() & Qt.WindowTransparentForInput)
        self.assertTrue(self.window.testAttribute(Qt.WA_ShowWithoutActivating))

    def test_expanded_interactive_card_opens_panel_on_click(self):
        window = island.Island(interactive=True, reduced_motion=True)
        window._timer.stop()
        requested = []
        window.requested.connect(requested.append)
        window.show()
        window.open_island()
        QTest.mouseClick(window, Qt.LeftButton, pos=window.body_rect().center().toPoint())
        self.assertIn('panel', requested)
        window.close()

    def test_management_panel_builds_without_network_or_model(self):
        from storage import Store
        from panel import ControlPanel
        with tempfile.TemporaryDirectory() as folder:
            panel = ControlPanel(store=Store(Path(folder) / 'test.sqlite3'),initial_page='Clipboard')
            self.assertEqual(panel.tabs.count(), 6)
            self.assertNotIn('Sistem',panel._pages)
            self.assertEqual(panel._tasks, {})
            self.assertEqual(panel._built['Clipboard'].filter.itemText(0),'All')
            panel.open_page('Notes')
            from PySide6.QtWidgets import QPushButton
            notes=panel._built['Notes'];self.assertEqual(notes.input.placeholderText(),'New note — press Enter')
            self.assertIn('New note',[action[0] for action in notes.menu_actions() if action])
            panel.open_page('Atur');self.assertEqual(panel.heading.text(),'Settings')
            panel.close()

    def test_removed_command_is_blocked_and_notes_flush_on_close(self):
        from storage import Store
        from panel import ControlPanel
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'LOCALAPPDATA': folder}):
            store = Store(Path(folder) / 'Kai/kai.sqlite3')
            panel = ControlPanel(store=store,initial_page='Clipboard')
            try:
                panel.command('timer 5 menit')
                self.assertEqual(panel._tasks, {}, panel.status.text())
                self.assertEqual(len(store.jobs()), 0, panel.status.text())
                self.assertIn('removed', panel.status.text())
                panel.command('status sistem')
                self.assertEqual(panel._tasks,{})
                panel.open_page('Notes')
                notes=panel._built['Notes'];notes.create()
                notes.input.setText('Save before debounce')
                panel.close()
                self.assertEqual(store.notes('Save before debounce')[0]['preview'],'Save before debounce')
            finally:
                panel.close()
                APP.processEvents()


if __name__ == '__main__':
    unittest.main(verbosity=2)
