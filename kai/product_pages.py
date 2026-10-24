"""Small native pages for the productivity island; loaded only with its controls."""
import datetime as dt
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QMimeData, QUrl,QRectF,QPointF,QEvent
from PySide6.QtGui import QDrag, QIcon, QPixmap, QPainter, QColor, QFont, QImageReader,QPen,QPainterPath,QLinearGradient
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,
    QListWidget,QListWidgetItem,QAbstractItemView,QStyledItemDelegate,QStyle,
    QComboBox,QFileDialog,QSplitter,QInputDialog,QButtonGroup,QGridLayout,QFrame)


def button(label,callback,row,tip=''):
    widget=QPushButton(label);widget.setCursor(Qt.PointingHandCursor);widget.clicked.connect(callback)
    if tip:widget.setToolTip(tip)
    row.addWidget(widget);return widget


class EntryDelegate(QStyledItemDelegate):
    def paint(self,painter,option,index):
        data=index.data(Qt.UserRole+1) or {};rect=option.rect.adjusted(0,2,0,-2)
        selected=bool(option.state&QStyle.State_Selected);hover=bool(option.state&QStyle.State_MouseOver)
        painter.save();painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor('#73687f') if selected else QColor(255,255,255,10))
        painter.setBrush(QColor(210,192,225,28 if selected else 10 if hover else 4));painter.drawRoundedRect(rect.adjusted(1,1,-1,-1),11,11)
        badge=rect.adjusted(12,11,-rect.width()+42,-11)
        painter.setPen(Qt.NoPen);painter.setBrush(QColor(data.get('accent','#a5a0bb')));painter.drawRoundedRect(badge,7,7)
        painter.setPen(QColor('#15141a'));font=QFont('Segoe UI Variable');font.setPixelSize(11);font.setBold(True);painter.setFont(font)
        painter.drawText(badge,Qt.AlignCenter,data.get('symbol','K'))
        icon=index.data(Qt.DecorationRole)
        if isinstance(icon,QIcon) and not icon.isNull():icon.paint(painter,badge)
        left=rect.x()+54;width=rect.width()-left+rect.x()-18
        font.setPixelSize(12);font.setBold(True);painter.setFont(font);painter.setPen(QColor('#f3f1ef'))
        title=painter.fontMetrics().elidedText(data.get('title',index.data() or ''),Qt.ElideRight,width-35 if data.get('pinned') else width)
        painter.drawText(left,rect.y()+23,title)
        font.setPixelSize(10);font.setBold(False);painter.setFont(font);painter.setPen(QColor('#a7a4af'))
        painter.drawText(left,rect.y()+40,painter.fontMetrics().elidedText(data.get('subtitle',''),Qt.ElideRight,width))
        if data.get('pinned'):
            painter.setPen(QColor('#d7c5e9'));painter.drawText(rect.adjusted(0,9,-12,0),Qt.AlignRight|Qt.AlignTop,'PIN')
        painter.restore()

    def sizeHint(self,option,index):return QSize(200,57)


def entry_list():
    widget=QListWidget();widget.setObjectName('entries');widget.setItemDelegate(EntryDelegate(widget))
    widget.setMouseTracking(True);widget.setSpacing(1);widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);widget.setUniformItemSizes(True);return widget


def add_entry(widget,identifier,title,subtitle,symbol='K',pinned=False,accent='#b6a6ce'):
    item=QListWidgetItem(title);item.setData(Qt.UserRole,identifier)
    item.setData(Qt.UserRole+1,dict(title=title,subtitle=subtitle,symbol=symbol,pinned=bool(pinned),accent=accent))
    widget.addItem(item);return item


