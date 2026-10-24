"""Local bounded conversions. Imported only in the disposable conversion process."""
from pathlib import Path
import html
import re
import zipfile
import xml.etree.ElementTree as ET

SUPPORTED={'.png','.jpg','.jpeg','.pdf','.docx'}


def image_read(path,max_side=2048):
    from PySide6.QtCore import Qt,QSize
    from PySide6.QtGui import QImageReader
    reader=QImageReader(str(path));reader.setAllocationLimit(64);size=reader.size()
    if size.width()<=0 or size.height()<=0 or size.width()*size.height()>24_000_000:raise ValueError('Invalid image or image exceeds 24 megapixels')
    reader.setAutoTransform(True);reader.setScaledSize(size.scaled(QSize(max_side,max_side),Qt.KeepAspectRatio));image=reader.read()
    if image.isNull():raise ValueError('Unable to read the image')
    return image


def pdf_open(path):
    from PySide6.QtPdf import QPdfDocument
    document=QPdfDocument(None);error=document.load(str(path))
    if error!=QPdfDocument.Error.None_ or document.pageCount()<1:raise ValueError('PDF is damaged, locked, or unsupported')
    if document.pageCount()>50:document.close();raise ValueError('PDF limit: 50 pages per file')
    return document


def render_page(document,index):
    from PySide6.QtCore import Qt,QSize
    size=document.pagePointSize(index).toSize().scaled(QSize(1800,1800),Qt.KeepAspectRatio)
    image=document.render(index,size)
    if image.isNull():raise ValueError('Unable to render the PDF page')
    return image


def image_pdf(image,path):
    from PySide6.QtCore import Qt,QRectF
    from PySide6.QtGui import QPdfWriter,QPainter,QPageSize
    writer=QPdfWriter(str(path));writer.setResolution(144);writer.setPageSize(QPageSize(QPageSize.A4))
    painter=QPainter(writer)
    try:
        box=QRectF(writer.pageLayout().paintRectPixels(144));size=image.size().scaled(box.size().toSize(),Qt.KeepAspectRatio)
        target=QRectF(0,0,size.width(),size.height());target.moveCenter(box.center());painter.drawImage(target,image)
    finally:painter.end()


def text_pdf(content,path,is_html=False):
    from PySide6.QtCore import QMarginsF
    from PySide6.QtGui import QTextDocument,QFont,QPdfWriter,QPageSize
    document=QTextDocument();document.setDefaultFont(QFont('Segoe UI',11))
    if is_html:document.setHtml(content)
    else:document.setPlainText(content)
    writer=QPdfWriter(str(path));writer.setResolution(144);writer.setPageSize(QPageSize(QPageSize.A4));writer.setPageMargins(QMarginsF(12,12,12,12))
    document.print_(writer)


def text_docx(content,path):
    """Minimal editable OOXML, using only stdlib ZIP/XML; no Word process."""
    namespace='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    ET.register_namespace('w',namespace)
    root=ET.Element('{'+namespace+'}document');body=ET.SubElement(root,'{'+namespace+'}body')
    for line in content.splitlines() or ['']:
        paragraph=ET.SubElement(body,'{'+namespace+'}p');run=ET.SubElement(paragraph,'{'+namespace+'}r');text=ET.SubElement(run,'{'+namespace+'}t')
        text.set('{http://www.w3.org/XML/1998/namespace}space','preserve');text.text=line
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr('word/document.xml',ET.tostring(root,encoding='utf-8',xml_declaration=True))


