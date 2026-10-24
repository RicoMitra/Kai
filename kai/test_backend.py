"""Small regression suite for persistent state and process-owned speech memory."""
import importlib.util
import multiprocessing
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace


def recognize_example(audio, options):
    return {'text': 'timer 5 menit', 'lang': 'id', 'size': 'test', 'device': 'cpu'}


def recognize_slow(audio, options):
    time.sleep(10)


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp.cleanup()

    def store(self):
        self.assertIsNotNone(importlib.util.find_spec('storage'), 'Persistent store missing')
        from storage import Store
        return Store(Path(self.temp.name) / 'kai.sqlite3')

    def test_timers_survive_reopen_and_fire_once(self):
        store = self.store()
        item = store.add_job('timer', 60, 'Minum', now=100)
        reopened = type(store)(store.path)
        self.assertEqual(reopened.jobs()[0]['id'], item['id'])
        self.assertEqual(reopened.due_jobs(159), [])
        self.assertEqual(len(reopened.due_jobs(160)), 1)
        self.assertEqual(reopened.due_jobs(170), [])

    def test_pause_resume_cancel_preserve_remaining_time(self):
        store = self.store()
        job = store.add_job('timer', 60, now=100)
        store.pause_job(job['id'], now=120)
        self.assertEqual(store.due_jobs(1000), [])
        store.resume_job(job['id'], now=1000)
        self.assertEqual(store.due_jobs(1039), [])
        self.assertEqual(len(store.due_jobs(1040)), 1)
        job = store.add_job('alarm', 10, now=100)
        self.assertEqual(store.cancel_jobs(kind='alarm'), 1)
        self.assertEqual(store.due_jobs(10000), [])

    def test_invalid_durations_do_not_create_jobs(self):
        store = self.store()
        for value in (-1, 0, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                store.add_job('timer', value)
        self.assertEqual(store.jobs(), [])

    def test_calendar_and_shelf_are_deduplicated(self):
        store = self.store()
        store.save_event('meeting', 'Rapat', '2026-10-22T10:00:00+07:00', 3600)
        store.save_event('meeting', 'Rapat baru', '2026-10-22T11:00:00+07:00', 3600)
        self.assertEqual(len(store.calendar_events()), 1)
        path = Path(self.temp.name) / 'notes.txt'
        path.write_text('hello', encoding='utf-8')
        store.add_file(path)
        store.add_file(path)
        self.assertEqual(len(store.files()), 1)
        store.remove_file(str(path.resolve()))
        self.assertTrue(path.exists(), 'Removing a shelf item must not delete the file')

    def test_speech_worker_is_reaped_after_result(self):
        self.assertIsNotNone(importlib.util.find_spec('speech_worker'), 'On-demand worker missing')
        from speech_worker import SpeechJob
        job = SpeechJob(recognize_example)
        before = {p.pid for p in multiprocessing.active_children()}
        result = job.run(b'example', timeout=5)
        self.assertEqual(result['text'], 'timer 5 menit')
        self.assertFalse(job.busy)
        self.assertIsNone(job.process)
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, before)

    def test_disposable_task_reaps_process_and_keeps_heavy_imports_out(self):
        import sys
        import threading
        from tasks import invoke
        before = {p.pid for p in multiprocessing.active_children()}
        modules = {name for name in sys.modules if name.startswith(('winsdk', 'pycaw', 'spotipy'))}
        self.assertIn('Belum paham', invoke('command', 'asdfxyz bukan perintah'))
        with self.assertRaisesRegex(RuntimeError, 'Unknown task'):
            invoke('not-a-task')
        canceled = threading.Event()
        canceled.set()
        with self.assertRaisesRegex(RuntimeError, 'canceled'):
            invoke('system', canceled=canceled)
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, before)
        self.assertEqual({name for name in sys.modules if name.startswith(('winsdk', 'pycaw', 'spotipy'))}, modules)

    def test_ics_reimport_replaces_moved_events_and_rejects_fast_recurrence(self):
        import datetime as dt
        from integrations import import_calendar
        store = self.store()
        path = Path(self.temp.name) / 'schedule.ics'
        date = (dt.datetime.now() + dt.timedelta(days=1)).strftime('%Y%m%d')
        def write(hour, rule='FREQ=DAILY;COUNT=3'):
            path.write_text(f'BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nUID:test\nDTSTART:{date}T{hour}0000\nSUMMARY:Rapat\nRRULE:{rule}\nEND:VEVENT\nEND:VCALENDAR\n', encoding='utf-8')
        write('10')
        self.assertEqual(import_calendar(path, store), 3)
        write('11')
        self.assertEqual(import_calendar(path, store), 3)
        self.assertEqual(len(store.calendar_events()), 3)
        self.assertTrue(all('T11:' in item['start'] for item in store.calendar_events()))
        write('12', 'FREQ=SECONDLY')
        with self.assertRaises(ValueError):
            import_calendar(path, store)
        self.assertEqual(len(store.calendar_events()), 3)


