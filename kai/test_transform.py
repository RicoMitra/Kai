"""Small, local conversion checks; engines are imported only in the child process."""
from pathlib import Path
import tempfile
import unittest
from tasks import invoke


class TransformTests(unittest.TestCase):
    def test_image_to_pdf_and_extract_without_parent_engine(self):
        import sys
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QImage
        with tempfile.TemporaryDirectory() as directory:
            image=QImage(40,40,QImage.Format_RGB32);image.fill(Qt.white);source=Path(directory)/'sample.png';image.save(str(source))
            request={'items':[{'path':str(source)}],'format':'pdf','scratch':directory}
            result=invoke('transform',request,timeout=30)
            pdf=Path(result['files'][0]);self.assertEqual(pdf.read_bytes()[:5],b'%PDF-')
            with self.assertRaisesRegex(RuntimeError,'Supported'):
                invoke('transform',{'items':[{'path':str(pdf)}],'format':'jpg','scratch':directory},timeout=30)
            self.assertNotIn('PySide6.QtPdf',sys.modules)

    def test_single_item_limit_and_original_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            request={'items':[{'name':'note','text':'x'}]*2,'format':'pdf','scratch':directory}
            with self.assertRaisesRegex(RuntimeError,'one'):invoke('transform',request,timeout=30)


if __name__=='__main__':unittest.main()