class ClipboardPage(QWidget):
    paste_requested=Signal(str)
    message=Signal(str)
    def __init__(self,store,history,parent=None):
        super().__init__(parent);self.store=store;self.history=history
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8)
        row=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('Search text, links, or code…');row.addWidget(self.search,1)
        self.filter=QComboBox();self.filter.addItems(['All','Text','Links']);row.addWidget(self.filter);layout.addLayout(row)
        self.items=entry_list();layout.addWidget(self.items,1)
        self.empty=QLabel('Copy something. New clipboard items will appear here.');self.empty.setObjectName('hint');layout.addWidget(self.empty)
        row=QHBoxLayout();button('Paste',self.paste,row,'Paste into the last app; Enter/double-click')
        button('Copy',self.copy,row);button('Pin',self.pin,row);button('Delete',self.remove,row)
        self.pause=button('Pause',self.toggle,row,'Pause clipboard history');button('Clear',self.clear,row,'Clear unpinned history')
        layout.addLayout(row);self.search.textChanged.connect(self.refresh);self.filter.currentIndexChanged.connect(self.refresh)
        self.items.itemActivated.connect(lambda _:self.paste())
        if history:history.changed.connect(self.on_changed)
        self.refresh()

    def on_changed(self):
        if self.isVisible():self.refresh()

    def refresh(self,*_):
        current=self.items.currentItem();identifier=current.data(Qt.UserRole) if current else None
        self.items.clear();kind={1:'text',2:'link'}.get(self.filter.currentIndex())
        for row in self.store.clips(self.search.text(),80):
            if kind=='text' and row['kind'] not in ('text','code'):continue
            if kind=='link' and row['kind']!='link':continue
            label='Links' if row['kind']=='link' else 'Text'
            title=row['preview'].replace('\n',' ').strip()
            item=add_entry(self.items,row['id'],title,label+' · '+dt.datetime.fromtimestamp(row['added']).strftime('%H:%M'),label[0],row['pinned'])
            if row['id']==identifier:self.items.setCurrentItem(item)
        if self.items.currentRow()<0 and self.items.count():self.items.setCurrentRow(0)
        self.empty.setVisible(not self.items.count());self.pause.setText('Resume' if self.history and not self.history.enabled else 'Pause')

    def selected(self):
        item=self.items.currentItem();return item.data(Qt.UserRole) if item else None
    def copy(self):
        if self.history and self.history.restore(self.selected()):self.message.emit('Copied to clipboard')
    def paste(self):
        if self.selected():self.paste_requested.emit(self.selected())
    def pin(self):
        try:self.store.pin_clip(self.selected());self.refresh()
        except ValueError as exc:self.message.emit(str(exc))
    def remove(self):
        if self.history:self.history.remove(self.selected())
        else:self.store.remove_clip(self.selected())
        self.refresh()
    def toggle(self):
        if self.history:self.history.set_enabled(not self.history.enabled);self.refresh()
    def clear(self):
        if self.history:self.history.clear()
        else:self.store.clear_clips()
        self.refresh()


