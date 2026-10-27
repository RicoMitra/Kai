"""Small native pages for the productivity island; loaded only with its controls."""
import datetime as dt
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QMimeData, QUrl,QRectF,QPointF,QEvent
from PySide6.QtGui import QDrag, QIcon, QPixmap, QPainter, QColor, QFont, QImageReader,QPen,QPainterPath,QLinearGradient
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,
    QListWidget,QListWidgetItem,QAbstractItemView,QStyledItemDelegate,QStyle,
    QComboBox,QFileDialog,QSplitter,QInputDialog,QButtonGroup,QGridLayout,QFrame)


def popup(widget,position,actions):
    """Small dark context menu; actions are (label, callback) or None for a divider."""
    from PySide6.QtWidgets import QMenu
    menu=QMenu(widget)
    for action in actions:
        if action is None:menu.addSeparator()
        else:menu.addAction(action[0],action[1])
    menu.exec(position)


def empty_label(text):
    label=QLabel(text);label.setObjectName('hint');label.setAlignment(Qt.AlignCenter);label.setWordWrap(True);return label


class ClearAll(QPushButton):
    """Quiet text button. First click arms it (red, 3 s); a second click deletes everything."""
    confirmed=Signal()
    def __init__(self,label='Clear all',parent=None):
        super().__init__(label,parent);self.label=label;self.setObjectName('quiet');self.setCursor(Qt.PointingHandCursor)
        self.setToolTip('Click twice to delete everything here');self.armed=False
        self.reset=QTimer(self);self.reset.setSingleShot(True);self.reset.setInterval(3000);self.reset.timeout.connect(self.disarm)
        self.clicked.connect(self.press)
    def press(self):
        if self.armed:self.disarm();self.confirmed.emit();return
        self.armed=True;self.setText('Click again to delete');self.setProperty('armed',True);self.style().polish(self);self.reset.start()
    def disarm(self):
        self.armed=False;self.reset.stop();self.setText(self.label);self.setProperty('armed',False);self.style().polish(self)


def footer(layout,clear):
    """Count on the left, Clear all on the right — one slim line under a list."""
    row=QHBoxLayout();row.setContentsMargins(4,0,0,0);count=QLabel();count.setObjectName('hint');row.addWidget(count,1)
    button=ClearAll();button.confirmed.connect(clear);row.addWidget(button);layout.addLayout(row);return count,button


def button(label,callback,row,tip='',primary=False):
    widget=QPushButton(label);widget.setCursor(Qt.PointingHandCursor);widget.clicked.connect(callback)
    if tip:widget.setToolTip(tip)
    if primary:widget.setProperty('primary',True)  # white pill, like the reference "Buy" chip
    row.addWidget(widget);return widget


class EntryDelegate(QStyledItemDelegate):
    def paint(self,painter,option,index):
        data=index.data(Qt.UserRole+1) or {};rect=option.rect.adjusted(0,2,0,-2)
        selected=bool(option.state&QStyle.State_Selected);hover=bool(option.state&QStyle.State_MouseOver)
        painter.save();painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255,255,255,34 if selected else 22 if hover else 13));painter.drawRoundedRect(rect.adjusted(1,1,-1,-1),16,16)
        badge=rect.adjusted(12,11,-rect.width()+42,-11)
        painter.setBrush(QColor(data.get('accent','#a5a0bb')));painter.drawEllipse(badge)
        painter.setPen(QColor('#000000'));font=QFont('Segoe UI Variable');font.setPixelSize(11);font.setBold(True);painter.setFont(font)
        painter.drawText(badge,Qt.AlignCenter,data.get('symbol','K'))
        icon=index.data(Qt.DecorationRole)
        if isinstance(icon,QIcon) and not icon.isNull():icon.paint(painter,badge)
        left=rect.x()+54;width=rect.width()-left+rect.x()-18
        font.setPixelSize(13);font.setBold(True);painter.setFont(font);painter.setPen(QColor('#ffffff'))
        title=painter.fontMetrics().elidedText(data.get('title',index.data() or ''),Qt.ElideRight,width-35 if data.get('pinned') else width)
        painter.drawText(left,rect.y()+23,title)
        font.setPixelSize(11);font.setBold(False);painter.setFont(font);painter.setPen(QColor('#9b9ba1'))
        painter.drawText(left,rect.y()+40,painter.fontMetrics().elidedText(data.get('subtitle',''),Qt.ElideRight,width))
        if data.get('pinned'):
            painter.setPen(QColor('#ff9f0a'));painter.drawText(rect.adjusted(0,9,-14,0),Qt.AlignRight|Qt.AlignTop,'PIN')
        painter.restore()

    def sizeHint(self,option,index):return QSize(200,57)


