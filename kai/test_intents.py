"""Uji parser perintah. Jalankan:  python test_intents.py"""
from intents import parse

# (ucapan, nama intent, args yang harus ada)
CASES = [
    # --- putar lagu / artis
    ("puter tulus", "play", {"query": "tulus"}),
    ("Kai, play Tulus", "play", {"query": "tulus"}),
    ("putar tulus", "play", {"query": "tulus"}),
    ("setel lagu tulus", "play", {"query": "tulus"}),
    ("putarin hati-hati di jalan dong", "play", {"query": "hati hati di jalan"}),
    ("mainin Blinding Lights", "play", {"query": "blinding lights"}),
    ("nyalain lagu Tulus", "play", {"query": "tulus"}),
    ("lagu Tulus dong", "play", {"query": "tulus"}),
    ("cariin lagu Tulus", "play", {"query": "tulus"}),
    ("aku mau dengerin Tulus", "play", {"query": "tulus"}),
    ("pengen dengerin Tulus", "play", {"query": "tulus"}),
    ("dengerin Tulus dong", "play", {"query": "tulus"}),
    ("puter lagunya Tulus", "play", {"query": "tulus"}),
    ("ada lagu Tulus gak?", "play", {"query": "tulus"}),
    ("ganti ke Tulus", "play", {"query": "tulus"}),
    ("ganti lagu ke Tulus", "play", {"query": "tulus"}),
    ("can you play Tulus", "play", {"query": "tulus"}),
    ("I wanna listen to Tulus", "play", {"query": "tulus"}),
    ("play some Taylor Swift", "play", {"query": "taylor swift"}),
    ("play Blinding Lights by The Weeknd", "play",
     {"track": "blinding lights", "artist": "the weeknd"}),
    ("puter hati hati di jalan nya tulus", "play",
     {"track": "hati hati di jalan", "artist": "tulus"}),
    ("putar lagu dari Tulus", "play_artist", {"artist": "tulus"}),
    ("play something by Taylor Swift", "play_artist", {"artist": "taylor swift"}),
    ("putar yang enak dong", "play_random", {}),
    ("play something", "play_random", {}),
    ("putar lagu", "resume", {}),
    # --- ganti lagu
    ("next", "next", {}),
    ("skip", "next", {}),
    ("lanjut", "next", {}),
    ("ganti lagu", "next", {}),
    ("lagu berikutnya", "next", {}),
    ("lagu selanjutnya", "next", {}),
    ("lewatin aja", "next", {}),
    ("gak suka ah, ganti", "next", {}),
    ("skip this song", "next", {}),
    ("next song please", "next", {}),
    # --- mundur / ulang
    ("mundur", "prev", {}),
    ("balik", "prev", {}),
    ("lagu sebelumnya", "prev", {}),
    ("previous", "prev", {}),
    ("back", "prev", {}),
    ("ulangin lagunya", "restart", {}),
    ("puter dari awal", "restart", {}),
    # --- jeda / lanjut
    ("pause", "pause", {}),
    ("stop dulu", "pause", {}),
    ("diem dulu", "pause", {}),
    ("berhenti", "pause", {}),
    ("hold on", "pause", {}),
    ("lanjutin", "resume", {}),
    ("mulai lagi", "resume", {}),
    ("resume", "resume", {}),
    ("puter lagi", "resume", {}),
    ("play", "resume", {}),
    # --- volume
    ("volume 40", "volume_set", {"level": 40}),
    ("volumenya 40 aja", "volume_set", {"level": 40}),
    ("volume empat puluh", "volume_set", {"level": 40}),
    ("set volume to 40", "volume_set", {"level": 40}),
    ("gedein volume", "volume_up", {"step": 10}),
    ("kencengin dong", "volume_up", {}),
    ("naikin volumenya", "volume_up", {}),
    ("turn it up", "volume_up", {}),
    ("kecilin dikit", "volume_down", {"step": 5}),
    ("pelanin volumenya", "volume_down", {}),
    ("turn it down", "volume_down", {}),
    ("mute", "mute", {}),
    ("bisu", "mute", {}),
    ("unmute", "unmute", {}),
    ("suaranya nyalain", "unmute", {}),
    # --- timer, alarm, pomodoro
    ("timer 25 menit", "timer", {"seconds": 1500}),
    ("timer dua puluh lima menit", "timer", {"seconds": 1500}),
    ("timer 1 jam 30 menit", "timer", {"seconds": 5400}),
    ("timer setengah jam", "timer", {"seconds": 1800}),
    ("ingetin 10 menit lagi", "timer", {"seconds": 600}),
    ("ingetin gue minum obat 10 menit lagi", "timer", {"seconds": 600, "label": "minum obat"}),
    ("set a timer for 5 minutes", "timer", {"seconds": 300}),
    ("alarm jam 6 pagi", "alarm", {"hour": 6, "minute": 0}),
    ("bangunin jam 5", "alarm", {"hour": 5, "minute": 0}),
    ("bangunin jam enam", "alarm", {"hour": 6, "minute": 0}),
    ("pasang alarm jam setengah 7 pagi", "alarm", {"hour": 6, "minute": 30}),
    ("alarm jam 8 malam", "alarm", {"hour": 20, "minute": 0}),
    ("alarm jam 6 kurang 10", "alarm", {"hour": 5, "minute": 50}),
    ("set alarm for 6 am", "alarm", {"hour": 6, "minute": 0}),
    ("alarm jam 6.30", "alarm", {"hour": 6, "minute": 30}),
    ("mulai pomodoro", "pomodoro", {"seconds": 1500}),
    ("fokus 45 menit", "pomodoro", {"seconds": 2700}),
    ("batalin alarm", "cancel", {"kind": "alarm"}),
    ("cancel the timer", "cancel", {"kind": "timer"}),
    # --- lain-lain
    ("buka vscode", "open_app", {"name": "vscode"}),
    ("open chrome", "open_app", {"name": "chrome"}),
    ("jam berapa sekarang", "time_now", {}),
    ("what time is it", "time_now", {}),
    ("cuaca hari ini", "weather", {}),
    ("tambah rapat besok jam 10", "calendar_add", {"title": "rapat", "when": "besok jam 10"}),
    ("hari ini ada jadwal apa", "calendar_today", {}),
    # --- tidak boleh salah tangkap
    ("puter dua lipa", "play", {"query": "dua lipa"}),
    ("play one dance", "play", {"query": "one dance"}),
    ("puter bang bang", "play", {"query": "bang bang"}),
    ("asdfgh qwerty", "unknown", {}),
]


def main():
    fails = 0
    for text, name, args in CASES:
        got = parse(text)
        ok = got.name == name and all(got.args.get(k) == v for k, v in args.items())
        if not ok:
            fails += 1
            print(f"GAGAL: {text!r}\n   harapan: {name} {args}\n   hasil:   {got.name} {got.args}")
    print(f"{len(CASES) - fails}/{len(CASES)} lulus")
    raise SystemExit(1 if fails else 0)


if __name__ == "__main__":
    main()
