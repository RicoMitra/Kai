"""Watch new screenshots only. Shelf owns references, never the original files."""
import ctypes
from pathlib import Path
import os
import sys
import uuid
from PySide6.QtCore import QObject, QFileSystemWatcher, QTimer, Signal, QRunnable, QThreadPool, QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QImage,QImageReader

IMAGE_SUFFIXES=('.png','.jpg','.jpeg','.bmp','.webp')


def known_folder(identity,fallback):
    if sys.platform=='win32':
        class GUID(ctypes.Structure):_fields_=[('data',ctypes.c_ubyte*16)]
        folder_id=GUID((ctypes.c_ubyte*16).from_buffer_copy(uuid.UUID(identity).bytes_le));result=ctypes.c_wchar_p()
        shell=ctypes.WinDLL('shell32');shell.SHGetKnownFolderPath.argtypes=[ctypes.POINTER(GUID),ctypes.c_uint,ctypes.c_void_p,ctypes.POINTER(ctypes.c_wchar_p)]
        if shell.SHGetKnownFolderPath(ctypes.byref(folder_id),0,None,ctypes.byref(result))==0:
            path=Path(result.value);ctypes.windll.ole32.CoTaskMemFree(ctypes.cast(result,ctypes.c_void_p));return path
    return Path(fallback)


def downloads_folder():return known_folder('374de290-123f-4565-9164-39c4925e467b',Path.home()/'Downloads')


class IntakeSignals(QObject):
    ready=Signal(str,str,str,bool)
    failed=Signal(str)


class InspectShelf(QRunnable):
    def __init__(self,payload,source,folder,quiet=False):
        super().__init__();self.payload=payload;self.source=source;self.folder=folder;self.quiet=quiet;self.signals=IntakeSignals()

    def run(self):
        try:
            import hashlib
            image=self.payload if isinstance(self.payload,QImage) else None
            path=None if image is not None else Path(self.payload).resolve();digest=''
            if path and path.suffix.lower() in IMAGE_SUFFIXES and path.is_file():
                reader=QImageReader(str(path));reader.setAllocationLimit(64);size=reader.size()
                if 0<size.width()*size.height()<=12_000_000:image=reader.read()
            if image is not None and not image.isNull():
                if image.width()*image.height()>12_000_000:raise ValueError('Clipboard image exceeds 12 megapixels')
                # RGB32 ignores PNG compression/metadata and clipboard alpha differences.
                hashed=hashlib.sha256(f'{image.width()}x{image.height()}:'.encode())
                # Preserve the exact RGB32 digest without a second full-sized image.
                for y in range(0,image.height(),64):
                    strip=image.copy(0,y,image.width(),min(64,image.height()-y)).convertToFormat(QImage.Format_RGB32)
                    hashed.update(strip.constBits())
                del strip
                digest=hashed.hexdigest()
                if path is None:
                    data=QByteArray();buffer=QBuffer(data);buffer.open(QIODevice.WriteOnly)
                    if not image.save(buffer,'PNG') or data.size()>4*1024**2:raise ValueError('Clipboard PNG limit: 4 MiB')
                    path=self.folder/(digest+'.png')
                    used=sum(p.stat().st_size for p in self.folder.glob('*.png'))
                    if not path.exists() and used+data.size()>24*1024**2:raise ValueError('Shelf image storage is full (24 MiB)')
                    if not path.exists():path.write_bytes(bytes(data))
            if path is None or not path.exists():raise ValueError('Shelf file unavailable')
            self.signals.ready.emit(str(path),digest,self.source,self.quiet)
        except Exception as exc:self.signals.failed.emit(str(exc))


class ShelfIntake(QObject):
    changed=Signal()
    offered=Signal(str)
    error=Signal(str)

    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.stopped=False;self.queue=[];self.job=None;self.reconciled=False
        self.folder=store.path.parent/'clipboard-images';self.folder.mkdir(exist_ok=True)
        self.pool=QThreadPool(self);self.pool.setMaxThreadCount(1);self.pool.setExpiryTimeout(1000)

    def image(self,image):
        if hasattr(image,'toImage'):image=image.toImage()
        if not isinstance(image,QImage) or image.isNull() or self.stopped:return
        # ponytail: one queued bitmap; folder events retain screenshot bursts without RAM copies.
        self.queue=[item for item in self.queue if not isinstance(item[0],QImage)]
        self.queue.append((image,'Clipboard',False));self.start_next()

    def files(self,paths,source='Clipboard',quiet=False):
        pending={str(item[0]) for item in self.queue if not isinstance(item[0],QImage)}
        for path in paths[:100]:
            if Path(path).exists() and str(path) not in pending and len(self.queue)<100:
                self.queue.append((str(path),source,quiet));pending.add(str(path))
        self.start_next()

    def reconcile(self):
        if self.reconciled:return
        self.reconciled=True
        for row in self.store.files():
            if Path(row['path']).suffix.lower() in IMAGE_SUFFIXES:self.files([row['path']],row['source'],True)

    def start_next(self):
        if self.stopped or self.job is not None or not self.queue:return
        payload,source,quiet=self.queue.pop(0);self.purge()
        task=InspectShelf(payload,source,self.folder,quiet);self.job=task
        task.signals.ready.connect(self.ready);task.signals.failed.connect(self.failed);self.pool.start(task)

    def ready(self,path,digest,source,quiet):
        self.job=None
        if self.stopped:return
        try:
            with self.store.connection() as db:
                existing=db.execute('SELECT 1 FROM files WHERE path=? OR (fingerprint=? AND ?!=\'\')',(path,digest,digest)).fetchone()
            if digest:path=self.store.add_shelf_image(path,digest,source)
            else:self.store.add_file(path,source)
            self.changed.emit()
            if not quiet and not existing:self.offered.emit(path)
        except (OSError,ValueError) as exc:self.error.emit(str(exc))
        self.purge();self.start_next()

    def failed(self,message):
        self.job=None
        if not self.stopped:self.error.emit(message);self.start_next()

    def purge(self):
        with self.store.connection() as db:references={row[0] for row in db.execute('SELECT path FROM files')}
        for path in self.folder.glob('*.png'):
            if str(path) not in references:
                try:path.unlink()
                except OSError:pass

    def stop(self):
        self.stopped=True;self.queue.clear();self.pool.waitForDone(5000)


