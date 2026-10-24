"""Native conversion/cleanup acceptance using generated files, never private documents."""
import json
import multiprocessing
import os
from pathlib import Path
import sys
import tempfile
import time
import zipfile
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kai'))
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage,QPainter,QFont,QPdfWriter,QTextDocument
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from storage import Store
from tasks import invoke
from panel import ControlPanel


def wait_for(predicate,seconds=20):
    deadline=time.monotonic()+seconds
    while not predicate() and time.monotonic()<deadline:QTest.qWait(50)
    assert predicate(),'Timed out'


def main():
    app=QApplication([]);report={};out=ROOT/'artifacts/productivity';out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'LOCALAPPDATA':directory}):
        root=Path(directory);png=root/'source.png';jpg=root/'source.jpg';pdf=root/'source.pdf';word=root/'source.docx';md=root/'source.md'
        image=QImage(1300,320,QImage.Format_RGB32);image.fill(Qt.white);painter=QPainter(image);painter.setPen(Qt.black);painter.setFont(QFont('Arial',46));painter.drawText(45,140,'KAI LOCAL CONVERSION');painter.end();image.save(str(png));image.save(str(jpg),'JPEG');del image
        writer=QPdfWriter(str(pdf));document=QTextDocument();document.setPlainText('KAI LOCAL PDF\nA small document created for verification.');document.print_(writer);del writer,document
        md.write_text('# KAI LOCAL NOTES\n\nA note kept locally.',encoding='utf-8')
        with zipfile.ZipFile(word,'w') as archive:
            archive.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            archive.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
            archive.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>KAI LOCAL WORD</w:t></w:r><w:drawing><a:blip r:embed="rId1"/></w:drawing></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Example table</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>')
            archive.writestr('word/_rels/document.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="media/image1.png" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"/></Relationships>')
            archive.write(png,'word/media/image1.png')
        scan=root/'scan.pdf';writer=QPdfWriter(str(scan));writer.setResolution(144);painter=QPainter(writer);painter.drawImage(0,0,QImage(str(png)));painter.end();del writer
        cases=[]
        for source,target in ((png,'pdf'),(jpg,'pdf'),(pdf,'md'),(pdf,'docx'),(word,'pdf'),(scan,'md')):
            scratch=root/f'job-{source.stem}-{target}';result=invoke('transform',{'items':[{'path':str(source)}],'format':target,'scratch':str(scratch)},timeout=30)
            assert len(result['files'])==1
            for name in result['files']:
                data=Path(name).read_bytes()
                if target=='pdf':assert data.startswith(b'%PDF-')
                elif target=='docx':
                    with zipfile.ZipFile(name) as archive:
                        assert b'KAI' in archive.read('word/document.xml')
                        assert '[Content_Types].xml' in archive.namelist() and '_rels/.rels' in archive.namelist()
                else:assert 'KAI' in data.decode('utf-8'),data[:100]
            cases.append(source.name+' → '+target)
        report['conversions']=cases;report['windows_ocr']='real generated scanned PDF recognized locally; no model download'
        assert 'PySide6.QtPdf' not in sys.modules and not any(name.startswith('winsdk.windows.media.ocr') for name in sys.modules)
        assert not multiprocessing.active_children();report['engine_isolation_and_reaped']=True
        store=Store(root/'Kai/kai.sqlite3')
        panel=ControlPanel(store=store,initial_page='Transform');panel.resize(500,326);panel.show();page=panel._built['Transform']
        try:
            assert 'Command' not in panel._pages and 'Sistem' not in panel._pages
            assert len(page.source.buttons())==4 and len(page.format.buttons())==3
            page.set_files([str(png)]);assert page.source.checkedId()==0
            with patch('product_pages.QFileDialog.getOpenFileName',return_value=(str(pdf),'')):
                page.source.button(2).click()
            assert page.source.checkedId()==2 and page.inputs[0]['path']==str(pdf)
            assert not page.format.button(0).isEnabled() and page.format.button(1).isEnabled() and page.format.button(2).isEnabled()
            page.set_files([str(png)]*3);assert len(page.inputs)==1
            page.set_files([str(png)]);page.start();scratch=page.folder;wait_for(lambda:not page.running)
            assert page.outputs,panel.status.text();assert all(Path(path).exists() for path in page.outputs)
            panel.grab().save(str(out/'fast-transform.png'))
            destination=root/'saved';destination.mkdir()
            with patch('product_pages.QFileDialog.getExistingDirectory',return_value=str(destination)):page.save()
            assert not scratch.exists() and len(list(destination.iterdir()))==1
            page.start();scratch=page.folder;panel.open_page('Notes')
            wait_for(lambda:'transform' not in panel._tasks and not scratch.exists())
            assert len(list(destination.iterdir()))==1 and not multiprocessing.active_children()
            report['ui']={'command_replaced':True,'four_workflows_only':True,'single_input_and_result':True,'save_cleans_temporary':True,'leave_cancels_and_reaps':True,'saved_copy_kept':True,'no_parent_pdf_or_ocr_engine':True}
        finally:panel.close();QTest.qWait(300)
    (out/'transform-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
