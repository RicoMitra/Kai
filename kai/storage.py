"""Small local SQLite store. No user data is written into the source tree."""
from contextlib import contextmanager
import datetime as dt
import json
import math
import os
from pathlib import Path
import sqlite3
import threading
import time
import uuid


def data_dir():
    path = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local/share'))) / 'Kai'
    path.mkdir(parents=True, exist_ok=True)
    return path


def settings():
    try:
        value = json.loads((data_dir() / 'settings.json').read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save_settings(values):
    existing = settings()
    existing.update(values)
    target = data_dir() / 'settings.json'
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding='utf-8')
    os.replace(temporary, target)


class Store:
    def __init__(self, path=None):
        self.path = Path(path) if path else data_dir() / 'kai.sqlite3'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL,
                    due REAL NOT NULL, seconds REAL NOT NULL, state TEXT NOT NULL,
                    remaining REAL NOT NULL DEFAULT 0, daily INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY, seconds REAL NOT NULL, finished REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS calendar (
                    uid TEXT PRIMARY KEY, title TEXT NOT NULL, start TEXT NOT NULL,
                    duration INTEGER NOT NULL, source TEXT NOT NULL DEFAULT 'local');
                CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, added REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS clipboard (
                    id TEXT PRIMARY KEY, kind TEXT NOT NULL, content TEXT NOT NULL,
                    digest TEXT UNIQUE NOT NULL, added REAL NOT NULL, pinned INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY, body TEXT NOT NULL, updated REAL NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0);
            ''')
            columns = {row['name'] for row in db.execute('PRAGMA table_info(files)')}
            for name, declaration in [('pinned','INTEGER NOT NULL DEFAULT 0'),('source',"TEXT NOT NULL DEFAULT 'File'"),('opened','INTEGER NOT NULL DEFAULT 0'),('fingerprint','TEXT')]:
                if name not in columns: db.execute(f'ALTER TABLE files ADD COLUMN {name} {declaration}')
            if 'pinned' not in {row['name'] for row in db.execute('PRAGMA table_info(notes)')}:
                db.execute('ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0')
            # Keep legacy image references in Shelf, then remove them from text history.
            db.execute("INSERT OR IGNORE INTO files (path,added,source,pinned) SELECT content,added,'Clipboard',pinned FROM clipboard WHERE kind='image'")
            db.execute("DELETE FROM clipboard WHERE kind NOT IN ('text','link','code')")
            db.execute('CREATE INDEX IF NOT EXISTS files_fingerprint ON files(fingerprint)')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def add_job(self, kind, seconds, label='', *, now=None, daily=False):
        seconds = float(seconds)
        if kind not in ('timer', 'alarm', 'pomodoro', 'break') or not math.isfinite(seconds) or not 0 < seconds <= 366 * 86400:
            raise ValueError('Durasi harus positif dan maksimal 366 hari')
        now = time.time() if now is None else now
        item = {'id': uuid.uuid4().hex, 'kind': kind, 'label': label or kind.title(),
                'due': now + seconds, 'seconds': seconds, 'state': 'active',
                'remaining': 0, 'daily': int(daily)}
        with self.connection() as db:
            db.execute('INSERT INTO jobs VALUES (:id,:kind,:label,:due,:seconds,:state,:remaining,:daily)', item)
        return item

    def jobs(self):
        with self.connection() as db:
            return [dict(r) for r in db.execute("SELECT * FROM jobs WHERE state IN ('active','paused') ORDER BY due")]

    def due_jobs(self, now=None):
        now = time.time() if now is None else now
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            items = [dict(r) for r in db.execute("SELECT * FROM jobs WHERE state='active' AND due<=?", (now,))]
            for item in items:
                if item['daily']:
                    when = dt.datetime.fromtimestamp(item['due'])
                    while when.timestamp() <= now:
                        when += dt.timedelta(days=1)
                    db.execute('UPDATE jobs SET due=? WHERE id=?', (when.timestamp(), item['id']))
                else:
                    db.execute("UPDATE jobs SET state='done' WHERE id=?", (item['id'],))
                if item['kind'] == 'pomodoro':
                    db.execute('INSERT OR IGNORE INTO sessions VALUES (?,?,?)', (item['id'], item['seconds'], now))
        return items

    def pause_job(self, job_id, now=None):
        now = time.time() if now is None else now
        with self.connection() as db:
            db.execute("UPDATE jobs SET remaining=MAX(0,due-?),state='paused' WHERE id=? AND state='active'", (now, job_id))

    def resume_job(self, job_id, now=None):
        now = time.time() if now is None else now
        with self.connection() as db:
            db.execute("UPDATE jobs SET due=?+remaining,state='active' WHERE id=? AND state='paused'", (now, job_id))

    def cancel_jobs(self, *, kind=None, job_id=None):
        if kind is None and job_id is None:
            raise ValueError('Pilih timer/alarm yang dibatalkan')
        clause, value = ('id=?', job_id) if job_id else ('kind=?', kind)
        with self.connection() as db:
            return db.execute("UPDATE jobs SET state='canceled' WHERE state IN ('active','paused') AND " + clause, (value,)).rowcount

    def focus_stats(self):
        with self.connection() as db:
            row = db.execute("SELECT COUNT(*) AS sessions, COALESCE(SUM(seconds),0) AS seconds FROM sessions WHERE date(finished,'unixepoch','localtime')=date('now','localtime')").fetchone()
            return dict(row)

    def save_event(self, uid, title, start, duration=3600, source='local'):
        parsed = dt.datetime.fromisoformat(start)
        if not title.strip() or not 0 < duration <= 366 * 86400:
            raise ValueError('Judul/waktu acara tidak valid')
        if parsed.tzinfo is None:
            parsed = parsed.astimezone()
        with self.connection() as db:
            db.execute('INSERT OR REPLACE INTO calendar VALUES (?,?,?,?,?)',
                       (uid, title.strip(), parsed.isoformat(), int(duration), source))

    def calendar_events(self):
        with self.connection() as db:
            return [dict(r) for r in db.execute('SELECT * FROM calendar ORDER BY start')]

    def replace_import(self, source, items):
        with self.connection() as db:
            db.execute('DELETE FROM calendar WHERE source=?', (source,))
            db.executemany('INSERT OR REPLACE INTO calendar VALUES (?,?,?,?,?)', items)

    def delete_event(self, uid):
        with self.connection() as db:
            db.execute('DELETE FROM calendar WHERE uid=?', (uid,))

    def add_file(self, path, source='File'):
        path = Path(path).resolve()
        if not path.exists():
            raise ValueError('File unavailable')
        with self.connection() as db:
            db.execute('INSERT OR IGNORE INTO files (path,added,source) VALUES (?,?,?)', (str(path), time.time(),source))

    def files(self):
        with self.connection() as db:
            return [dict(r) for r in db.execute('SELECT * FROM files ORDER BY pinned DESC, added DESC LIMIT 100')]

    def add_shelf_image(self,path,fingerprint,source='Clipboard'):
        """One pixel identity across clipboard PNG and original screenshot paths."""
        path=str(Path(path).resolve())
        if not Path(path).is_file():raise ValueError('Image unavailable')
        owned=(self.path.parent/'clipboard-images').resolve()
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            same=[dict(row) for row in db.execute('SELECT * FROM files WHERE fingerprint=? OR path=?',(fingerprint,path))]
            # Prefer the user's original path, preserving pin and usage on consolidation.
            originals=[row for row in same if not Path(row['path']).is_relative_to(owned) and Path(row['path']).exists()]
            if originals:chosen=originals[0]['path'];chosen_source=originals[0]['source']
            elif not Path(path).is_relative_to(owned):chosen=path;chosen_source=source
            elif same:chosen=same[0]['path'];chosen_source=same[0]['source']
            else:chosen=path;chosen_source=source
            pinned=max((row['pinned'] for row in same),default=0)
            opened=sum(row['opened'] for row in same)
            added=min((row['added'] for row in same),default=time.time())
            db.execute('DELETE FROM files WHERE fingerprint=? OR path=?',(fingerprint,path))
            db.execute('INSERT OR REPLACE INTO files (path,added,pinned,source,opened,fingerprint) VALUES (?,?,?,?,?,?)',(chosen,added,pinned,chosen_source,opened,fingerprint))
        return chosen

    def remove_file(self, path):
        with self.connection() as db:
            db.execute('DELETE FROM files WHERE path=?', (path,))

    def pin_file(self, path):
        with self.connection() as db: db.execute('UPDATE files SET pinned=1-pinned WHERE path=?',(str(path),))

    def file_opened(self, path):
        with self.connection() as db: db.execute('UPDATE files SET opened=opened+1 WHERE path=?',(str(path),))

    def add_clip(self, kind, content):
        import hashlib
        if kind not in ('text','link','code'): raise ValueError('Clipboard stores text and URLs only')
        if len(content.encode('utf-8'))>65536: raise ValueError('Text exceeds 64 KiB')
        digest=hashlib.sha256((kind+'\0'+content).encode('utf-8')).hexdigest()
        with self.connection() as db:
            row=db.execute('SELECT id FROM clipboard WHERE digest=?',(digest,)).fetchone()
            identifier=row['id'] if row else uuid.uuid4().hex
            if row: db.execute('UPDATE clipboard SET added=? WHERE id=?',(time.time(),identifier))
            else: db.execute('INSERT INTO clipboard (id,kind,content,digest,added) VALUES (?,?,?,?,?)',(identifier,kind,content,digest,time.time()))
            db.execute('DELETE FROM clipboard WHERE pinned=0 AND id NOT IN (SELECT id FROM clipboard ORDER BY pinned DESC,added DESC LIMIT 80)')
        return identifier

    def clips(self, query='', limit=40):
        with self.connection() as db:
            return [dict(row) for row in db.execute('SELECT id,kind,substr(content,1,240) AS preview,added,pinned FROM clipboard WHERE content LIKE ? ORDER BY pinned DESC,added DESC LIMIT ?',('%'+query[:200]+'%',min(80,max(1,limit))))]

    def clip(self, identifier):
        with self.connection() as db:
            row=db.execute('SELECT * FROM clipboard WHERE id=?',(identifier,)).fetchone()
            return dict(row) if row else None

    def pin_clip(self, identifier):
        with self.connection() as db:
            row=db.execute('SELECT pinned FROM clipboard WHERE id=?',(identifier,)).fetchone()
            if row and not row['pinned'] and db.execute('SELECT count(*) FROM clipboard WHERE pinned=1').fetchone()[0]>=20: raise ValueError('Pin limit: 20 items')
            db.execute('UPDATE clipboard SET pinned=1-pinned WHERE id=?',(identifier,))

    def remove_clip(self, identifier):
        with self.connection() as db: db.execute('DELETE FROM clipboard WHERE id=?',(identifier,))

    def clear_clips(self):
        with self.connection() as db: db.execute('DELETE FROM clipboard WHERE pinned=0')

    def save_note(self, identifier=None, body='', done=None):
        if len(body)>20000: raise ValueError('Note limit: 20,000 characters')
        identifier=identifier or uuid.uuid4().hex
        with self.connection() as db:
            db.execute('INSERT INTO notes (id,body,updated) VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body,updated=excluded.updated',(identifier,body,time.time()))
            if done is not None: db.execute('UPDATE notes SET done=? WHERE id=?',(int(done),identifier))
        return identifier

    def notes(self, query=''):
        with self.connection() as db: return [dict(row) for row in db.execute('SELECT id,substr(body,1,180) AS preview,updated,done,pinned FROM notes WHERE body LIKE ? ORDER BY pinned DESC,updated DESC LIMIT 100',('%'+query[:200]+'%',))]

    def set_note_done(self,identifier,done):
        with self.connection() as db:db.execute('UPDATE notes SET done=? WHERE id=?',(int(bool(done)),identifier))

    def pin_note(self,identifier):
        with self.connection() as db:db.execute('UPDATE notes SET pinned=1-pinned WHERE id=?',(identifier,))

    def toggle_note_check(self,identifier,line):
        import re
        note=self.note(identifier)
        if not note:return
        lines=note['body'].split('\n')
        if 0<=line<len(lines):
            match=re.match(r'^(\s*[-*] \[)([ xX])(\] .*)$',lines[line])
            if match:
                lines[line]=match[1]+('x' if match[2]==' ' else ' ')+match[3]
                self.save_note(identifier,'\n'.join(lines))

    def note(self, identifier):
        with self.connection() as db:
            row=db.execute('SELECT * FROM notes WHERE id=?',(identifier,)).fetchone()
            return dict(row) if row else None

    def remove_note(self, identifier):
        with self.connection() as db: db.execute('DELETE FROM notes WHERE id=?',(identifier,))


_store = None


def get_store():
    global _store
    if _store is None:
        _store = Store()
    return _store


class Scheduler:
    def __init__(self, store=None):
        self.store = store or get_store()
        self.stopped = threading.Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name='Kai scheduler', daemon=True)
        self.thread.start()

    def _run(self):
        from events import emit
        while not self.stopped.is_set():
            try:
                for item in self.store.due_jobs():
                    emit('timer_done', item['label'], item)
                    values = settings()
                    if values.get('pomodoro_auto') and item['kind'] in ('pomodoro', 'break'):
                        if item['kind'] == 'pomodoro':
                            long_break = self.store.focus_stats()['sessions'] % 4 == 0
                            minutes = 15 if long_break else 5
                            next_job = self.store.add_job('break', minutes * 60, f'Istirahat {minutes} menit')
                        else:
                            minutes = max(1, min(180, int(values.get('focus_minutes', 25))))
                            next_job = self.store.add_job('pomodoro', minutes * 60, 'Sesi fokus selesai')
                        emit('timer_started', next_job['label'], next_job)
                    if settings().get('alarm_sound', True):
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception as exc:
                emit('error', f'Penjadwal: {exc}')
            self.stopped.wait(0.5)

    def stop(self):
        self.stopped.set()
        if self.thread:
            self.thread.join(timeout=1)
