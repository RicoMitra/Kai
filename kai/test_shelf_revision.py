"""Regression for the two screenshot sources and productivity 3.0 rules."""
from pathlib import Path
import tempfile
import unittest
from storage import Store


class ShelfRevisionTests(unittest.TestCase):
    def test_clipboard_accepts_only_text_and_links(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(Path(folder)/'test.sqlite3')
            for kind in ('image','file'):
                with self.assertRaises(ValueError):store.add_clip(kind,'private.png')

    def test_both_screenshot_orders_produce_one_original_reference(self):
        for reverse in (False,True):
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);store=Store(root/'test.sqlite3')
                managed=root/'clipboard-images';managed.mkdir()
                copy=managed/'copy.png';copy.write_bytes(b'clipboard')
                original=root/'Screenshot.png';original.write_bytes(b'original')
                pairs=[(copy,'Clipboard'),(original,'Screenshot')]
                if reverse:pairs.reverse()
                for path,source in pairs:store.add_shelf_image(path,'same-pixels',source)
                self.assertEqual(len(store.files()),1)
                self.assertEqual(store.files()[0]['path'],str(original.resolve()))
                self.assertTrue(copy.exists());self.assertTrue(original.exists())

    def test_notes_pin_and_checklist_are_persistent(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(Path(folder)/'test.sqlite3')
            first=store.save_note(body='Important\n- [ ] Ship Kai')
            store.pin_note(first)
            store.save_note(body='Newer')
            store.toggle_note_check(first,1)
            reopened=Store(store.path)
            self.assertEqual(reopened.notes()[0]['id'],first)
            self.assertIn('- [x] Ship Kai',reopened.note(first)['body'])
            reopened.toggle_note_check(first,1)
            self.assertIn('- [ ] Ship Kai',reopened.note(first)['body'])


if __name__=='__main__':unittest.main()
