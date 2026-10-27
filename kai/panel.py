"""On-demand native island controls. No legacy timer/calendar/weather pages."""
import datetime as dt
from pathlib import Path
import threading
from PySide6.QtCore import QObject,QRunnable,QThreadPool,QTimer,Qt,Signal,QUrl,QVariantAnimation,QEasingCurve
from PySide6.QtGui import QPixmap,QShortcut,QKeySequence,QDesktopServices
import config
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,
    QStackedWidget,QFormLayout,QCheckBox)
from widgets import ASSETS,MusicCard,PageNavigation
from product_pages import TransformPage,ClipboardPage,NotesPage,ShelfPage,FileList
from events import emit
from storage import get_store,settings,save_settings
from tasks import invoke

class TaskSignals(QObject):
    done = Signal(object)
    failed = Signal(str)
    finished=Signal()

class Task(QRunnable):
    def __init__(self, function):
        super().__init__()
        self.function = function
        self.signals = TaskSignals()
        self.canceled = threading.Event()
        self.finished_event=threading.Event()

    def run(self):
        try:
            if not self.canceled.is_set():
                result=self.function(self.canceled)
                if not self.canceled.is_set():self.signals.done.emit(result)
        except Exception as exc:
            if not self.canceled.is_set():
                try:self.signals.failed.emit(str(exc))
                except RuntimeError:pass  # QApplication has already destroyed the receiver.
        finally:
            self.finished_event.set()
            try:self.signals.finished.emit()
            except RuntimeError:pass