class NoteDelegate(QStyledItemDelegate):
    """Paint bounded rows directly; no widget, blur effect or bitmap per note."""
    def sizeHint(self,option,index):return QSize(220,58)

    def paint(self,painter,option,index):
        data=index.data(Qt.UserRole+1) or {};rect=QRectF(option.rect.adjusted(0,2,0,-2))
        done=index.data(Qt.CheckStateRole)==Qt.Checked.value
        selected=bool(option.state&QStyle.State_Selected);hover=bool(option.state&QStyle.State_MouseOver)
        painter.save();painter.setRenderHint(QPainter.Antialiasing)
        fill=QLinearGradient(rect.topLeft(),rect.bottomRight());fill.setColorAt(0,QColor(27,26,34,175 if selected else 145));fill.setColorAt(1,QColor(12,12,18,125))
        painter.setBrush(fill);painter.setPen(QColor(186,174,210,65 if selected else 35 if hover else 20));painter.drawRoundedRect(rect.adjusted(.5,.5,-.5,-.5),12,12)
        circle=QRectF(rect.x()+14,rect.center().y()-10,20,20)
        accent='#c7b9f0'
        painter.setPen(QPen(QColor(accent) if done else QColor('#a5a1b3'),1.3));painter.setBrush(QColor(accent) if done else QColor(0,0,0,0));painter.drawEllipse(circle)
        if done:
            tick=QPainterPath(QPointF(circle.x()+5,circle.y()+10));tick.lineTo(circle.x()+9,circle.y()+14);tick.lineTo(circle.x()+15,circle.y()+6)
            painter.setPen(QPen(QColor('#232033'),1.8,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin));painter.drawPath(tick)
        font=QFont('Segoe UI Variable');font.setPixelSize(14);font.setWeight(QFont.Medium);font.setStrikeOut(done);painter.setFont(font)
        painter.setPen(QColor('#a8a2af') if done else QColor('#f1edf4'))
        width=int(rect.width()-66-(30 if data.get('pinned') else 0));left=rect.x()+48
        title=painter.fontMetrics().elidedText(data.get('title','New note'),Qt.ElideRight,width)
        subtitle=data.get('subtitle','')
        painter.drawText(QRectF(left,rect.y()+(7 if subtitle else 0),width,26 if subtitle else rect.height()),Qt.AlignVCenter,title)
        if subtitle:
            font.setPixelSize(11);font.setWeight(QFont.Normal);font.setStrikeOut(False);painter.setFont(font);painter.setPen(QColor('#8c8699'))
            painter.drawText(QRectF(left,rect.y()+30,width,18),Qt.AlignVCenter,painter.fontMetrics().elidedText(subtitle,Qt.ElideRight,width))
        if data.get('pinned'):
            font.setPixelSize(8);font.setStrikeOut(False);painter.setFont(font);painter.setPen(QColor('#c0afd5'));painter.drawText(rect.adjusted(0,0,-12,0),Qt.AlignRight|Qt.AlignVCenter,'PIN')
        if option.state&QStyle.State_HasFocus:
            painter.setPen(QPen(QColor('#8a7b9d'),1,Qt.DotLine));painter.setBrush(Qt.NoBrush);painter.drawRoundedRect(rect.adjusted(3,3,-3,-3),10,10)
        painter.restore()

    def editorEvent(self,event,model,option,index):
        clicked=(event.type()==QEvent.MouseButtonRelease and event.button()==Qt.LeftButton and event.position().x()<option.rect.x()+44)
        keyboard=event.type()==QEvent.KeyPress and event.key()==Qt.Key_Space
        if clicked or keyboard:
            checked=index.data(Qt.CheckStateRole)==Qt.Checked.value
            model.setData(index,Qt.Unchecked.value if checked else Qt.Checked.value,Qt.CheckStateRole);return True
        return False