def entry_list():
    widget=QListWidget();widget.setObjectName('entries');widget.setItemDelegate(EntryDelegate(widget))
    widget.setMouseTracking(True);widget.setSpacing(1);widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);widget.setUniformItemSizes(True);return widget


def add_entry(widget,identifier,title,subtitle,symbol='K',pinned=False,accent='#e5e5ea'):
    item=QListWidgetItem(title);item.setData(Qt.UserRole,identifier)
    item.setData(Qt.UserRole+1,dict(title=title,subtitle=subtitle,symbol=symbol,pinned=bool(pinned),accent=accent))
    widget.addItem(item);return item


class ClipboardPage(QWidget):
    """Search and a quiet list. Enter/double-click pastes; everything else is one right-click away."""
    paste_requested=Signal(str)
    message=Signal(str)
    def __init__(self,store,history,parent=None):
        super().__init__(parent);self.store=store;self.history=history
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(10)
        self.search=QLineEdit();self.search.setPlaceholderText('Search clipboard');self.search.setClearButtonEnabled(True);layout.addWidget(self.search)
        self.filter=QComboBox();self.filter.addItems(['All','Text','Links']);self.filter.hide()  # driven from the ••• menu
        self.items=entry_list();self.items.setContextMenuPolicy(Qt.CustomContextMenu);self.items.customContextMenuRequested.connect(self.context_menu)
        self.items.setToolTip('Enter or double-click to paste · right-click for more');layout.addWidget(self.items,1)
        self.empty=empty_label('Copied text and links appear here');layout.addWidget(self.empty,1)
        self.count,self.clear_all=footer(layout,self.delete_all)
        self.search.textChanged.connect(self.refresh);self.filter.currentIndexChanged.connect(self.refresh)
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
            label='Link' if row['kind']=='link' else 'Text'
            title=row['preview'].replace('\n',' ').strip()
            item=add_entry(self.items,row['id'],title,label+' · '+dt.datetime.fromtimestamp(row['added']).strftime('%H:%M'),'↗' if row['kind']=='link' else 'T',row['pinned'],'#0a84ff' if row['kind']=='link' else '#e5e5ea')
            if row['id']==identifier:self.items.setCurrentItem(item)
        if self.items.currentRow()<0 and self.items.count():self.items.setCurrentRow(0)
        paused=self.history is not None and not self.history.enabled
        self.empty.setText('Clipboard history is paused' if paused else 'Copied text and links appear here')
        self.items.setVisible(bool(self.items.count()));self.empty.setVisible(not self.items.count())
        self.count.setText(f"{self.items.count()} item{'s' if self.items.count()!=1 else ''}" if self.items.count() else '');self.clear_all.setVisible(bool(self.items.count()))

    def menu_actions(self):
        paused=self.history is not None and not self.history.enabled
        return [('Show all',lambda:self.filter.setCurrentIndex(0)),('Text only',lambda:self.filter.setCurrentIndex(1)),('Links only',lambda:self.filter.setCurrentIndex(2)),None,
                ('Resume history' if paused else 'Pause history',self.toggle),('Clear unpinned',self.clear)]

    def context_menu(self,position):
        item=self.items.itemAt(position)
        if not item:return
        self.items.setCurrentItem(item)
        popup(self,self.items.viewport().mapToGlobal(position),[('Paste',self.paste),('Copy',self.copy),('Pin / unpin',self.pin),None,('Delete',self.remove)])

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
    def delete_all(self):
        if self.history:self.history.clear(include_pinned=True)
        else:self.store.clear_clips(include_pinned=True)
        self.refresh();self.message.emit('Clipboard history cleared')