def screenshots_folder():
    if sys.platform == 'win32':
        class GUID(ctypes.Structure):
            _fields_ = [('data',ctypes.c_ubyte*16)]
        folder_id = GUID((ctypes.c_ubyte*16).from_buffer_copy(uuid.UUID('b7bede81-df94-4682-a7d8-57a52620b86f').bytes_le))
        result = ctypes.c_wchar_p()
        shell = ctypes.WinDLL('shell32'); shell.SHGetKnownFolderPath.argtypes = [ctypes.POINTER(GUID),ctypes.c_uint,ctypes.c_void_p,ctypes.POINTER(ctypes.c_wchar_p)]
        if shell.SHGetKnownFolderPath(ctypes.byref(folder_id),0,None,ctypes.byref(result)) == 0:
            path = Path(result.value)
            ctypes.windll.ole32.CoTaskMemFree(ctypes.cast(result,ctypes.c_void_p))
            return path
    return Path(os.environ.get('OneDrive',str(Path.home()))) / 'Pictures/Screenshots'


class ScreenshotShelf(QObject):
    added = Signal(int)
    found = Signal(object,str)
    error = Signal(str)

    def __init__(self, store, folder=None, parent=None, intake=None, downloads=False):
        super().__init__(parent)
        self.store = store
        self.intake=intake;self.downloads=downloads;self.source='Download' if downloads else 'Screenshot'
        self.folder = Path(folder) if folder else (downloads_folder() if downloads else screenshots_folder())
        self.seen = set(self.entries())
        self.pending = {}
        self.attempts = {}
        self.watcher = QFileSystemWatcher(self)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(700 if downloads else 350)
        self.timer.timeout.connect(self.scan)
        self.watcher.directoryChanged.connect(lambda _:self.timer.start())
        self._watch()

    def entries(self):
        try:
            return [path for path in self.folder.iterdir() if path.is_file() and (self.downloads or path.suffix.lower() in IMAGE_SUFFIXES) and path.suffix.lower() not in ('.crdownload','.part','.partial','.tmp','.download')]
        except OSError:
            return []

    def _watch(self):
        for path in (self.folder,self.folder.parent):
            if path.is_dir() and str(path) not in self.watcher.directories(): self.watcher.addPath(str(path))

    def scan(self):
        self._watch()
        count = 0
        for path in self.entries():
            if path in self.seen: continue
            try:
                stat=path.stat();size=(stat.st_size,stat.st_mtime_ns)
                # Two event-loop turns avoid taking a file while Snipping Tool writes it.
                if stat.st_size <= 0 or self.pending.get(path) != size or (self.downloads and not self.readable(path)):
                    self.pending[path] = size
                    self.attempts[path] = self.attempts.get(path,0)+1
                    if self.attempts[path] >= 20:
                        self.seen.add(path); self.pending.pop(path,None); self.attempts.pop(path,None)
                        continue
                    self.timer.start(); continue
                if self.intake:self.intake.files([str(path)],self.source)
                else:self.store.add_file(path,self.source)
                self.found.emit([str(path)],self.source)
                self.seen.add(path); self.pending.pop(path,None); self.attempts.pop(path,None); count += 1
            except OSError:
                self.seen.add(path)
            except Exception as exc:
                self.error.emit(str(exc)); self.seen.add(path)
        if count: self.added.emit(count)

    @staticmethod
    def readable(path):
        if sys.platform!='win32':return True
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
        kernel.CreateFileW.restype=wintypes.HANDLE;kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.CreateFileW(str(path),0x80000000,1|4,None,3,0,None)
        if handle==ctypes.c_void_p(-1).value:return False
        kernel.CloseHandle(handle);return True

    def stop(self):
        self.timer.stop()
        if self.watcher.directories(): self.watcher.removePaths(self.watcher.directories())
