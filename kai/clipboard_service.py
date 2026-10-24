"""Event-driven text/URL history. Images/files are handed to Shelf, never stored here."""
import sys
from PySide6.QtCore import QObject,Signal,QTimer,QMimeData
from PySide6.QtGui import QClipboard
from storage import settings,save_settings


class ClipboardHistory(QObject):
    changed=Signal()
    image_received=Signal(object)
    files_received=Signal(object)
    url_copied=Signal(str)
    message=Signal(str)

    def __init__(self,clipboard,store,parent=None):
        super().__init__(parent);self.clipboard=clipboard;self.store=store
        self.native=isinstance(clipboard,QClipboard);self.enabled=bool(settings().get('clipboard_enabled',True));self._stopped=False
        self.pending=QTimer(self);self.pending.setSingleShot(True);self.pending.setInterval(80)
        self.pending.timeout.connect(self.capture);clipboard.dataChanged.connect(self.schedule)

    def schedule(self):
        if not self._stopped:self.pending.start()

    def set_enabled(self,enabled):
        self.enabled=bool(enabled);save_settings({'clipboard_enabled':self.enabled});self.changed.emit()

    def excluded(self,mime):
        if mime.hasFormat('application/x-kai-history') or mime.hasFormat('application/x-kde-passwordManagerHint'):return True
        if self.native and sys.platform=='win32':
            import ctypes
            user=ctypes.WinDLL('user32');user.RegisterClipboardFormatW.argtypes=[ctypes.c_wchar_p]
            if user.IsClipboardFormatAvailable(user.RegisterClipboardFormatW('ExcludeClipboardContentFromMonitorProcessing')):return True
        return any('CanIncludeInClipboardHistory' in name and bytes(mime.data(name))[:4]==b'\0\0\0\0' for name in mime.formats())

    def capture(self,mime=None):
        if self._stopped:return
        mime=mime or self.clipboard.mimeData()
        if mime is None or self.excluded(mime):return
        if mime.hasUrls():
            paths=[url.toLocalFile() for url in mime.urls()[:32] if url.isLocalFile()]
            if paths:self.files_received.emit(paths);return
        if mime.hasImage():self.image_received.emit(mime.imageData());return
        if not self.enabled or not mime.hasText():return
        value=mime.text()
        if not value.strip():return
        if len(value)>65536 or len(value.encode('utf-8'))>65536:
            self.message.emit('Clipboard text exceeds the 64 KiB limit');return
        kind='link' if value.strip().startswith(('https://','http://')) else ('code' if '\n' in value and any(part in value for part in ('def ','function ','{','import ','const ','SELECT ')) else 'text')
        self.store.add_clip(kind,value);self.changed.emit()
        if kind=='link':self.url_copied.emit(value.strip())

    def restore(self,identifier):
        row=self.store.clip(identifier)
        if not row or row['kind'] not in ('text','link','code'):return False
        mime=QMimeData();mime.setData('application/x-kai-history',b'1');mime.setText(row['content'])
        self.clipboard.setMimeData(mime);return True

    def clear(self):self.store.clear_clips();self.changed.emit()
    def remove(self,identifier):self.store.remove_clip(identifier);self.changed.emit()
    def stop(self):
        self._stopped=True;self.pending.stop()
        try:self.clipboard.dataChanged.disconnect(self.schedule)
        except RuntimeError:pass
