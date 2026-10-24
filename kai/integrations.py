"""On-demand local panels and bounded public API requests."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error
import uuid

from storage import data_dir, get_store, settings


def fetch_json(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'KaiDesktop/1.0 (personal desktop assistant)'})
    with urllib.request.urlopen(request, timeout=8) as response:
        content = response.read(2 * 1024 * 1024 + 1)
    if len(content) > 2 * 1024 * 1024:
        raise ValueError('Service response too large')
    return json.loads(content)


def weather(city=None):
    city = (city or settings().get('city', '')).strip()
    if not city:
        raise ValueError('Isi kota cuaca di Pengaturan Kai terlebih dahulu')
    cache = data_dir() / ('weather-' + hashlib.sha256(city.casefold().encode()).hexdigest()[:16] + '.json')
    saved = None
    if cache.exists():
        try:
            saved = json.loads(cache.read_text(encoding='utf-8'))
            if time.time() - saved['updated'] < 1200:
                return saved
        except (OSError, ValueError, KeyError):
            saved = None
    try:
        found = fetch_json('https://geocoding-api.open-meteo.com/v1/search?' + urllib.parse.urlencode({'name': city, 'count': 1, 'language': 'id'}))
        locations = found.get('results', [])
        if not locations:
            raise ValueError('Kota tidak ditemukan; tambahkan nama negara bila perlu')
        location = locations[0]
        forecast = fetch_json('https://api.open-meteo.com/v1/forecast?' + urllib.parse.urlencode({
            'latitude': location['latitude'], 'longitude': location['longitude'],
            'current': 'temperature_2m,relative_humidity_2m,weather_code', 'timezone': 'auto'}))
        result = {'city': location['name'], 'temperature': forecast['current']['temperature_2m'],
                  'humidity': forecast['current']['relative_humidity_2m'],
                  'code': forecast['current']['weather_code'], 'updated': time.time(), 'stale': False}
        cache.write_text(json.dumps(result), encoding='utf-8')
        return result
    except Exception:
        if saved is not None:
            return dict(saved, stale=True)
        raise


def parse_lrc(text):
    lines = []
    for line in text.splitlines():
        stamps = re.findall(r'\[(\d+):(\d+(?:\.\d+)?)\]', line)
        lyric = re.sub(r'\[[^]]*\]', '', line).strip()
        for minutes, seconds in stamps:
            lines.append((int(minutes) * 60 + float(seconds), lyric))
    return sorted(lines)


def lyrics(track, artist, duration=0):
    query = {'track_name': track, 'artist_name': artist}
    if duration:
        query['duration'] = round(duration)
    key = hashlib.sha256(json.dumps(query, sort_keys=True).encode()).hexdigest()
    cache_dir = data_dir() / 'lyrics'
    cache_dir.mkdir(exist_ok=True)
    path = cache_dir / (key + '.json')
    result = None
    if path.exists():
        try:
            saved = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(saved, dict) and saved.get('_expires', float('inf')) > time.time():
                result = saved
        except (OSError, ValueError, TypeError):
            pass  # A damaged cache must not permanently break this track.
    if result is None:
        try:
            try:
                result = fetch_json('https://lrclib.net/api/get?' + urllib.parse.urlencode(query))
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
                # One bounded fallback, never substitute another artist/live version.
                records = fetch_json('https://lrclib.net/api/search?' + urllib.parse.urlencode({
                    'track_name': track, 'artist_name': artist}))
                normalize = lambda value: re.sub(r'[^\w]+', ' ', str(value).casefold()).strip()
                result = next((row for row in records[:20]
                               if normalize(row.get('trackName')) == normalize(track)
                               and normalize(row.get('artistName')) == normalize(artist)
                               and (not duration or abs(float(row.get('duration') or 0)-duration) <= 2)
                               and (row.get('plainLyrics') or row.get('syncedLyrics') or row.get('instrumental'))), {})
            if not result.get('instrumental') and not (result.get('plainLyrics') or result.get('syncedLyrics')):
                result = {'_expires': time.time() + 6*3600}
        except (urllib.error.URLError, TimeoutError, OSError):
            # Short backoff prevents retrying once per media refresh when offline.
            result = {'_retry': True, '_expires': time.time() + 60}
        path.write_text(json.dumps(result), encoding='utf-8')
        # ponytail: bounded 50-track disk cache; never retain all lyrics in RAM.
        for old in sorted(cache_dir.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[50:]:
            old.unlink()
    plain, synced = result.get('plainLyrics') or '', parse_lrc(result.get('syncedLyrics') or '')
    status = ('retry' if result.get('_retry') else 'instrumental' if result.get('instrumental')
              else 'available' if plain or synced else 'unavailable')
    return {'plain': plain, 'synced': synced, 'status': status}


def add_calendar(title, when):
    from intents import normalize, parse_clock
    if not when:
        raise ValueError('Sebutkan hari dan jam acara, atau tambah melalui panel Jadwal')
    clock = parse_clock(normalize('alarm ' + when))
    if clock is None:
        raise ValueError('Jam acara belum jelas; contoh: tambah rapat besok jam 10')
    now = dt.datetime.now().astimezone()
    days = 2 if 'lusa' in when else 1 if any(word in when for word in ('besok', 'tomorrow')) else 0
    weekdays = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']
    for index, word in enumerate(weekdays):
        if re.search(r'\b' + word + r'\b', when):
            days = (index - now.weekday()) % 7
            break
    target = (now + dt.timedelta(days=days)).replace(hour=clock[0], minute=clock[1], second=0, microsecond=0)
    if target <= now:
        raise ValueError('Waktu acara sudah lewat; sebutkan besok atau tanggal lewat panel Jadwal')
    get_store().save_event(uuid.uuid4().hex, title, target.isoformat())
    return f'{title} ditambahkan: {target:%d/%m %H:%M} (kalender lokal)'


def import_calendar(path, store=None):
    import icalendar
    import recurring_ical_events
    store = store or get_store()
    path = Path(path)
    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError('Kalender maksimal 10 MB')
    calendar = icalendar.Calendar.from_ical(path.read_bytes())
    events = calendar.walk('VEVENT')
    if len(events) > 2000:
        raise ValueError('Maksimal 2000 acara sumber per kalender')
    for event in events:
        rule = event.get('rrule')
        if rule and str(rule.get('FREQ', [''])[0]).upper() in ('SECONDLY', 'MINUTELY', 'HOURLY'):
            raise ValueError('Pengulangan lebih sering dari harian tidak didukung')
        if rule and any(rule.get(field) for field in ('BYSECOND', 'BYMINUTE', 'BYHOUR')):
            raise ValueError('Impor pengulangan dengan beberapa waktu per hari belum didukung')
    today = dt.datetime.now().astimezone()
    expanded = recurring_ical_events.of(calendar).between(today - dt.timedelta(days=1), today + dt.timedelta(days=90))
    source = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]
    items = []
    for event in expanded[:2000]:
        start = event.decoded('dtstart')
        if not isinstance(start, dt.datetime):
            start = dt.datetime.combine(start, dt.time.min).astimezone()
        if start.tzinfo is None:
            start = start.astimezone()
        end = event.decoded('dtend', None)
        if isinstance(end, dt.date) and not isinstance(end, dt.datetime):
            end = dt.datetime.combine(end, dt.time.min).astimezone()
        if isinstance(end, dt.datetime) and end.tzinfo is None:
            end = end.astimezone()
        duration = max(1, int((end - start).total_seconds())) if end else 3600
        uid = source + ':' + str(event.get('uid', 'event')) + ':' + start.isoformat()
        items.append((uid, str(event.get('summary', '(tanpa judul)')), start.isoformat(), duration, source))
    if len(expanded) > 2000:
        raise ValueError('Hasil pengulangan melebihi 2000 acara; pecah kalender menjadi beberapa berkas')
    store.replace_import(source, items)
    return len(items)


def today_events(store=None):
    today = dt.datetime.now().astimezone().date()
    return [item for item in (store or get_store()).calendar_events()
            if dt.datetime.fromisoformat(item['start']).astimezone().date() == today]


def system_status():
    import psutil
    memory = psutil.virtual_memory()
    network_before = psutil.net_io_counters(); sampled_at = time.monotonic()
    drive = os.environ.get('SystemDrive', 'C:') + os.sep
    disk = psutil.disk_usage(drive)
    battery = psutil.sensors_battery()
    result = {'CPU': f'{psutil.cpu_percent(interval=0.15):.0f}%',
              'RAM': f'{memory.used / 2**30:.1f} / {memory.total / 2**30:.1f} GiB',
              'Penyimpanan': f'{disk.used / 2**30:.0f} / {disk.total / 2**30:.0f} GiB',
              'Baterai': f'{battery.percent:.0f}%' if battery else 'Tidak tersedia',
              'GPU': 'Tidak tersedia', 'Suhu GPU': 'Tidak tersedia', 'Suhu CPU': 'Tidak tersedia'}
    network_after = psutil.net_io_counters(); elapsed = max(.01,time.monotonic()-sampled_at)
    down = max(0,network_after.bytes_recv-network_before.bytes_recv)/elapsed/1024
    up = max(0,network_after.bytes_sent-network_before.bytes_sent)/elapsed/1024
    result['Jaringan'] = f'DL {down:.0f} / UL {up:.0f} KiB/s'
    processes=[]
    for process in psutil.process_iter(['name','memory_info']):
        try:
            info=process.info
            if info['memory_info']: processes.append((info['memory_info'].rss,info['name'] or 'Proses'))
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    result['Proses']='\n'.join(f'{name}   {size/2**20:.0f} MiB' for size,name in sorted(processes,reverse=True)[:5])
    try:
        probe = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,memory.used',
                                '--format=csv,noheader,nounits'], capture_output=True, text=True,
                               timeout=3, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if probe.returncode == 0 and probe.stdout.strip():
            gpu, temp, vram = probe.stdout.splitlines()[0].split(',')
            result.update({'GPU': f'{gpu.strip()}% · VRAM {vram.strip()} MiB', 'Suhu GPU': temp.strip() + '°C'})
    except (OSError, subprocess.TimeoutExpired):
        pass
    return result