class NoteDelegate(QStyledItemDelegate):
    """Paint bounded rows directly; no widget, blur effect or bitmap per note."""
    delete_requested=Signal(object)
    def sizeHint(self,option,index):return QSize(220,48)

    def paint(self,painter,option,index):
        data=index.data(Qt.UserRole+1) or {};rect=QRectF(option.rect.adjusted(0,2,0,-2))
        done=index.data(Qt.CheckStateRole)==Qt.Checked.value
        selected=bool(option.state&QStyle.State_Selected);hover=bool(option.state&QStyle.State_MouseOver)
        painter.save();painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255,255,255,34 if selected else 22 if hover else 13));painter.setPen(Qt.NoPen);painter.drawRoundedRect(rect.adjusted(.5,.5,-.5,-.5),16,16)
        circle=QRectF(rect.x()+14,rect.center().y()-10,20,20)
        accent='#ffd60a'
        painter.setPen(QPen(QColor(accent) if done else QColor('#6e6e73'),1.6));painter.setBrush(QColor(accent) if done else QColor(0,0,0,0));painter.drawEllipse(circle)
        if done:
            tick=QPainterPath(QPointF(circle.x()+5,circle.y()+10));tick.lineTo(circle.x()+9,circle.y()+14);tick.lineTo(circle.x()+15,circle.y()+6)
            painter.setPen(QPen(QColor('#000000'),2,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin));painter.drawPath(tick)
        font=QFont('Segoe UI Variable');font.setPixelSize(14);font.setWeight(QFont.Medium);font.setStrikeOut(done);painter.setFont(font)
        painter.setPen(QColor('#6e6e73') if done else QColor('#ffffff'))
        width=int(rect.width()-66-(30 if data.get('pinned') else 0));left=rect.x()+48
        title=painter.fontMetrics().elidedText(data.get('title','New note'),Qt.ElideRight,width)
        subtitle=data.get('subtitle','')
        painter.drawText(QRectF(left,rect.y()+(7 if subtitle else 0),width,26 if subtitle else rect.height()),Qt.AlignVCenter,title)
        if subtitle:
            font.setPixelSize(11);font.setWeight(QFont.Normal);font.setStrikeOut(False);painter.setFont(font);painter.setPen(QColor('#9b9ba1'))
            painter.drawText(QRectF(left,rect.y()+30,width,18),Qt.AlignVCenter,painter.fontMetrics().elidedText(subtitle,Qt.ElideRight,width))
        if hover:
            # Hover-only delete button: a quiet circle with an ×.
            center=QPointF(rect.right()-24,rect.center().y())
            painter.setPen(Qt.NoPen);painter.setBrush(QColor(255,255,255,30));painter.drawEllipse(center,11,11)
            painter.setPen(QPen(QColor('#d1d1d6'),1.6,Qt.SolidLine,Qt.RoundCap))
            painter.drawLine(center+QPointF(-3.5,-3.5),center+QPointF(3.5,3.5));painter.drawLine(center+QPointF(3.5,-3.5),center+QPointF(-3.5,3.5))
        elif data.get('pinned'):
            font.setPixelSize(8);font.setStrikeOut(False);painter.setFont(font);painter.setPen(QColor('#ff9f0a'));painter.drawText(rect.adjusted(0,0,-14,0),Qt.AlignRight|Qt.AlignVCenter,'PIN')
        if option.state&QStyle.State_HasFocus:
            painter.setPen(QPen(QColor(255,255,255,90),1));painter.setBrush(Qt.NoBrush);painter.drawRoundedRect(rect.adjusted(2,2,-2,-2),14,14)
        painter.restore()

    def editorEvent(self,event,model,option,index):
        if event.type()==QEvent.MouseButtonRelease and event.button()==Qt.LeftButton and event.position().x()>option.rect.right()-40:
            self.delete_requested.emit(index.data(Qt.UserRole));return True
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
        layout.setSpacing(10)
        self.input=QLineEdit();self.input.setMaxLength(20000);self.input.setPlaceholderText('New note — press Enter');self.input.setAccessibleName('New note');layout.addWidget(self.input)
        self.items=entry_list();delegate=NoteDelegate(self.items);delegate.delete_requested.connect(self.delete_note);self.items.setItemDelegate(delegate);self.items.setAccessibleName('Notes; Space to check, Delete to remove')
        self.items.setContextMenuPolicy(Qt.CustomContextMenu);self.items.customContextMenuRequested.connect(self.context_menu);layout.addWidget(self.items,1)
        self.empty=empty_label('Nothing here yet');layout.addWidget(self.empty,1)
        self.saved,self.clear_all=footer(layout,self.delete_all)
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
        count=self.items.count();self.items.setVisible(bool(count));self.empty.setVisible(not count)
        self.saved.setText(f"{count} note{'s' if count!=1 else ''}" if count else '');self.clear_all.setVisible(bool(count))

    def menu_actions(self):
        return [('New note',self.create),('Pin / unpin selected',self.pin),('Mark selected done',self.toggle_done),None,('Delete selected',self.remove)]

    def create(self):
        self.commit();self.draft=None;self.input.setFocus()

    def changed(self):
        if not self.loading:self.dirty=True;self.saved.setText('Saving…');self.timer.start()

    def flush(self):
        if not self.dirty:return
        self.timer.stop();self.dirty=False;body=self.input.text()
        if body.strip():self.draft=self.store.save_note(self.draft,body);self.identifier=self.draft
        elif self.draft:self.store.remove_note(self.draft);self.draft=None
        self.refresh()

    def commit(self):
        self.flush();self.loading=True;self.input.clear();self.loading=False;self.draft=None

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
        if identifier==self.draft:self.loading=True;self.input.clear();self.loading=False;self.draft=None
        self.identifier=None;self.refresh()

    def delete_all(self):
        self.commit();self.store.clear_notes();self.identifier=None;self.refresh()

    def delete_note(self,identifier):
        self.identifier=identifier;self.remove()

    def context_menu(self,position):
        from PySide6.QtWidgets import QMenu
        item=self.items.itemAt(position)
        if not item:return
        self.items.setCurrentItem(item);menu=QMenu(self);menu.addAction('Done / not done',self.toggle_done);menu.addAction('Pin / unpin',self.pin);menu.addSeparator();menu.addAction('Delete',self.remove);menu.exec(self.items.viewport().mapToGlobal(position))


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
    p.setPen(Qt.NoPen);p.setBrush(QColor('#ff9f0a' if folder else '#bf5af2' if image else '#8e8e93'))
    if folder:p.drawRoundedRect(6,14,24,12,4,4);p.drawRoundedRect(6,22,52,32,5,5)
    else:
        p.drawRoundedRect(14,6,36,52,6,6);p.setPen(QColor('#000000'));p.drawLine(22,28,42,28);p.drawLine(22,36,42,36)
    p.end();return QIcon(pixmap)