class NotesPage(QWidget):
    """A single task list: add, check, delete. No search, editor or detail view."""
    message=Signal(str)
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.identifier=None;self.draft=None;self.dirty=False;self.loading=False
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8)
        row=QHBoxLayout();row.addStretch();button('+ Note',self.create,row);layout.addLayout(row)
        self.input=QLineEdit();self.input.setMaxLength(20000);self.input.setPlaceholderText('Write a note, then press Enter…');self.input.hide();layout.addWidget(self.input)
        self.items=entry_list();self.items.setItemDelegate(NoteDelegate(self.items));self.items.setAccessibleName('Notes; Space to check, Delete to remove')
        self.items.setContextMenuPolicy(Qt.CustomContextMenu);self.items.customContextMenuRequested.connect(self.context_menu);layout.addWidget(self.items,1)
        row=QHBoxLayout();self.saved=QLabel();self.saved.setObjectName('hint');row.addWidget(self.saved,1);button('Delete',self.remove,row);layout.addLayout(row)
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.setInterval(350);self.timer.timeout.connect(self.flush)
        self.input.textChanged.connect(self.changed);self.input.returnPressed.connect(self.commit)
        self.items.currentItemChanged.connect(lambda item,old:setattr(self,'identifier',item.data(Qt.UserRole) if item else None))
        self.items.itemChanged.connect(self.note_checked);self.items.installEventFilter(self);self.refresh()

    def eventFilter(self,watched,event):
        if watched is self.items and event.type()==QEvent.KeyPress and event.key()==Qt.Key_Delete:self.remove();return True
        return super().eventFilter(watched,event)

    def refresh(self,*_):
        self.flush();selected=self.identifier;self.items.blockSignals(True);self.items.clear()
        for row in self.store.notes():
            lines=row['preview'].split('\n');title=lines[0].strip() or 'New note';subtitle=next((value.strip() for value in lines[1:] if value.strip()),'')
            item=add_entry(self.items,row['id'],title,subtitle,pinned=row['pinned']);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked if row['done'] else Qt.Unchecked)
            item.setToolTip('Space / circle: done · Delete: remove · right-click: pin')
            if row['id']==selected:self.items.setCurrentItem(item)
        if self.items.currentRow()<0:self.items.setCurrentRow(0)
        item=self.items.currentItem();self.identifier=item.data(Qt.UserRole) if item else None;self.items.blockSignals(False)
        self.saved.setText(f'{self.items.count()} notes · saved automatically')

    def create(self):
        self.commit();self.draft=None;self.input.show();self.input.setFocus()

    def changed(self):
        if not self.loading:self.dirty=True;self.saved.setText('Saving…');self.timer.start()

    def flush(self):
        if not self.dirty:return
        self.timer.stop();self.dirty=False;body=self.input.text()
        if body.strip():self.draft=self.store.save_note(self.draft,body);self.identifier=self.draft
        elif self.draft:self.store.remove_note(self.draft);self.draft=None
        self.refresh()

    def commit(self):
        self.flush();self.loading=True;self.input.clear();self.loading=False;self.draft=None;self.input.hide()

    def note_checked(self,item):
        self.store.set_note_done(item.data(Qt.UserRole),item.checkState()==Qt.Checked)

    def toggle_done(self):
        row=self.store.note(self.identifier) if self.identifier else None
        if row:self.store.set_note_done(self.identifier,not row['done']);self.refresh()

    def pin(self):
        identifier=self.identifier;self.flush();identifier=identifier or self.draft
        if identifier:self.store.pin_note(identifier);self.identifier=identifier;self.refresh()

    def remove(self):
        identifier=self.identifier or self.draft;self.flush();identifier=identifier or self.draft
        if identifier:self.store.remove_note(identifier)
        if identifier==self.draft:self.loading=True;self.input.clear();self.loading=False;self.draft=None;self.input.hide()
        self.identifier=None;self.refresh()

    def context_menu(self,position):
        from PySide6.QtWidgets import QMenu
        item=self.items.itemAt(position)
        if not item:return
        self.items.setCurrentItem(item);menu=QMenu(self);menu.addAction('Pin / unpin',self.pin);menu.addAction('Delete',self.remove);menu.exec(self.items.viewport().mapToGlobal(position))


class FileList(QListWidget):
    changed=Signal()
    def __init__(self,store):
        super().__init__();self.store=store;self.setAcceptDrops(True)
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():event.acceptProposedAction()
    def dragMoveEvent(self,event):self.dragEnterEvent(event)
    def mimeData(self,items):
        mime=QMimeData();mime.setUrls([QUrl.fromLocalFile(item.data(Qt.UserRole)) for item in items if Path(item.data(Qt.UserRole)).exists()]);return mime
    def startDrag(self,supported):
        mime=self.mimeData(self.selectedItems())
        if mime.hasUrls():
            drag=QDrag(self);drag.setMimeData(mime)
            if self.currentItem():drag.setPixmap(self.currentItem().icon().pixmap(40,40))
            drag.exec(Qt.CopyAction)
    def dropEvent(self,event):
        for url in event.mimeData().urls()[:100]:
            if url.isLocalFile():
                try:self.store.add_file(url.toLocalFile())
                except ValueError:pass
        event.acceptProposedAction();self.changed.emit()


def file_icon(folder=False,image=False):
    pixmap=QPixmap(64,64);pixmap.fill(Qt.transparent);p=QPainter(pixmap);p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen);p.setBrush(QColor('#ccb58c' if folder else '#b4accb' if image else '#b8bfcb'))
    if folder:p.drawRoundedRect(6,14,24,12,4,4);p.drawRoundedRect(6,22,52,32,5,5)
    else:
        p.drawRoundedRect(14,6,36,52,6,6);p.setPen(QColor('#44424d'));p.drawLine(22,28,42,28);p.drawLine(22,36,42,36)
    p.end();return QIcon(pixmap)