class InputTests(unittest.TestCase):
    def test_low_memory_rejects_model_before_heavy_import(self):
        import sys
        from speech_worker import recognize
        with patch.dict(sys.modules, {'psutil': SimpleNamespace(virtual_memory=lambda: SimpleNamespace(available=100 * 2**20))}):
            with self.assertRaisesRegex(RuntimeError, 'RAM'):
                recognize(b'', {'model': 'small'})

    def test_voice_start_does_not_load_whisper(self):
        import sys
        from stt import VoiceService, PushToTalk
        before = 'faster_whisper' in sys.modules
        with patch.object(PushToTalk, 'start'), patch.object(PushToTalk, 'stop'):
            voice = VoiceService(lambda text: None).start()
            self.assertIsNone(voice.job.process)
            self.assertEqual('faster_whisper' in sys.modules, before)
            voice.stop()

    def test_numeric_commands_preserve_decimal_and_reject_invalid_input(self):
        from intents import parse
        self.assertEqual(parse('timer 1.5 menit').args.get('seconds'), 90)
        self.assertEqual(parse('timer 1,5 menit').args.get('seconds'), 90)
        self.assertEqual(parse('timer -5 menit').name, 'invalid')
        self.assertIsNone(parse('alarm jam 25').args.get('hour'))
        self.assertIsNone(parse('alarm 13 pm').args.get('hour'))
        self.assertEqual(parse('play one dance').args.get('query'), 'one dance')

    def test_ptt_closes_stream_at_limit_and_cleans_up(self):
        import stt
        class Stream:
            closed = False
            def __init__(self, **kwargs): pass
            def start(self): pass
            def stop(self): pass
            def close(self): self.closed = True
        module = SimpleNamespace(InputStream=Stream)
        with patch.dict('sys.modules', {'sounddevice': module}), patch.object(stt.config, 'MAX_RECORD_SECONDS', 0.03):
            ptt = stt.PushToTalk(lambda audio: None)
            ptt._begin()
            stream = ptt._stream
            time.sleep(0.08)
            self.assertFalse(ptt._recording)
            self.assertTrue(stream.closed)
            ptt.stop()

    def test_ptt_does_not_rearm_until_hotkey_released(self):
        import stt
        ptt = stt.PushToTalk(lambda audio: None)
        starts = []
        ptt._begin = lambda: starts.append(True)
        def key(name, kind):
            ptt._on_key(SimpleNamespace(name=name, event_type=kind))
        key('ctrl', 'down'); key('space', 'down'); key('space', 'down')
        self.assertEqual(len(starts), 1)
        key('space', 'up'); key('space', 'down')
        self.assertEqual(len(starts), 2)

    def test_speech_timeout_reaps_worker(self):
        self.assertIsNotNone(importlib.util.find_spec('speech_worker'), 'On-demand worker missing')
        from speech_worker import SpeechJob
        job = SpeechJob(recognize_slow)
        with self.assertRaises(TimeoutError):
            job.run(b'example', timeout=0.1)
        self.assertFalse(job.busy)
        self.assertIsNone(job.process)


if __name__ == '__main__':
    unittest.main(verbosity=2)