class ShelfPage(QWidget):
    message=Signal(str)
    transform_requested=Signal(object)
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.queue=[]
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8)
        layout.setSpacing(10)
        self.search=QLineEdit();self.search.setPlaceholderText('Search Shelf');self.search.setClearButtonEnabled(True);layout.addWidget(self.search)
        self.filter=QComboBox();self.filter.addItems(['All','Images','Documents','Folder','Pinned']);self.filter.hide()  # driven from the ••• menu
        self.files=FileList(store);self.files.setViewMode(QListWidget.IconMode);self.files.setIconSize(QSize(84,58));self.files.setGridSize(QSize(104,92));self.files.setSpacing(4)
        self.files.setContextMenuPolicy(Qt.CustomContextMenu);self.files.customContextMenuRequested.connect(self.context_menu);self.files.setToolTip('Double-click to open · drag out to share · right-click for more')
        self.files.setMovement(QListWidget.Static);self.files.setResizeMode(QListWidget.Adjust);self.files.setSelectionMode(QAbstractItemView.ExtendedSelection);self.files.setDragEnabled(True)
        row=QHBoxLayout();row.setSpacing(12);row.addWidget(self.files,1)
        self.preview=QLabel();self.preview.setAlignment(Qt.AlignCenter);self.preview.setWordWrap(True);self.preview.setFixedWidth(160);self.preview.setObjectName('preview');self.preview.hide();row.addWidget(self.preview)
        layout.addLayout(row,1)
        self.empty=empty_label('Screenshots, copied images and new downloads land here');layout.addWidget(self.empty,1)
        self.count,self.clear_all=footer(layout,self.delete_all);self.clear_all.setToolTip('Click twice to empty Shelf · original files stay on disk')
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
        self.files.setVisible(bool(self.files.count()));self.empty.setVisible(not self.files.count())
        self.count.setText(f"{self.files.count()} item{'s' if self.files.count()!=1 else ''}" if self.files.count() else '');self.clear_all.setVisible(bool(self.files.count()))
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
        self.preview.clear();self.preview.setVisible(item is not None)
        if not item:return
        path=Path(item.data(Qt.UserRole));self.preview.setToolTip(str(path))
        if path.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp'):
            reader=QImageReader(str(path));reader.setAllocationLimit(24);reader.setScaledSize(reader.size().scaled(QSize(160,125),Qt.KeepAspectRatio));image=reader.read()
            if not image.isNull():self.preview.setPixmap(QPixmap.fromImage(image));return
        try:size=f'{path.stat().st_size/1024:.1f} KiB' if path.is_file() else 'Folder'
        except OSError:size='File unavailable'
        self.preview.setText(path.name+'\n'+size)

    def next_thumbnail(self):
        if not self.isVisible():return
        if not self.queue:self.schedule_thumbnails();return
        path,item=self.queue.pop(0);reader=QImageReader(path);reader.setScaledSize(reader.size().scaled(QSize(96,96),Qt.KeepAspectRatio));reader.setAllocationLimit(24)
        image=reader.read()
        if not image.isNull():item.setIcon(QIcon(QPixmap.fromImage(image)))
        if self.queue:self.thumbnail_timer.start(30)
    def menu_actions(self):
        filters=[(label,lambda checked=False,i=i:self.filter.setCurrentIndex(i)) for i,label in enumerate(('Show all','Images','Documents','Folders','Pinned'))]
        return [('Add files…',self.choose),('Add folder…',self.choose_folder),None,*filters,None,('Clear unpinned',self.clear)]

    def context_menu(self,position):
        item=self.files.itemAt(position)
        if not item:return
        if not item.isSelected():self.files.setCurrentItem(item)
        popup(self,self.files.viewport().mapToGlobal(position),[('Open',lambda:self.open_file(item)),('Pin / unpin',self.pin),('Convert',self.transform_files),None,('Remove from Shelf',self.remove)])

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
    def delete_all(self):
        self.store.clear_files();self.refresh();self.message.emit('Shelf emptied · original files kept')
    def clear(self):
        for row in self.store.files():
            if not row['pinned']:self.store.remove_file(row['path'])
        self.refresh()