class ShelfPage(QWidget):
    message=Signal(str)
    transform_requested=Signal(object)
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.queue=[]
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8)
        row=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('Search Shelf…');row.addWidget(self.search,1)
        self.filter=QComboBox();self.filter.addItems(['All','Images','Documents','Folder','Pinned']);row.addWidget(self.filter);layout.addLayout(row)
        self.files=FileList(store);self.files.setViewMode(QListWidget.IconMode);self.files.setIconSize(QSize(64,56));self.files.setGridSize(QSize(98,100))
        self.files.setMovement(QListWidget.Static);self.files.setResizeMode(QListWidget.Adjust);self.files.setSelectionMode(QAbstractItemView.ExtendedSelection);self.files.setDragEnabled(True)
        split=QSplitter();split.addWidget(self.files)
        self.preview=QLabel('Select an image\nto preview');self.preview.setAlignment(Qt.AlignCenter);self.preview.setWordWrap(True);self.preview.setMinimumWidth(135);self.preview.setMaximumWidth(170);self.preview.setObjectName('hint');split.addWidget(self.preview);split.setSizes([340,150]);layout.addWidget(split,1)
        self.hint=QLabel('Screenshots, images & new downloads · drag to share');self.hint.setObjectName('hint');layout.addWidget(self.hint)
        row=QHBoxLayout();button('+ File',self.choose,row);button('+ Folder',self.choose_folder,row);button('Open',lambda:self.open_file(self.files.currentItem()),row)
        button('Pin',self.pin,row);button('Convert',self.transform_files,row);button('Remove',self.remove,row);button('Clear',self.clear,row);layout.addLayout(row)
        self.search.textChanged.connect(self.refresh);self.filter.currentIndexChanged.connect(self.refresh);self.files.changed.connect(self.refresh);self.files.itemDoubleClicked.connect(self.open_file)
        self.thumbnail_timer=QTimer(self);self.thumbnail_timer.setSingleShot(True);self.thumbnail_timer.timeout.connect(self.next_thumbnail)
        self.files.currentItemChanged.connect(self.preview_item);self.files.verticalScrollBar().valueChanged.connect(lambda _:self.schedule_thumbnails())
        self.icons=[file_icon(),file_icon(folder=True),file_icon(image=True)];self.refresh()

    def refresh(self,*_):
        selected={item.data(Qt.UserRole) for item in self.files.selectedItems()};self.thumbnail_timer.stop();self.queue=[];self.files.clear()
        for row in self.store.files():
            path=Path(row['path']);image=path.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp');folder=path.is_dir();kind=self.filter.currentIndex()
            if self.search.text().casefold() not in path.name.casefold():continue
            if (kind==1 and not image) or (kind==2 and (folder or image)) or (kind==3 and not folder) or (kind==4 and not row['pinned']):continue
            label=('• ' if row['pinned'] else '')+path.name
            item=QListWidgetItem(self.icons[1 if folder else 2 if image else 0],label);item.setData(Qt.UserRole,str(path));item.setSizeHint(QSize(92,96))
            item.setToolTip(str(path)+'\n'+row['source']+f" · opened {row['opened']} times");self.files.addItem(item);item.setSelected(str(path) in selected)
        self.preview_item(self.files.currentItem());self.thumbnail_timer.start(300)

    def schedule_thumbnails(self):
        self.queue=[]
        for index in range(self.files.count()):
            item=self.files.item(index);path=item.data(Qt.UserRole)
            if Path(path).suffix.lower() not in ('.png','.jpg','.jpeg','.webp','.bmp'):continue
            if self.files.visualItemRect(item).intersects(self.files.viewport().rect()) and len(self.queue)<12:self.queue.append((path,item))
            else:item.setIcon(self.icons[2])
        if self.queue:self.thumbnail_timer.start(30)

    def preview_item(self,item,*_):
        self.preview.clear()
        if not item:self.preview.setText('Select an image\nto preview');return
        path=Path(item.data(Qt.UserRole));self.preview.setToolTip(str(path))
        if path.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp'):
            reader=QImageReader(str(path));reader.setAllocationLimit(24);reader.setScaledSize(reader.size().scaled(QSize(160,125),Qt.KeepAspectRatio));image=reader.read()
            if not image.isNull():self.preview.setPixmap(QPixmap.fromImage(image));return
        try:size=f'{path.stat().st_size/1024:.1f} KiB' if path.is_file() else 'Folder'
        except OSError:size='File unavailable'
        self.preview.setText(path.name+'\n\n'+size+'\nOpen to view contents')

    def next_thumbnail(self):
        if not self.isVisible():return
        if not self.queue:self.schedule_thumbnails();return
        path,item=self.queue.pop(0);reader=QImageReader(path);reader.setScaledSize(reader.size().scaled(QSize(96,96),Qt.KeepAspectRatio));reader.setAllocationLimit(24)
        image=reader.read()
        if not image.isNull():item.setIcon(QIcon(QPixmap.fromImage(image)))
        if self.queue:self.thumbnail_timer.start(30)
    def choose(self):
        paths,_=QFileDialog.getOpenFileNames(self,'Add to Smart Shelf')
        for path in paths:self.store.add_file(path)
        self.refresh()
    def choose_folder(self):
        path=QFileDialog.getExistingDirectory(self,'Add folder to Shelf')
        if path:self.store.add_file(path);self.refresh()
    def open_file(self,item):
        if not item:return
        from PySide6.QtGui import QDesktopServices
        path=item.data(Qt.UserRole)
        if Path(path).exists():QDesktopServices.openUrl(QUrl.fromLocalFile(path));self.store.file_opened(path)
        else:self.message.emit('File moved. Remove the old reference from Shelf.')
    def pin(self):
        for item in self.files.selectedItems():self.store.pin_file(item.data(Qt.UserRole))
        self.refresh()
    def transform_files(self):
        paths=[item.data(Qt.UserRole) for item in self.files.selectedItems()]
        if len(paths)!=1:self.message.emit('Select one file for Fast Transform');return
        self.transform_requested.emit(paths)
    def remove(self):
        for item in self.files.selectedItems():self.store.remove_file(item.data(Qt.UserRole))
        self.refresh()
    def clear(self):
        for row in self.store.files():
            if not row['pinned']:self.store.remove_file(row['path'])
        self.refresh()


