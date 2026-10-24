"""Pemahaman perintah Kai: teks hasil Whisper -> Intent.

Murni regex + aturan, tanpa LLM, jadi ringan dan jalan offline.
Jalankan langsung untuk mencoba:  python intents.py "puter tulus dong"
"""
import re
import sys
from dataclasses import dataclass, field


@dataclass
class Intent:
    name: str
    args: dict = field(default_factory=dict)
    raw: str = ""


# Kata pengisi yang dibuang hanya di awal/akhir kalimat (bukan di tengah, supaya judul lagu aman)
FILLERS = {"dong", "donk", "deh", "dah", "ya", "yah", "yaa", "kak", "tolong", "tlg",
           "please", "pls", "aja", "saja", "sih", "nih", "lah", "gitu", "ah"}

WAKE_RE = re.compile(
    r"^(?:(?:hey|hei|hai|halo|hello|oke|ok|okay|eh|yo)\s+)?(?:kai|kay|kae|kaye|kei)\b[\s,]*")

PLAY_VERB = (r"(?:putar(?:in|kan)?|puter(?:in)?|play(?:in)?|setel(?:in)?|mainin|nyalain|nyalakan|"
             r"dengerin|denger|dengar(?:kan)?|cariin|carikan|cari)")
# Kata kerja "putar" yang tidak ambigu dengan perintah lain (setel/nyalain bisa berarti alarm/suara)
_STRICT = re.compile(r"^(?:putar|puter|play|mainin|dengerin|cariin)\w*\b")

_LEAD_WORDS = re.compile(r"^(?:(?:dong|deh|donk|lagu(?:nya)?|song|songs|musik|music|some)\s+)+")
_PLAIN_WORDS = {"lagu", "lagunya", "musik", "musiknya", "music", "song", "songs"}
_SPLIT_ARTIST = re.compile(r"\s+(?:by|dari|nya|punya|milik|oleh)\s+")
_ARTIST_ONLY = re.compile(r"^(?:by|dari|punya|milik|oleh)\s+(.+)$")


# ---------------------------------------------------------------- angka
_ID_UNITS = {"nol": 0, "kosong": 0, "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5,
             "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9}
_EN_UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
             "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
             "eighteen": 18, "nineteen": 19}
_EN_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
            "seventy": 70, "eighty": 80, "ninety": 90}
_SPECIAL = {"sepuluh": 10, "sebelas": 11, "seratus": 100}
_MULT = {"puluh", "belas", "ratus", "hundred"}
_NUMWORDS = set(_ID_UNITS) | set(_EN_UNITS) | set(_EN_TENS) | set(_SPECIAL) | _MULT


def _run_value(tokens):
    cur = 0
    for tok in tokens:
        if tok in _ID_UNITS:
            cur += _ID_UNITS[tok]
        elif tok in _EN_UNITS:
            cur += _EN_UNITS[tok]
        elif tok in _EN_TENS:
            cur += _EN_TENS[tok]
        elif tok in _SPECIAL:
            cur += _SPECIAL[tok]
        elif tok == "belas":
            cur += 10
        elif tok == "puluh":
            cur = (cur or 1) * 10
        elif tok in ("ratus", "hundred"):
            cur = (cur or 1) * 100
    return cur


def replace_number_words(text):
    """'empat puluh' -> '40'. Hanya dipanggil di perintah yang memang butuh angka,
    supaya judul lagu seperti 'Dua Lipa' atau 'One Dance' tidak rusak."""
    out, run = [], []
    for tok in text.split():
        if tok in _NUMWORDS:
            run.append(tok)
        else:
            if run:
                out.append(str(_run_value(run)))
                run = []
            out.append(tok)
    if run:
        out.append(str(_run_value(run)))
    return " ".join(out)


_DUR_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(jam|hours?|hrs?|menit|minutes?|mins?|detik|seconds?|secs?)\b")


def parse_duration(text):
    t = replace_number_words(text)
    total, found = 0.0, False
    for m in _DUR_RE.finditer(t):
        val = float(m.group(1).replace(",", "."))
        unit = m.group(2)
        mult = 3600 if unit.startswith(("jam", "hour", "hr")) else \
            60 if unit.startswith(("menit", "minute", "min")) else 1
        total += val * mult
        found = True
    if re.search(r"\bsetengah\s+jam\b|\bhalf\s+(?:an\s+)?hour\b", t):
        total += 1800
        found = True
    elif re.search(r"\bjam\s+setengah\b", t):
        total += 1800
    return int(total) if found else None


