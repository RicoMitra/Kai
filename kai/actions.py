"""Aksi yang dijalankan Kai: Spotify (Premium), volume sistem, timer, alarm, buka aplikasi.
Perpustakaan khusus Windows diimpor di dalam fungsi, jadi modul ini aman diimpor di OS lain."""
import datetime as dt
from contextlib import contextmanager
import os
import random
import subprocess
import time
import traceback

import config
from events import emit

# ------------------------------------------------------------------ Spotify
_sp = None


def sp():
    global _sp
    if _sp is None:
        import spotipy
        from spotipy.oauth2 import SpotifyPKCE
        from spotipy.cache_handler import CacheFileHandler
        from storage import settings, data_dir
        client_id = settings().get('spotify_client_id') or os.environ.get("SPOTIFY_CLIENT_ID")
        if not client_id:
            raise RuntimeError("SPOTIFY_CLIENT_ID is missing; set it in Settings")
        auth = SpotifyPKCE(client_id=client_id, redirect_uri=config.SPOTIFY_REDIRECT_URI,
                           scope=config.SPOTIFY_SCOPE, open_browser=True,
                           cache_handler=CacheFileHandler(cache_path=str(data_dir() / 'spotify-token.json')))
        _sp = spotipy.Spotify(auth_manager=auth, requests_timeout=8, retries=1)
    return _sp


def _device_id():
    s = sp()
    devs = s.devices().get("devices", [])
    active = [d for d in devs if d.get("is_active")]
    if active:
        return active[0]["id"]
    if devs:
        return devs[0]["id"]
    try:  # buka Spotify desktop lalu tunggu muncul sebagai perangkat
        os.startfile("spotify:")
    except Exception:
        pass
    for _ in range(10):
        time.sleep(1)
        devs = s.devices().get("devices", [])
        if devs:
            return devs[0]["id"]
    return None


def _media_key(name):
    import keyboard
    keyboard.send(name)


def _fuzz():
    from rapidfuzz import fuzz
    return fuzz


def play(args):
    s, dev = sp(), _device_id()
    if dev is None:
        return "Spotify belum terbuka dan tidak ada perangkat aktif"
    q = args["query"]
    if args.get("track") and args.get("artist"):
        res = s.search(q=f'track:{args["track"]} artist:{args["artist"]}', type="track", limit=1)
        items = res["tracks"]["items"]
        if items:
            s.start_playback(device_id=dev, uris=[items[0]["uri"]])
            return f'Memutar {items[0]["name"]} - {items[0]["artists"][0]["name"]}'
    res = s.search(q=q, type="track,artist", limit=5)
    artists = res.get("artists", {}).get("items", [])
    tracks = res.get("tracks", {}).get("items", [])
    if artists and _fuzz().ratio(q, artists[0]["name"].lower()) >= 85:
        s.start_playback(device_id=dev, context_uri=artists[0]["uri"])
        return f'Memutar {artists[0]["name"]}'
    if tracks:
        s.start_playback(device_id=dev, uris=[tracks[0]["uri"]])
        return f'Memutar {tracks[0]["name"]} - {tracks[0]["artists"][0]["name"]}'
    return f"Tidak menemukan: {q}"


def play_artist(args):
    s, dev = sp(), _device_id()
    if dev is None:
        return "Spotify belum terbuka dan tidak ada perangkat aktif"
    q = args["artist"]
    artists = s.search(q=q, type="artist", limit=3).get("artists", {}).get("items", [])
    if artists and _fuzz().ratio(q, artists[0]["name"].lower()) >= 80:
        s.start_playback(device_id=dev, context_uri=artists[0]["uri"])
        return f'Memutar {artists[0]["name"]}'
    return play({"query": args.get("query_full") or q})   # mungkin itu judul lagu, bukan artis


def play_random(args):
    s, dev = sp(), _device_id()
    if dev is None:
        return "Spotify belum terbuka dan tidak ada perangkat aktif"
    items = s.current_user_saved_tracks(limit=50).get("items", [])
    uris = [i["track"]["uri"] for i in items]
    if not uris:
        s.shuffle(True, device_id=dev)
        s.start_playback(device_id=dev)
        return "Memutar acak dari daftar putar terakhir"
    random.shuffle(uris)
    s.start_playback(device_id=dev, uris=uris)
    return "Memutar acak dari lagu yang kamu sukai"


def next_track(args):
    try:
        from native import transport
        if transport('next'): return 'Lagu berikutnya'
    except Exception:
        pass
    try:
        sp().next_track()
    except Exception:
        _media_key("next track")
    return "Lagu berikutnya"


def prev_track(args):
    try:
        from native import transport
        if transport('prev'): return 'Lagu sebelumnya'
    except Exception:
        pass
    try:
        sp().previous_track()
    except Exception:
        _media_key("previous track")
    return "Lagu sebelumnya"


def restart(args):
    try:
        from native import transport
        if transport('restart'): return 'Diulang dari awal'
    except Exception:
        pass
    sp().seek_track(0)
    return "Diulang dari awal"


def pause(args):
    try:
        from native import transport
        if transport('pause'): return 'Dijeda'
    except Exception:
        pass
    try:
        pb = sp().current_playback()
        if pb and pb.get("is_playing"):
            sp().pause_playback()
            return "Dijeda"
        return "Sudah berhenti"
    except Exception:
        _media_key("play/pause media")
        return "Play/pause"