class TransformPage(QWidget):
    run_requested=Signal(object)
    message=Signal(str)
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.inputs=[];self.outputs=[];self.folder=None;self.running=False;self.setAcceptDrops(True)
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(4)
        columns=QHBoxLayout();columns.setSpacing(16);left=QVBoxLayout();right=QVBoxLayout();left.setSpacing(4);right.setSpacing(4)
        left.addWidget(QLabel('FROM'));right.addWidget(QLabel('TO'))
        self.source=QButtonGroup(self);self.format=QButtonGroup(self)
        for group,labels,side in ((self.source,('PNG','JPG','PDF','Word'),left),(self.format,('PDF','MD','Word'),right)):
            grid=QGridLayout();grid.setSpacing(5)
            for index,label in enumerate(labels):
                item=QPushButton(label);item.setCheckable(True);item.setCursor(Qt.PointingHandCursor);group.addButton(item,index);grid.addWidget(item,index//2,index%2)
            side.addLayout(grid);group.button(0).setChecked(True)
        self.source.idClicked.connect(self.choose)
        self.files=entry_list();self.files.setMinimumHeight(46);self.files.setMaximumHeight(70);left.addWidget(self.files,1)
        row=QHBoxLayout();button('+ File',lambda:self.choose(),row);left.addLayout(row)
        self.results=QListWidget();self.results.setMinimumHeight(46);self.results.setMaximumHeight(70);right.addWidget(self.results,1)
        self.start_button=button('Convert →',self.start,right)
        divider=QFrame();divider.setFrameShape(QFrame.VLine);divider.setStyleSheet('background:rgba(255,255,255,24);');divider.setFixedWidth(1)
        columns.addLayout(left,1);columns.addWidget(divider);columns.addLayout(right,1);layout.addLayout(columns,1)
        row=QHBoxLayout();row.addStretch();button('Save',self.save,row,'Save the result before leaving this page');button('Clear',self.clear,row,'Remove temporary results; originals stay unchanged');layout.addLayout(row)
        self.info=QLabel();self.info.setWordWrap(True);self.info.setObjectName('hint');self.info.hide();layout.addWidget(self.info)
        for item in self.source.buttons()+self.format.buttons():
            if item.text()=='Word':item.setToolTip('Word document (.docx)')

    def dragEnterEvent(self,event):
        if not self.running and event.mimeData().hasUrls():event.acceptProposedAction()
    def dropEvent(self,event):
        self.set_files([url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]);event.acceptProposedAction()
    def choose(self,source=None):
        if self.running:return
        filters=('PNG (*.png)','JPG (*.jpg *.jpeg)','PDF (*.pdf)','Word (*.docx)')
        selected=filters[source] if source is not None else 'Documents/images (*.png *.jpg *.jpeg *.pdf *.docx)'
        paths,_=QFileDialog.getOpenFileName(self,'Fast Transform','',selected)
        if paths:self.set_files([paths])
        else:self.refresh_inputs()
    def set_files(self,paths):
        if self.running:return
        if len(paths)!=1:self.message.emit('Select one file');return
        self.inputs=[{'path':str(Path(path).resolve())} for path in paths];self.refresh_inputs()
    def refresh_inputs(self):
        self.files.clear()
        self.source.setExclusive(False)
        for item in self.source.buttons():item.setChecked(False)
        self.source.setExclusive(True)
        if self.inputs and self.inputs[0].get('path'):
            suffix=Path(self.inputs[0]['path']).suffix.lower();index={'.png':0,'.jpg':1,'.jpeg':1,'.pdf':2,'.docx':3}.get(suffix)
            if index is not None:
                self.source.button(index).setChecked(True)
                allowed=(1,2) if index==2 else (0,)
                for choice in self.format.buttons():choice.setEnabled(self.format.id(choice) in allowed)
                if self.format.checkedId() not in allowed:self.format.button(allowed[0]).setChecked(True)
        for item in self.inputs:
            label=Path(item['path']).name if item.get('path') else item['name']
            add_entry(self.files,None,label,'Local file' if item.get('path') else 'Local note',symbol='↗')
    def start(self):
        if self.running:return
        if not self.inputs:self.message.emit('Choose a file first');return
        self.cleanup();import tempfile
        from storage import data_dir
        root=data_dir()/'transform-temp';root.mkdir(exist_ok=True)
        self.folder=Path(tempfile.mkdtemp(prefix='job-',dir=root));self.running=True;self.start_button.setEnabled(False);self.info.setText('Converting…');self.info.show()
        self.run_requested.emit({'items':self.inputs.copy(),'format':('pdf','md','docx')[self.format.checkedId()],'scratch':str(self.folder)})
    def finished(self,result):
        self.running=False;self.start_button.setEnabled(True);self.outputs=result['files'][:1];self.results.clear()
        for path in self.outputs:self.results.addItem(Path(path).name)
        self.info.setText('Ready to save.');self.info.setToolTip(result['message']);self.info.show()
    def failed(self,message):
        self.running=False;self.start_button.setEnabled(True);self.cleanup();self.info.setText(message[:110]+('…' if len(message)>110 else ''));self.info.setToolTip(message);self.info.show()
    def save(self):
        if not self.outputs:self.message.emit('No results yet');return
        target=QFileDialog.getExistingDirectory(self,'Save converted files')
        if not target:return
        import shutil
        try:
            for source in self.outputs:
                path=Path(source);destination=Path(target)/path.name;number=2
                while destination.exists():destination=Path(target)/f'{path.stem} ({number}){path.suffix}';number+=1
                shutil.copy2(path,destination)
            self.message.emit('Results saved. Temporary files cleared.');self.cleanup()
        except OSError as exc:self.message.emit(str(exc))
    def cleanup(self):
        if self.folder and not self.running:
            import shutil
            shutil.rmtree(self.folder,ignore_errors=True);self.folder=None
        self.outputs=[];self.results.clear();self.info.clear();self.info.hide()
    def clear(self):
        if self.running:self.message.emit('Wait for completion or switch pages to cancel');return
        self.cleanup();self.inputs=[];self.refresh_inputs()
