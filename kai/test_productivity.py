"""Persistence, bounded history and safe calculator regression checks."""
from pathlib import Path
import tempfile
import unittest
from storage import Store
from quick_command import calculate,suggestions


class ProductivityTests(unittest.TestCase):
    def test_history_dedupe_pin_search_quota_and_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.sqlite3';store=Store(path)
            identifier=store.add_clip('text','keep this');store.pin_clip(identifier)
            self.assertEqual(store.add_clip('text','keep this'),identifier)
            for index in range(100):store.add_clip('text',f'Entry {index}')
            self.assertEqual(len(store.clips(limit=80)),80)
            self.assertEqual(store.clips()[0]['id'],identifier)
            self.assertEqual(store.clips('Entry 99')[0]['preview'],'Entry 99')
            store.clear_clips();self.assertEqual(len(Store(path).clips()),1)
            with self.assertRaises(ValueError):store.add_clip('text','x'*65537)
            for index in range(19):store.pin_clip(store.add_clip('text',f'Pinned {index}'))
            with self.assertRaises(ValueError):store.pin_clip(store.add_clip('text','Too many pins'))

    def test_notes_and_shelf_metadata_keep_original(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(Path(directory)/'test.sqlite3');file=Path(directory)/'keep.txt';file.write_text('original')
            store.add_file(file,'Clipboard');store.pin_file(file);store.file_opened(file)
            self.assertEqual(store.files()[0]['opened'],1);self.assertEqual(store.files()[0]['pinned'],1)
            store.remove_file(str(file));self.assertEqual(file.read_text(),'original')
            identifier=store.save_note(body='First idea');store.save_note(identifier,'Edited idea',True)
            self.assertEqual(Store(store.path).note(identifier)['body'],'Edited idea')
            self.assertTrue(store.notes('Edited')[0]['done']);store.remove_note(identifier)
            self.assertIsNone(store.note(identifier))

    def test_calculator_and_search_do_not_execute_code(self):
        self.assertEqual(calculate('(125+75)*3/2'),'300.0')
        self.assertEqual(calculate('-12 + 4 * 5'),'8')
        for expression in ("__import__('os').system('calc')",'2**999999','1/0','[1]*99','10**12**12','True+1','(1).__class__'):
            with self.assertRaises((ValueError,SyntaxError,ZeroDivisionError,OverflowError)):calculate(expression)
        values=suggestions('code',[{'name':'Visual Studio Code','target':'code','kind':'app'}])
        self.assertEqual(values[0]['target'],'code')


if __name__=='__main__':unittest.main()
