"""Pengaturan Kai. Ubah di sini, bukan di file lain."""

APP_VERSION = '4.0.0'

# Tahan tombol ini untuk bicara, lepas untuk memproses.
HOTKEY = ("ctrl", "space")

# Island: logical pixels (DIP), independent of Windows display scaling.
ISLAND_COLLAPSED_WIDTH = 72
ISLAND_COLLAPSED_HEIGHT = 24
ISLAND_EXPANDED_WIDTH = 320
ISLAND_EXPANDED_HEIGHT = 68
ISLAND_TOP = 8
ISLAND_HOT_WIDTH = 140
ISLAND_COLLAPSE_DELAY = 0.7
ISLAND_CURSOR_INTERVAL_MS = 33
ISLAND_SPRING_FREQUENCY = 22.0
# Kai 4.0: slightly underdamped so the capsule settles with a soft overshoot.
ISLAND_SPRING_DAMPING = 0.78
ISLAND_COMPACT_RADIUS = 34
ISLAND_DECK_RADIUS = 30
ISLAND_MAGNET_DISTANCE = 150

# Apple system dark accents (docs/20-kai-4-dynamic-island.md).
ACCENTS = {'Transform': '#FF9F0A', 'Clipboard': '#0A84FF', 'Notes': '#FFD60A',
           'Shelf': '#BF5AF2', 'Media': '#30D158', 'Atur': '#98989D'}

SAMPLE_RATE = 16000
MIN_RECORD_SECONDS = 0.4
MAX_RECORD_SECONDS = 20

# "auto": ada GPU NVIDIA -> medium, hanya CPU -> small.
# Bisa diisi manual: tiny / base / small / medium
MODEL_SIZE = "auto"

# Nama artis/lagu yang sering diucapkan. Membantu Whisper mengeja nama dengan benar.
# Ini CONTOH, ganti dengan artis dan lagu favoritmu.
HINT_NAMES = ["Tulus", "Hindia", "Nadin Amizah", "Taylor Swift", "The Weeknd", "Blinding Lights"]

# Aplikasi yang boleh dibuka lewat "Kai, buka ...". Hanya yang terdaftar di sini yang bisa dibuka.
APPS = {
    "spotify": "spotify:",
    "chrome": "chrome",
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "notepad": "notepad",
    "kalkulator": "calc",
    "calculator": "calc",
    "file explorer": "explorer",
    "explorer": "explorer",
}

# Spotify (butuh akun Premium). Client ID diisi lewat variabel lingkungan SPOTIFY_CLIENT_ID.
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
SPOTIFY_SCOPE = "user-modify-playback-state user-read-playback-state user-library-read"