def _apply_period(h, period):
    if period == "pagi":
        return 0 if h == 12 else h
    if period == "siang":
        return h if h >= 11 else h + 12
    if period == "sore":
        return h + 12 if h < 12 else h
    if period == "malam":
        if 6 <= h < 12:
            return h + 12
        return 0 if h == 12 else h
    return h  # subuh atau tanpa keterangan


def parse_clock(text):
    """Kembalikan (jam, menit) 24 jam, atau None."""
    t = replace_number_words(text)
    mp = re.search(r"\b(pagi|siang|sore|malam|subuh)\b", t)
    period = mp.group(1) if mp else None

    def ok(h, m):
        return (h, m) if 0 <= h <= 23 and 0 <= m <= 59 else None

    m = re.search(r"\b(\d{1,2}):(\d{2})\b\s*(am|pm)?", t)
    if m:
        h, mi, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm and not 1 <= h <= 12:
            return None
        if ampm == "pm" and h < 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
        elif not ampm:
            h = _apply_period(h, period)
        return ok(h, mi)

    m = re.search(r"\b(\d{1,2})\s*(am|pm)\b", t)
    if m:
        h = int(m.group(1))
        if not 1 <= h <= 12:
            return None
        if m.group(2) == "pm" and h < 12:
            h += 12
        elif m.group(2) == "am" and h == 12:
            h = 0
        return ok(h, 0)

    m = re.search(r"\b(?:jam|pukul)\s+(setengah\s+)?(\d{1,2})(?:\s+(lewat|kurang)\s+(\d{1,2}))?", t)
    if m:
        raw_h = int(m.group(2))
        if not 0 <= raw_h <= 23:
            return None
        h = _apply_period(raw_h, period)
        mi = 0
        if m.group(1):
            h, mi = h - 1, 30
        elif m.group(3) == "lewat":
            mi = int(m.group(4))
        elif m.group(3) == "kurang":
            h, mi = h - 1, 60 - int(m.group(4))
        return ok(h % 24, mi)

    m = re.search(r"\b(\d{1,2})\s+(pagi|siang|sore|malam|subuh)\b", t)
    if m:
        return ok(_apply_period(int(m.group(1)), m.group(2)), 0)

    m = re.search(r"\bat\s+(\d{1,2})\b", t)
    if m:
        return ok(int(m.group(1)), 0)
    return None