def docx_read(path,scratch):
    """Paragraphs/headings/tables/embedded raster images; not a Word layout engine."""
    w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    r='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    a='{http://schemas.openxmlformats.org/drawingml/2006/main}'
    parts=[];images=0;text_length=0
    with zipfile.ZipFile(path) as archive:
        if sum(info.file_size for info in archive.infolist())>32*1024**2:raise ValueError('DOCX contents exceed 32 MiB')
        if archive.getinfo('word/document.xml').file_size>4*1024**2:raise ValueError('Word document is too complex')
        root=ET.fromstring(archive.read('word/document.xml'));relations={}
        if 'word/_rels/document.xml.rels' in archive.namelist():
            for node in ET.fromstring(archive.read('word/_rels/document.xml.rels')):
                if node.get('TargetMode')!='External':relations[node.get('Id')]=node.get('Target','')
        body=root.find(w+'body')
        for block in body:
            if block.tag==w+'p':
                value=''.join(node.text or '' for node in block.iter(w+'t'))
                style=block.find('.//'+w+'pStyle');style_name=style.get(w+'val','') if style is not None else ''
                match=re.search(r'heading\s*([1-6])',style_name,re.I);tag='h'+match[1] if match else 'p'
                text_length+=len(value)
                parts.append(f'<{tag}>'+html.escape(value)+f'</{tag}>')
                for blip in block.iter(a+'blip'):
                    target=relations.get(blip.get(r+'embed'),'')
                    import posixpath
                    member=posixpath.normpath('word/'+target)
                    if not member.startswith('word/media/') or member not in archive.namelist():continue
                    images+=1
                    if images>8:raise ValueError('Low-memory mode allows up to 8 DOCX images')
                    from PySide6.QtCore import Qt,QSize
                    source=scratch/f'embedded-{images}{Path(member).suffix}';source.write_bytes(archive.read(member))
                    image=image_read(source,1000);small=scratch/f'embedded-{images}.png';image.save(str(small),'PNG')
                    size=image.size().scaled(QSize(500,600),Qt.KeepAspectRatio)
                    parts.append(f'<p><img src="{small.as_uri()}" width="{size.width()}" height="{size.height()}"></p>')
            elif block.tag==w+'tbl':
                rows=[]
                for row in block.findall(w+'tr'):
                    rows.append([''.join(node.text or '' for node in cell.iter(w+'t')) for cell in row.findall(w+'tc')])
                if rows:
                    parts.append('<table border="1" cellspacing="0" cellpadding="4">'+''.join('<tr>'+''.join('<td>'+html.escape(cell)+'</td>' for cell in row)+'</tr>' for row in rows)+'</table>')
                    text_length+=sum(len(cell) for row in rows for cell in row)
        if text_length>200_000:raise ValueError('Document text exceeds 200,000 characters')
    return '\n'.join(parts)


def ocr_image(image,scratch):
    import asyncio
    async def read():
        from winsdk.windows.media.ocr import OcrEngine
        from winsdk.windows.storage import StorageFile
        from winsdk.windows.graphics.imaging import BitmapDecoder,BitmapPixelFormat,BitmapAlphaMode
        engine=OcrEngine.try_create_from_user_profile_languages()
        if engine is None:raise ValueError('Windows OCR language unavailable; Kai does not download models')
        path=scratch/'ocr-input.png';image.save(str(path),'PNG')
        file=await StorageFile.get_file_from_path_async(str(path));stream=await file.open_read_async()
        try:
            decoder=await BitmapDecoder.create_async(stream)
            bitmap=await decoder.get_software_bitmap_async(BitmapPixelFormat.BGRA8,BitmapAlphaMode.IGNORE)
            try:result=await engine.recognize_async(bitmap);return '\n'.join(line.text for line in result.lines)
            finally:bitmap.close()
        finally:stream.close()
    return asyncio.run(read())


def convert(request):
    items=request.get('items',[]);output=request.get('format');scratch=Path(request['scratch']).resolve();scratch.mkdir(parents=True,exist_ok=True)
    if len(items)!=1:raise ValueError('Select one file')
    if not items[0].get('path'):raise ValueError('Choose a PNG, JPG, PDF or DOCX file')
    path=Path(items[0]['path']).resolve();suffix=path.suffix.lower()
    allowed={'.png':('pdf',),'.jpg':('pdf',),'.jpeg':('pdf',),'.pdf':('md','docx'),'.docx':('pdf',)}
    if not path.is_file() or suffix not in SUPPORTED or path.stat().st_size>20*1024**2:raise ValueError('Use PNG/JPG/PDF/DOCX, up to 20 MiB/file; save legacy .doc as .docx first')
    if output not in allowed[suffix]:raise ValueError('Supported: JPG/PNG to PDF, PDF to MD/Word, Word to PDF')
    if suffix=='.pdf':
        from PySide6.QtCore import QCoreApplication
        app=QCoreApplication.instance() or QCoreApplication([])
    else:
        from PySide6.QtGui import QGuiApplication
        app=QGuiApplication.instance() or QGuiApplication([])
    name=re.sub(r'[^\w .-]','_',path.stem)[:60] or 'Result';target=scratch/f'{name}.{output}'
    if suffix in ('.png','.jpg','.jpeg'):
        image_pdf(image_read(path),target);message='Image saved as PDF.'
    elif suffix=='.docx':
        markup=docx_read(path,scratch);text_pdf(markup,target,True)
        message='Word to PDF: basic paragraphs, headings, tables and images. Complex layouts may differ.'
    else:
        pdf=pdf_open(path)
        try:
            parts=[];length=0
            for page in range(pdf.pageCount()):
                value=pdf.getAllText(page).text();length+=len(value)
                if length>200_000:raise ValueError('Text limit: 200,000 characters')
                parts.append(value)
            value='\n\n'.join(parts);del parts
            if not value.strip():
                if pdf.pageCount()>2:raise ValueError('Scanned PDF OCR is limited to 2 pages; split the document first')
                value='\n\n'.join(ocr_image(render_page(pdf,page),scratch) for page in range(pdf.pageCount()))
            if not value.strip():raise ValueError('No text could be extracted')
            if len(value)>200_000:raise ValueError('Text limit: 200,000 characters')
            if output=='docx':text_docx(value,target)
            else:target.write_text(value,encoding='utf-8')
            message='Editable text extracted. Original PDF layout is not preserved; review OCR on scanned pages.'
        finally:pdf.close()
    return {'files':[str(target)],'message':message}