def resume(args):
    try:
        from native import transport
        if transport('resume'): return 'Dilanjutkan'
    except Exception:
        pass
    try:
        pb = sp().current_playback()
        if pb and pb.get("is_playing"):
            return "Sudah diputar"
        sp().start_playback()
        return "Dilanjutkan"
    except Exception:
        _media_key("play/pause media")
        return "Play/pause"


# ------------------------------------------------------------------ volume sistem
@contextmanager
def _endpoint():
    import ctypes
    import comtypes
    result = ctypes.windll.ole32.CoInitializeEx(None, 0)
    if result not in (0, 1, -2147417850):  # Existing STA is also usable.
        raise OSError('COM audio tidak dapat diinisialisasi')
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    dev = AudioUtilities.GetSpeakers()
    try:
        if hasattr(dev, "EndpointVolume"):
            endpoint = dev.EndpointVolume
        else:
            iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            endpoint = cast(iface, POINTER(IAudioEndpointVolume))
        yield endpoint
    finally:
        endpoint = dev = None
        if result in (0, 1):
            ctypes.windll.ole32.CoUninitialize()


def volume_set(args):
    level = max(0, min(100, int(args["level"])))
    with _endpoint() as endpoint:
        endpoint.SetMasterVolumeLevelScalar(level / 100, None)
    return f"Volume {level}%"


def _volume_step(sign, args):
    with _endpoint() as ep:
        now = round(ep.GetMasterVolumeLevelScalar() * 100)
        new = max(0, min(100, now + sign * int(args.get("step", 10))))
        ep.SetMasterVolumeLevelScalar(new / 100, None)
    return f"Volume {new}%"


def volume_up(args):
    return _volume_step(+1, args)


def volume_down(args):
    return _volume_step(-1, args)


def mute(args):
    with _endpoint() as endpoint:
        endpoint.SetMute(1, None)
    return "Muted"


def unmute(args):
    with _endpoint() as endpoint:
        endpoint.SetMute(0, None)
    return "Suara dinyalakan"


# ------------------------------------------------------------------ timer, alarm, pomodoro
def _start(kind, seconds, label):
    from storage import get_store
    item = get_store().add_job(kind, seconds, label)
    emit('timer_started', label, item)
    return item


def _fmt(seconds):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return " ".join(x for x in (f"{h} jam" if h else "", f"{m} menit" if m else "",
                                f"{s} detik" if s and not h else "") if x) or "0 detik"


def timer(args):
    if not args.get("seconds"):
        return "Durasi timer tidak terdengar. Coba: timer 25 menit"
    label = args.get("label") or "Timer selesai"
    _start("timer", args["seconds"], label)
    return f"Timer {_fmt(args['seconds'])} dimulai"


def pomodoro(args):
    from storage import get_store
    get_store().cancel_jobs(kind='pomodoro')
    get_store().cancel_jobs(kind='break')
    _start("pomodoro", args["seconds"], "Sesi fokus selesai, waktunya istirahat")
    return f"Fokus {_fmt(args['seconds'])} dimulai"


def alarm(args):
    if args.get("hour") is None:
        return "Jam alarm tidak terdengar. Coba: alarm jam 6 pagi"
    now = dt.datetime.now()
    when = now.replace(hour=args["hour"], minute=args["minute"], second=0, microsecond=0)
    if when <= now:
        when += dt.timedelta(days=1)
    _start("alarm", (when - now).total_seconds(), f"Alarm {when:%H:%M}")
    return f"Alarm {when:%H:%M} dipasang (Kai harus tetap menyala)"


def cancel(args):
    kind = args["kind"]
    from storage import get_store
    n = get_store().cancel_jobs(kind=kind)
    if kind == 'pomodoro':
        n += get_store().cancel_jobs(kind='break')
    return f"{n} {kind} dibatalkan" if n else f"Tidak ada {kind} aktif"


# ------------------------------------------------------------------ lain-lain
def open_app(args):
    from rapidfuzz import process
    match = process.extractOne(args["name"], list(config.APPS), score_cutoff=80)
    if not match:
        return f'Aplikasi "{args["name"]}" tidak ada di daftar (config.py)'
    target = config.APPS[match[0]]
    subprocess.Popen(["cmd", "/c", "start", "", target])
    return f"Membuka {match[0]}"


def time_now(args):
    return dt.datetime.now().strftime("Sekarang jam %H:%M")


def weather_today(args):
    from integrations import weather
    result = weather()
    emit('weather', f"{result['city']} {result['temperature']}°C", result)
    return f"{result['city']}: {result['temperature']}°C" + (' (data tersimpan, offline)' if result['stale'] else '')


def calendar_add(args):
    from integrations import add_calendar
    return add_calendar(args['title'], args.get('when'))


def calendar_today(args):
    from integrations import today_events
    items = today_events()
    return '; '.join(f"{dt.datetime.fromisoformat(i['start']):%H:%M} {i['title']}" for i in items) or 'Tidak ada jadwal hari ini'


HANDLERS = {
    "play": play, "play_artist": play_artist, "play_random": play_random,
    "next": next_track, "prev": prev_track, "restart": restart, "pause": pause, "resume": resume,
    "volume_set": volume_set, "volume_up": volume_up, "volume_down": volume_down,
    "mute": mute, "unmute": unmute,
    "open_app": open_app,
    "invalid": lambda args: args.get('reason', 'Perintah tidak valid'),
}


def run(intent):
    fn = HANDLERS.get(intent.name)
    if fn is None:
        return f'Belum paham: "{intent.raw}"'
    try:
        return fn(intent.args)
    except Exception as e:
        traceback.print_exc()
        return f"Gagal: {e}"