# ---------------------------------------------------------------- normalisasi
def normalize(text):
    t = text.lower().strip()
    t = t.replace("’", "'").replace("`", "'")
    t = re.sub(r"[-_/]", " ", t)
    if re.search(r'\balarm\b|\bbangunin\b|\bbangunkan\b', t):
        t = re.sub(r"(?<=\d)\.(?=\d)", ":", t)
    else:
        t = re.sub(r'(?<=\d),(?=\d)', '.', t)
    t = re.sub(r"[^\w\s:'.]", " ", t)
    t = re.sub(r'(?<!\d)\.|\.(?!\d)', ' ', t)
    t = re.sub(r"(?<!\d):|:(?!\d)", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _strip_fillers(toks):
    while len(toks) > 1 and toks[-1] in FILLERS:
        toks = toks[:-1]
    while len(toks) > 1 and toks[0] in FILLERS:
        toks = toks[1:]
    return toks


def _english_wrappers(t):
    t = re.sub(r"^(?:can|could|would|will)\s+you\s+(?:please\s+)?", "", t)
    t = re.sub(r"^(?:i\s+(?:wanna|want\s+to|would\s+like\s+to)|i'd\s+like\s+to|id\s+like\s+to)"
               r"\s+(?:listen\s+to|hear|play)\s+", "play ", t)
    t = re.sub(r"^(?:put\s+on|throw\s+on|let's\s+(?:listen\s+to|hear)|lets\s+(?:listen\s+to|hear))\s+",
               "play ", t)
    return t


# ---------------------------------------------------------------- aturan
def _r_cancel(t):
    m = re.match(r"^(?:batalin|batalkan|batal|matiin|matikan|cancel|hapus|hentikan|stop)\s+"
                 r"(?:the\s+|si\s+)?(alarm|timer|pomodoro)\b", t)
    if m:
        return Intent("cancel", {"kind": m.group(1)})


def _r_time(t):
    if re.search(r"\bjam\s+berapa\b|\bwhat\s+time\b|\bwhat(?:'s|s|\s+is)\s+the\s+time\b|"
                 r"\bwaktu\s+sekarang\b|\btime\s+now\b", t):
        return Intent("time_now")


def _r_alarm(t):
    if _STRICT.match(t):
        return None
    if not (re.search(r"\balarm\w*\b", t) or re.match(r"^(?:bangunin|bangunkan|banguni|wake\s+me)\b", t)):
        return None
    clock = parse_clock(t)
    if clock is None:
        return Intent("alarm", {"hour": None, "minute": None})
    return Intent("alarm", {"hour": clock[0], "minute": clock[1]})


def _r_pomodoro(t):
    if _STRICT.match(t):
        return None
    if re.search(r"\bpomodoro\b", t) or re.match(r"^(?:mulai\s+)?(?:fokus|focus)\b", t):
        return Intent("pomodoro", {"seconds": parse_duration(t) or 25 * 60})


def _r_timer(t):
    if _STRICT.match(t):
        return None
    is_timer = (re.search(r"\btimer\b|\bhitung\s+mundur\b|\bcountdown\b", t)
                or re.match(r"^(?:ingetin|ingatkan|remind)\b", t))
    if not is_timer:
        return None
    secs = parse_duration(t)
    if secs is None:
        m = re.search(r"\b(\d+)\b", replace_number_words(t))
        if m:
            secs = int(m.group(1)) * 60   # angka tanpa satuan dianggap menit
    label = None
    if re.match(r"^(?:ingetin|ingatkan|remind)\b", t):
        rest = re.sub(r"^(?:ingetin|ingatkan|remind(?:\s+me)?)\s*", "", t)
        rest = re.sub(r"^(?:gue|gw|gua|aku|saya|me)\s+", "", rest)
        rest = _DUR_RE.sub(" ", replace_number_words(rest))
        rest = re.sub(r"\b(?:lagi|in|nanti|untuk|to|for)\b", " ", rest)
        label = re.sub(r"\s+", " ", rest).strip() or None
    return Intent("timer", {"seconds": secs, "label": label})


def _r_calendar(t):
    if _STRICT.match(t):
        return None
    verbs = r"(?:tambah(?:in|kan)?|bikin(?:in)?|buat(?:in)?|catat(?:in)?|add|schedule|jadwalin|masukin)"
    m = re.match(rf"^{verbs}\s+(?:acara\s+|event\s+|jadwal\s+|agenda\s+|meeting\s+)?(.+?)\s+"
                 r"((?:besok|lusa|hari\s+ini|nanti|senin|selasa|rabu|kamis|jumat|sabtu|minggu|"
                 r"tomorrow|today|tonight|next\s+\w+|on\s+\w+)\b.*)$", t)
    if m:
        return Intent("calendar_add", {"title": m.group(1), "when": m.group(2)})
    m = re.match(rf"^{verbs}\s+(?:acara|event|jadwal|agenda)\s+(.+)$", t)
    if m:
        return Intent("calendar_add", {"title": m.group(1), "when": None})
    if re.search(r"(?:ada\s+)?(?:jadwal|agenda|acara)\s+apa|\bjadwal\s+(?:hari\s+ini|besok)\b|"
                 r"\bwhat(?:'s|s|\s+is)\s+on\s+my\s+(?:calendar|schedule)\b", t):
        return Intent("calendar_today")


def _r_weather(t):
    if _STRICT.match(t):
        return None
    if re.search(r"\bcuaca\b|\bweather\b|\bforecast\b|\bhujan\s+(?:gak|nggak|ga|ngga|gk|enggak|tidak)\b|"
                 r"\bbakal\s+hujan\b|\bwill\s+it\s+rain\b|\bis\s+it\s+raining\b", t):
        return Intent("weather")


def _r_volume(t):
    if _STRICT.match(t):
        return None
    t2 = replace_number_words(t)
    has_ctx = re.search(r"\b(?:volume\w*|suara\w*)\b", t)
    # nyalakan suara / unmute
    if (re.search(r"\bunmute\b", t)
            or re.search(r"\b(?:suara\w*|volume\w*)\s+(?:nyalain|nyalakan|nyala|hidupin|hidupkan|bunyiin|on)\b", t)
            or re.search(r"\b(?:nyalain|nyalakan|hidupin|hidupkan|bunyiin)\s+(?:suara|volume)\w*", t)):
        return Intent("unmute")
    if (re.search(r"\bmute\b|\bbisu\w*\b|\bsenyap\b", t)
            or re.search(r"\b(?:matiin|matikan)\s+(?:suara|volume)\w*", t)
            or re.search(r"\bsuara\w*\s+(?:mati|off)\b", t)):
        return Intent("mute")
    if re.search(r"\bvolume\w*", t):
        m = re.search(r"\b(\d{1,3})\b", t2)
        if m:
            return Intent("volume_set", {"level": min(100, int(m.group(1)))})
    toks = t.split()
    ctx_or_short = has_ctx or len(toks) <= 3
    step = 5 if re.search(r"\b(?:dikit|sedikit|little|bit)\b", t) else 10
    up = (re.search(r"\b(?:gedein|gedeinin|gedekan|kencengin|kencangin|keraskan|kerasin|naikin|naikkan|"
                    r"besarin|besarkan|louder)\b", t) and ctx_or_short) \
        or re.search(r"\bvolume\w*\s+(?:up|naik|gede|kenceng|keras)\b|\bturn\s+(?:it\s+)?up\b|"
                     r"\b(?:tambah|tambahin)\s+(?:volume|suara)", t)
    if up:
        return Intent("volume_up", {"step": step})
    down = (re.search(r"\b(?:kecilin|kecilkan|pelanin|pelankan|turunin|turunkan|kurangin|kurangi|"
                      r"quieter|softer)\b", t) and ctx_or_short) \
        or re.search(r"\bvolume\w*\s+(?:down|turun|kecil|pelan)\b|\bturn\s+(?:it\s+)?down\b", t)
    if down:
        return Intent("volume_down", {"step": step})


def _r_transport(t):
    if re.match(r"^(?:ulangin|ulangi|ulang|repeat|restart|replay)"
                r"(?:\s+(?:lagunya|lagu|lagu\s+ini|this\s+song|the\s+song|lagi))*$", t) \
            or re.search(r"\bdari\s+awal\b|\bfrom\s+the\s+(?:start|beginning)\b", t) \
            or re.match(r"^(?:puter|putar|putarin|play)\s+ulang$", t):
        return Intent("restart")
    if re.match(r"^(?:go\s+)?(?:mundur|balik|kembali|back|previous|prev|sebelumnya)(?:\s+(?:ke|to))?"
                r"(?:\s+(?:lagu\w*|song|track|tadi|sebelumnya|the\s+previous\s+song|yang\s+tadi))*$", t) \
            or re.match(r"^lagu\s+(?:sebelumnya|tadi|yang\s+tadi|sebelum\s+ini)$", t) \
            or re.match(r"^(?:previous|last)\s+(?:song|track)$", t):
        return Intent("prev")
    if re.match(r"^(?:next|skip|lanjut|lewat\w*|berikutnya|selanjutnya|ganti)"
                r"(?:\s+(?:lagu\w*|song|track|ini|this\s+song|the\s+song|lain|yang\s+lain))*$", t) \
            or re.match(r"^lagu\s+(?:berikutnya|selanjutnya|lain|yang\s+lain)$", t) \
            or (re.search(r"\b(?:gak|nggak|ga|ngga|enggak|ngak|gk)\s+suka\b|\bbosen\b|\bbosan\b", t)
                and not _STRICT.match(t)):
        return Intent("next")
    if re.match(r"^(?:pause|stop|setop|berhenti|hentikan|diem|diam|tahan|jeda|hold\s+on|wait)"
                r"(?:\s+(?:dulu|bentar|sebentar|lagunya|lagu|musiknya|musik|the\s+music|music|song))*$", t):
        return Intent("pause")
    if re.match(r"^(?:resume|unpause|continue|lanjutin|lanjutkan|lanjut\s+(?:puter|putar|lagi|play)|"
                r"mulai\s+lagi|(?:puter|putar|play)\s+(?:lagi|again))"
                r"(?:\s+(?:lagunya|lagu|musiknya|musik|lagi))*$", t) \
            or re.match(r"^(?:play|puter|putar|setel|mainin)$", t):
        return Intent("resume")


def _r_open_app(t):
    m = re.match(r"^(?:buka|bukain|bukakan|open|launch|jalanin|jalankan|run)\s+"
                 r"(?:aplikasi\s+|app\s+|the\s+)?(.+)$", t)
    if m:
        return Intent("open_app", {"name": m.group(1)})


def _r_random(t):
    if re.match(r"^(?:putar|puter|play|setel|mainin)\w*\s+(?:lagu\s+|musik\s+|music\s+)?"
                r"(?:yang\s+enak|yang\s+asik|yang\s+asyik|apa(?:\s+(?:aja|saja))?|random|acak|"
                r"sesuatu|something|anything|apa\s+gitu)$", t):
        return Intent("play_random")


def _r_artist_only(t):
    m = re.match(rf"^{PLAY_VERB}\s+(?:(?:some|something|songs?|lagu(?:nya)?|musik|music|apa)\s+)+"
                 r"(?:by|dari|nya|punya|milik|oleh)\s+(.+)$", t)
    if m:
        full = re.sub(rf"^{PLAY_VERB}\s+", "", t)
        return Intent("play_artist", {"artist": m.group(1), "query_full": _LEAD_WORDS.sub("", full)})


_PLAY_RES = [
    re.compile(r"^(?:(?:aku|gue|gw|gua|saya)\s+)?(?:lagi\s+)?(?:mau|pengen|pingin|pengin|ingin)\s+"
               r"(?:dengerin|denger|dengar|nonton|main|putar|puter|play)\s+(?P<q>.+)$"),
    re.compile(r"^ada\s+lagu\s+(?P<q>.+?)(?:\s+(?:gak|nggak|ga|ngga|gk|enggak))?$"),
    re.compile(r"^ganti\s+(?:lagu\s+)?(?:ke|jadi|dengan|pake|pakai)\s+(?P<q>.+)$"),
    re.compile(rf"^{PLAY_VERB}\s+(?P<q>.+)$"),
    re.compile(r"^lagu\s+(?P<q>.+)$"),
]


def _r_play(t):
    for rx in _PLAY_RES:
        m = rx.match(t)
        if not m:
            continue
        q = _LEAD_WORDS.sub("", m.group("q")).strip()
        if not q or q in _PLAIN_WORDS:
            return Intent("resume")
        m2 = _ARTIST_ONLY.match(q)
        if m2:
            return Intent("play_artist", {"artist": m2.group(1), "query_full": q})
        parts = _SPLIT_ARTIST.split(q, maxsplit=1)
        if len(parts) == 2 and parts[0] and parts[1]:
            return Intent("play", {"query": q, "track": parts[0], "artist": parts[1]})
        return Intent("play", {"query": q})


_RULES = [_r_cancel, _r_time, _r_alarm, _r_pomodoro, _r_timer, _r_calendar, _r_weather,
          _r_volume, _r_transport, _r_open_app, _r_random, _r_artist_only, _r_play]


def parse(text):
    raw = text
    t = normalize(text)
    t = WAKE_RE.sub("", t).strip()
    t = " ".join(_strip_fillers(t.split()))
    t = _english_wrappers(t)
    if not t:
        return Intent("unknown", {"reason": "kosong"}, raw)
    for rule in _RULES:
        result = rule(t)
        if result is not None:
            result.raw = raw
            if result.name in ('timer', 'alarm', 'pomodoro', 'volume_set') and re.search(r'(?:^|\s)[-−]\s*\d|\b(?:minus|negatif|negative)\b', raw.casefold()):
                return Intent('invalid', {'reason': 'Angka negatif tidak diperbolehkan'}, raw)
            return result
    return Intent("unknown", {}, raw)


if __name__ == "__main__":
    for line in sys.argv[1:] or ["puter tulus dong"]:
        print(parse(line))