class ControlPanel(QWidget):
    dismissed=Signal()
    resized=Signal(int)
    paste_requested=Signal(str)
    shelf_opened=Signal()

    def __init__(self,media=None,audio=None,store=None,parent=None,clipboard=None,initial_page='Transform'):
        super().__init__(parent);self.media=media;self.audio=audio;self.store=store or get_store();self.clipboard=clipboard
        self.setObjectName('IslandDeck');self.setAttribute(Qt.WA_DeleteOnClose)
        # Kai 4.0: iOS-style black surface, pill controls, white primary actions (docs/20).
        self.setStyleSheet("""
            QWidget { background:transparent;color:#ffffff;font-family:'Segoe UI Variable';font-size:12px; }
            QLabel#heading { font-size:16px;font-weight:600; }
            QLabel#hint,QLabel#status,QLabel#clock { color:#9b9ba1;font-size:11px; }
            QLabel#caption { color:#6e6e73;font-size:10px;font-weight:600;letter-spacing:1px;padding-right:2px; }
            QLabel#preview { background:rgba(255,255,255,13);border-radius:16px;color:#9b9ba1;font-size:11px;padding:8px; }
            QPushButton#chip { background:transparent;border:1px solid rgba(255,255,255,30);border-radius:13px;padding:4px 11px;font-size:11px;min-height:18px; }
            QPushButton#chip:hover { background:rgba(255,255,255,16); }
            QPushButton#chip:checked { background:#ffffff;color:#000000;border-color:#ffffff; }
            QPushButton#chip:disabled { color:#48484a;border-color:rgba(255,255,255,12);background:transparent; }
            QPushButton#quiet { background:transparent;color:#8e8e93;font-size:11px;font-weight:500;padding:3px 8px;border-radius:10px; }
            QPushButton#quiet:hover { color:#ffffff;background:rgba(255,255,255,14); }
            QPushButton#quiet[armed="true"] { color:#ff453a;background:rgba(255,69,58,30); }
            QPushButton#dropzone { background:rgba(255,255,255,8);border:0;border-radius:20px; }
            QPushButton#dropzone:hover { background:rgba(255,255,255,14); }
            QLineEdit,QPlainTextEdit,QTextBrowser,QComboBox { background:rgba(255,255,255,18);border:1px solid transparent;border-radius:14px;padding:8px 14px;selection-background-color:#3a3a3c; }
            QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus { border-color:rgba(255,255,255,70);background:rgba(255,255,255,24); }
            QComboBox::drop-down { border:0;width:22px; }
            QComboBox QAbstractItemView { background:#1c1c1e;border:1px solid rgba(255,255,255,24);border-radius:12px;padding:4px;selection-background-color:#3a3a3c;outline:0; }
            QListWidget { background:transparent;border:0;outline:0; }
            QListWidget::item { border-radius:16px;padding:4px;color:#ffffff; }
            QListWidget::item:selected { background:rgba(255,255,255,30); }
            QListWidget::item:hover { background:rgba(255,255,255,14); }
            QPushButton { background:rgba(255,255,255,26);border:0;border-radius:14px;padding:7px 14px;font-weight:600; }
            QPushButton:hover { background:rgba(255,255,255,40); }
            QPushButton:pressed { background:rgba(255,255,255,16); }
            QPushButton:checked { background:#ffffff;color:#000000; }
            QPushButton:disabled { color:#5b5b60;background:rgba(255,255,255,10); }
            QPushButton:focus { border:1px solid rgba(255,255,255,110); }
            QPushButton[primary="true"] { background:#ffffff;color:#000000; }
            QPushButton[primary="true"]:hover { background:#e5e5ea; }
            QPushButton[primary="true"]:pressed { background:#c7c7cc; }
            QPushButton#icon { background:rgba(255,255,255,22);border-radius:14px;padding:0 0 2px 0;min-width:28px;max-width:28px;min-height:28px;max-height:28px;font-size:11px;color:#d1d1d6; }
            QPushButton#icon:hover { background:rgba(255,255,255,46); }
            QCheckBox { spacing:10px; }
            QCheckBox::indicator { width:18px;height:18px;border-radius:9px;border:1.5px solid #6e6e73; }
            QCheckBox::indicator:checked { background:#30d158;border-color:#30d158; }
            QScrollBar:vertical { background:transparent;width:4px; }
            QScrollBar::handle:vertical { background:#48484a;border-radius:2px;min-height:20px; }
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }
            QSplitter::handle { background:rgba(255,255,255,14);width:1px; }
            QMenu { background:#1c1c1e;border:1px solid rgba(255,255,255,24);border-radius:12px;padding:5px; }
            QMenu::item { padding:6px 18px;border-radius:8px; }
            QMenu::item:selected { background:#3a3a3c; }
            QToolTip { background:#1c1c1e;color:#ffffff;border:1px solid rgba(255,255,255,30);border-radius:8px;padding:5px 8px; }
        """)
        self._closed=False;self._tasks={};self._lyrics=None;self._lyrics_key=None;self._auto_lyrics=False
        self.pool=QThreadPool.globalInstance();self.pool.setMaxThreadCount(1);self.pool.setExpiryTimeout(1000)
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(10)
        # Header: accent dot + title, then one "more" menu and close. Page actions live in the menu.
        header=QHBoxLayout();header.setSpacing(10)
        self.dot=QLabel();self.dot.setFixedSize(8,8);header.addWidget(self.dot)
        self.heading=QLabel('Fast Transform');self.heading.setObjectName('heading');header.addWidget(self.heading);header.addStretch()
        self.more=self.button('•••',self._show_menu,header);self.more.setObjectName('icon');self.more.setToolTip('More · actions and settings');self.more.setAccessibleName('More')
        close=self.button('✕',self.dismissed.emit,header);close.setObjectName('icon');close.setToolTip('Close · Escape');close.setAccessibleName('Close');layout.addLayout(header)
        self.tabs=QStackedWidget();layout.addWidget(self.tabs,1)
        self._pages={};self._built={};self._nav={}
        for name in ('Transform','Clipboard','Notes','Shelf','Media','Atur'):
            widget=QWidget();self._pages[name]=widget;self.tabs.addWidget(widget)
        self.status=QLabel('');self.status.setObjectName('status');self.status.setTextFormat(Qt.PlainText);self.status.setVisible(False);layout.addWidget(self.status)
        self.navigation=PageNavigation(self);self.navigation.selected.connect(self.open_page);self._nav=self.navigation.buttons;layout.addWidget(self.navigation)
        self.escape=QShortcut(QKeySequence('Escape'),self);self.escape.activated.connect(self.dismissed.emit)
        self.timer=QTimer(self);self.timer.setInterval(1000);self.timer.timeout.connect(self._refresh)
        self.slide=QVariantAnimation(self);self.slide.setDuration(260);self.slide.setEasingCurve(QEasingCurve.OutCubic)
        self.slide.valueChanged.connect(lambda value:self.tabs.currentWidget().move(round(value),0))
        self.open_page(initial_page)

    def button(self,label,callback,layout):
        button=QPushButton(label);button.setCursor(Qt.PointingHandCursor);button.clicked.connect(callback);layout.addWidget(button);return button

    def _show_menu(self):
        from PySide6.QtWidgets import QMenu
        menu=QMenu(self);widget=self._built.get(self.current_page())
        for action in (widget.menu_actions() if hasattr(widget,'menu_actions') else []):
            if action is None:menu.addSeparator()
            else:menu.addAction(*action)
        if not menu.isEmpty():menu.addSeparator()
        menu.addAction('Settings',lambda:self.open_page('Atur'))
        menu.exec(self.more.mapToGlobal(self.more.rect().bottomLeft()))

    def notify(self,message):
        self.status.setText(str(message));self.status.setVisible(bool(message))

    def current_page(self):
        return next((name for name,widget in self._pages.items() if widget is self.tabs.currentWidget()),'Transform')

    def page(self,name):
        layout=QVBoxLayout(self._pages[name]);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8);return layout

    def open_page(self,name):
        if name not in self._pages:name='Transform'
        if self.current_page()=='Transform' and name!='Transform':
            self._cleanup_transform()
        if 'Notes' in self._built:self._built['Notes'].flush()
        order=list(self._pages);before=order.index(self.current_page())
        self.slide.stop();self.tabs.currentWidget().move(0,0)
        self.tabs.setCurrentWidget(self._pages[name]);self.notify('')
        reduced=getattr(self.parentWidget(),'reduced_motion',False)
        if self.isVisible() and not reduced and order.index(name)!=before:
            # New page glides in from the direction of travel.
            self.slide.setStartValue(22. if order.index(name)>before else -22.);self.slide.setEndValue(0.);self.slide.start()
        if name not in self._built:self._build(name)
        widget=self._built.get(name)
        if widget and hasattr(widget,'refresh'):widget.refresh()
        self._update_navigation();self._sync_media_service();self.show();self.resized.emit(self.preferred_height())
        if name=='Clipboard':QTimer.singleShot(0,lambda:widget.search.setFocus() if not self._closed else None)
        if name=='Media':self.timer.start();self._refresh()
        else:
            self.timer.stop()
            if 'lyrics' in self._tasks:self._tasks['lyrics'].canceled.set()
        if name=='Shelf':self.shelf_opened.emit()

    def _build(self,name):
        layout=self.page(name)
        if name=='Transform':
            widget=TransformPage(self.store);widget.run_requested.connect(self._transform);widget.message.connect(self.notify);layout.addWidget(widget);self._built[name]=widget
        elif name=='Clipboard':
            widget=ClipboardPage(self.store,self.clipboard);widget.paste_requested.connect(self.paste_requested);widget.message.connect(self.notify);layout.addWidget(widget);self._built[name]=widget
        elif name=='Notes':
            widget=NotesPage(self.store);widget.message.connect(self.notify);layout.addWidget(widget);self._built[name]=widget
        elif name=='Shelf':
            widget=ShelfPage(self.store);widget.message.connect(self.notify);widget.transform_requested.connect(self._transform_files);layout.addWidget(widget);self._built[name]=widget;self.files=widget.files
        elif name=='Media':self._make_media(layout);self._built[name]=self.music
        elif name=='Atur':self._make_settings(layout);self._built[name]=self.client_id

    def _transform(self,request):
        if 'transform' in self._tasks:self._built['Transform'].failed('The previous worker is closing. Try again shortly.');return
        def convert(canceled):
            owner=getattr(self.media,'owner',None)
            for cleanup in list(getattr(owner,'retired',[])):
                cleanup.join(timeout=4)
                if cleanup.is_alive():raise RuntimeError('Media worker is still closing. Try again shortly.')
            return invoke('transform',request,timeout=90,canceled=canceled)
        self.task('transform',convert,self._built['Transform'].finished)

    def _cleanup_transform(self):
        widget=self._built.get('Transform')
        if not widget:return
        task=self._tasks.get('transform');folder=widget.folder
        if task:task.canceled.set()
        if task and not task.finished_event.is_set():
            task.canceled.set();widget.folder=None
            if folder:
                def remove():
                    task.finished_event.wait(95)
                    import shutil
                    shutil.rmtree(folder,ignore_errors=True)
                threading.Thread(target=remove,daemon=True,name='Kai transform cleanup').start()
        widget.running=False;widget.start_button.setEnabled(True);widget.cleanup()

    def _transform_files(self,paths):
        self.open_page('Transform');self._built['Transform'].set_files(paths)

    def _update_navigation(self):
        name=self.current_page();self.heading.setText({'Media':'Music','Clipboard':'Smart Clipboard','Shelf':'Smart Shelf','Notes':'Smarter Notes','Transform':'Fast Transform','Atur':'Settings'}.get(name,name))
        reduced=getattr(self.parentWidget(),'reduced_motion',settings().get('reduced_motion',False))
        self.dot.setStyleSheet(f"background:{config.ACCENTS.get(name,'#ffffff')};border-radius:4px;")
        self.navigation.select(name,animate=not reduced)

    def preferred_height(self):
        return {'Media':300,'Shelf':340,'Clipboard':340,'Notes':340,'Transform':330,'Atur':300}.get(self.current_page(),320)

    def _sync_media_service(self,*_):
        if hasattr(self.media,'set_active'):self.media.set_active(not self._closed and self.current_page()=='Media')

    def _execute_command(self,value):
        kind=value['kind'];target=value['target']
        if kind=='calculation':
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(value['name']);self.notify('Result copied: '+value['name'])
        elif kind in ('path','shortcut'):QDesktopServices.openUrl(QUrl.fromLocalFile(target));self.notify('Opened')
        elif kind=='url':QDesktopServices.openUrl(QUrl(target));self.notify('Opened in browser')
        elif kind=='app':self.command('buka '+value['name'].lower())
        else:self.command(target)

    def command(self,text):
        from intents import parse
        intent=parse(text)
        if intent.name in ('timer','alarm','pomodoro','calendar_add','calendar','weather') or any(word in intent.name for word in ('timer','alarm','pomodoro','calendar','weather','focus','agenda')):
            self.notify('Time, focus, calendar and weather features were removed.');return
        if intent.name not in ('mute','unmute','volume_set','volume_up','volume_down','prev','next','pause','resume','open_app','play_random','play_artist','play'):
            self.notify('Quick Command has been replaced by Fast Transform.');return
        self.task('action',lambda canceled:invoke('command',text,canceled=canceled))

    def _make_media(self,layout):
        self.music=MusicCard();self.music.transport.connect(self.media_command);self.music.lyrics_requested.connect(self._load_lyrics)
        self.music.seek_requested.connect(lambda fraction:self.media_command('seek:'+str(round(fraction,6))))
        self.music.volume_changed.connect(lambda value:self.audio.set_volume(value) if self.audio else None)
        self.music.mute_requested.connect(lambda:self.audio.toggle_mute() if self.audio else None);layout.addWidget(self.music,1)

    def _make_settings(self,layout):
        values=settings();form=QFormLayout();self.client_id=QLineEdit(values.get('spotify_client_id',''));form.addRow('Spotify Client ID',self.client_id);layout.addLayout(form)
        self.media_on_demand=QCheckBox('Load media/audio only while Music is open');self.media_on_demand.setChecked(bool(values.get('media_on_demand',True)));layout.addWidget(self.media_on_demand)
        self.capture_clipboard=QCheckBox('Save local clipboard history');self.capture_clipboard.setChecked(self.clipboard.enabled if self.clipboard else bool(values.get('clipboard_enabled',True)));layout.addWidget(self.capture_clipboard)
        hint=QLabel('Ctrl+Alt+Space opens Fast Transform. Clipboard: text/URLs only, 80 items. Images and downloads go to Shelf.');hint.setWordWrap(True);hint.setObjectName('hint');layout.addWidget(hint)
        row=QHBoxLayout();self.button('Save',self._save_settings,row).setProperty('primary',True);self.button('Login Spotify',self._spotify_login,row);layout.addLayout(row);layout.addStretch()

    def _save_settings(self):
        save_settings({'spotify_client_id':self.client_id.text().strip(),'media_on_demand':self.media_on_demand.isChecked(),'clipboard_enabled':self.capture_clipboard.isChecked()})
        if self.clipboard:self.clipboard.set_enabled(self.capture_clipboard.isChecked())
        self.notify('Saved. Media mode changes apply after restarting Kai.')

    def _spotify_login(self):
        self._save_settings();self.task('spotify',lambda canceled:invoke('login',timeout=180,canceled=canceled))

    def _refresh_files(self):
        widget=self._built.get('Shelf')
        if widget and self.current_page()=='Shelf':widget.refresh()

    def _refresh(self):
        if self._closed:return
        data=self.media.snapshot if self.media else {};audio=self.audio.snapshot if self.audio else {}
        key=(data.get('title'),data.get('artist'))
        if self._lyrics and self._lyrics_key != key:
            self._lyrics=None
        if 'Media' in self._built:self.music.set_state(data,audio,self._lyrics)
        if self.current_page()=='Media' and self._auto_lyrics and data.get('title') and self._lyrics is None and 'lyrics' not in self._tasks:self._load_lyrics()

    def closeEvent(self,event):
        self._closed=True;self.timer.stop();self.navigation.animation.stop();self.slide.stop()
        if 'Notes' in self._built:self._built['Notes'].flush()
        self._cleanup_transform()
        for task in self._tasks.values():task.canceled.set()
        for task in self._tasks.values():
            try:task.signals.done.disconnect();task.signals.failed.disconnect();task.signals.finished.disconnect()
            except (RuntimeError,TypeError):pass
        self._tasks.clear()
        if hasattr(self.media,'set_active'):self.media.set_active(False)
        import gc
        QTimer.singleShot(800,gc.collect)
        super().closeEvent(event)


    def task(self, key, function, callback=None):
            if key in self._tasks:
                return
            self.status.setVisible(key!='transform')
            self.status.setText('Working…')
            task = Task(function)
            self._tasks[key] = task
            def done(result):
                self._tasks.pop(key, None)
                if self._closed or task.canceled.is_set():
                    return
                if callback:
                    self.notify('')
                    callback(result)
                else:
                    self.status.setText(str(result))
                self._refresh()
            def failed(message):
                self._tasks.pop(key, None)
                if not self._closed and not task.canceled.is_set():
                    self.status.setText(message)
                    if key=='transform' and 'Transform' in self._built:
                        self.status.hide();self._built['Transform'].failed(message)
            task.signals.done.connect(done, Qt.QueuedConnection)
            task.signals.failed.connect(failed, Qt.QueuedConnection)
            task.signals.finished.connect(lambda:self._tasks.pop(key,None) if self._tasks.get(key) is task else None,Qt.QueuedConnection)
            self.pool.start(task)

    def media_command(self, command):
            if hasattr(self.media, 'command'):
                self.media.command(command)
                self.status.setText('')
                return
            from native import transport
            self.task('transport', lambda canceled: 'Media command sent' if transport(command) else 'No media session accepted the command')

    def _load_lyrics(self):
            data = dict(self.media.snapshot) if self.media else {}
            if not data.get('title'):
                self.status.setText('Play music first.')
                return
            self._auto_lyrics = True
            key = (data['title'], data.get('artist', ''))
            def done(result):
                current = self.media.snapshot if self.media else {}
                if key != (current.get('title'),current.get('artist','')): return
                self._lyrics, self._lyrics_key = result, key
                self.music.set_state(data,self.audio.snapshot if self.audio else {},result)
                self.status.setText({'unavailable': 'Lyrics unavailable in LRCLIB.',
                                     'instrumental': 'Instrumental track.',
                                     'retry': 'Lyrics temporarily unavailable. Try again in a minute.'}.get(result.get('status'), 'Lyrics from LRCLIB'))
            self.task('lyrics', lambda canceled: invoke('lyrics', key[0], key[1], data.get('duration', 0), canceled=canceled), done)