class DropZone(QPushButton):
    """Large rounded target: click to choose, or drop a file onto it."""
    def __init__(self,parent=None):
        super().__init__(parent);self.setObjectName('dropzone');self.setCursor(Qt.PointingHandCursor);self.setMinimumHeight(110)
        self.title='Drop a file or click to choose';self.detail='PNG · JPG · PDF · Word (.docx)'
    def set_text(self,title,detail):self.title,self.detail=title,detail;self.update()
    def paintEvent(self,event):
        super().paintEvent(event)
        painter=QPainter(self);painter.setRenderHint(QPainter.Antialiasing);rect=QRectF(self.rect()).adjusted(1,1,-1,-1)
        painter.setPen(QPen(QColor(255,255,255,46),1.2,Qt.DashLine));painter.setBrush(Qt.NoBrush);painter.drawRoundedRect(rect,20,20)
        center=QPointF(rect.center().x(),rect.center().y()-22)
        painter.setPen(QPen(QColor('#ff9f0a'),2,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
        painter.drawLine(center+QPointF(0,7),center+QPointF(0,-7));painter.drawLine(center+QPointF(-5,-2),center+QPointF(0,-7));painter.drawLine(center+QPointF(5,-2),center+QPointF(0,-7))
        font=QFont('Segoe UI Variable');font.setPixelSize(14);font.setWeight(QFont.DemiBold);painter.setFont(font);painter.setPen(QColor('#ffffff'))
        painter.drawText(QRectF(rect.x()+16,center.y()+12,rect.width()-32,22),Qt.AlignCenter,painter.fontMetrics().elidedText(self.title,Qt.ElideMiddle,int(rect.width()-32)))
        font.setPixelSize(11);font.setWeight(QFont.Normal);painter.setFont(font);painter.setPen(QColor('#9b9ba1'))
        painter.drawText(QRectF(rect.x()+16,center.y()+34,rect.width()-32,18),Qt.AlignCenter,self.detail)


class TransformPage(QWidget):
    run_requested=Signal(object)
    message=Signal(str)
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.inputs=[];self.outputs=[];self.folder=None;self.running=False;self.setAcceptDrops(True)
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(12)
        self.zone=DropZone();self.zone.clicked.connect(lambda:self.choose());layout.addWidget(self.zone,1)
        self.source=QButtonGroup(self);self.format=QButtonGroup(self)
        row=QHBoxLayout();row.setSpacing(6)
        for group,labels,caption in ((self.source,('PNG','JPG','PDF','Word'),'FROM'),(self.format,('PDF','MD','Word'),'TO')):
            heading=QLabel(caption);heading.setObjectName('caption');row.addWidget(heading)
            for index,label in enumerate(labels):
                item=QPushButton(label);item.setObjectName('chip');item.setCheckable(True);item.setCursor(Qt.PointingHandCursor);group.addButton(item,index);row.addWidget(item)
            group.button(0).setChecked(True)
            if caption=='FROM':row.addStretch(1)
        layout.addLayout(row)
        self.source.idClicked.connect(self.choose)
        self.results=QListWidget();self.results.hide()  # result path kept for Save; shown in the drop zone
        row=QHBoxLayout();row.setSpacing(8);self.info=QLabel();self.info.setObjectName('hint');self.info.hide();row.addWidget(self.info,1)
        self.clear_button=button('Clear',self.clear,row,'Remove temporary results; originals stay unchanged');self.save_button=button('Save',self.save,row,'Save the result before leaving this page')
        self.start_button=button('Convert',self.start,row,'Convert the chosen file',primary=True);layout.addLayout(row)
        for item in self.source.buttons()+self.format.buttons():
            if item.text()=='Word':item.setToolTip('Word document (.docx)')
        self.refresh_inputs()

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
        if self.outputs:self.zone.set_text(Path(self.outputs[0]).name,'Ready — save it before leaving this page')
        elif self.inputs:self.zone.set_text(Path(self.inputs[0]['path']).name,'Click to choose another file')
        else:self.zone.set_text('Drop a file or click to choose','PNG · JPG · PDF · Word (.docx)')
        self.start_button.setVisible(not self.outputs);self.start_button.setEnabled(bool(self.inputs) and not self.running)
        self.save_button.setVisible(bool(self.outputs));self.clear_button.setVisible(bool(self.inputs or self.outputs))
    def start(self):
        if self.running:return
        if not self.inputs:self.message.emit('Choose a file first');return
        self.cleanup();import tempfile
        from storage import data_dir
        root=data_dir()/'transform-temp';root.mkdir(exist_ok=True)
        self.folder=Path(tempfile.mkdtemp(prefix='job-',dir=root));self.running=True;self.start_button.setEnabled(False);self.info.setText('Converting…');self.info.show()
        self.run_requested.emit({'items':self.inputs.copy(),'format':('pdf','md','docx')[self.format.checkedId()],'scratch':str(self.folder)})
    def finished(self,result):
        self.running=False;self.outputs=result['files'][:1];self.results.clear()
        for path in self.outputs:self.results.addItem(Path(path).name)
        self.info.setText('Ready to save.');self.info.setToolTip(result['message']);self.info.show();self.refresh_inputs()
    def failed(self,message):
        self.running=False;self.cleanup();self.info.setText(message[:110]+('…' if len(message)>110 else ''));self.info.setToolTip(message);self.info.show();self.refresh_inputs()
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
        if hasattr(self,'zone'):self.refresh_inputs()
    def clear(self):
        if self.running:self.message.emit('Wait for completion or switch pages to cancel');return
        self.inputs=[];self.cleanup()
