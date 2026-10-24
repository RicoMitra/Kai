# Kontrak 58 pola perintah

> Cakupan aktif 0.3.0: lihat [16](16-kai-productivity.md). Clipboard/Command/Notes/Smart Shelf/Musik/Sistem; jam dan logo tetap. Fokus/Agenda/Waktu/Cuaca di bawah adalah arsip sumber, bukan fitur runtime aktif.

> Pembaruan 22 Oktober 2026: Mode suara kini nonaktif. Kontrak parser di bawah tetap tersedia melalui kolom perintah teks/CLI; bukan janji pengenalan ucapan aktif.

Seluruh nomor pola sumber dipertahankan. Tabel adalah cakupan target; keberhasilan parser berbeda dari keberhasilan handler/API. `{lagu}`, `{artis}`, `{n}`, `{app}` adalah slot, bukan teks literal.

| No | Pola sumber | Intent/aksi target |
| --- | --- | --- |
| 1 | puter {lagu} | play |
| 2 | putar {lagu} | play |
| 3 | play {lagu} | play |
| 4 | setel {lagu} | play |
| 5 | putarin {lagu} dong | play |
| 6 | mainin {lagu} | play |
| 7 | nyalain {lagu} | play |
| 8 | lagu {lagu} dong | play |
| 9 | cariin lagu {lagu} | play |
| 10 | aku mau dengerin {lagu} | play |
| 11 | pengen dengerin {artis} | Pencarian play; cocokkan artis di handler |
| 12 | dengerin {artis} dong | Pencarian play; cocokkan artis di handler |
| 13 | puter lagunya {artis} | Pencarian play; cocokkan artis di handler |
| 14 | putar lagu dari {artis} | play_artist |
| 15 | play {lagu} by {artis} | play dengan track dan artist |
| 16 | puter {lagu} nya {artis} | play dengan track dan artist |
| 17 | play something by {artis} | play_artist |
| 18 | play some {artis} | Pencarian play; cocokkan artis di handler |
| 19 | putar yang enak dong | play_random dari lagu disukai |
| 20 | next | next |
| 21 | skip | next |
| 22 | lanjut | next, sesuai baseline; bukan resume |
| 23 | ganti lagu | next |
| 24 | ganti ke {lagu} | play |
| 25 | lagu berikutnya / lagu selanjutnya | next |
| 26 | lewatin aja | next |
| 27 | gak suka ah, ganti | next |
| 28 | skip this song | next |
| 29 | mundur | prev |
| 30 | balik | prev |
| 31 | lagu sebelumnya | prev |
| 32 | back / previous | prev |
| 33 | ulangin lagunya | restart dari posisi 0 |
| 34 | puter dari awal | restart |
| 35 | pause | pause |
| 36 | stop dulu | pause |
| 37 | diem dulu | pause |
| 38 | berhenti | pause |
| 39 | lanjutin | resume |
| 40 | mulai lagi / resume | resume |
| 41 | volume {n} | volume_set, 0–100 |
| 42 | volumenya {n} aja | volume_set |
| 43 | gedein / kencengin / naikin volume | volume_up |
| 44 | kecilin / pelanin / turunin volume | volume_down |
| 45 | mute / bisu | mute |
| 46 | unmute / suaranya nyalain | unmute |
| 47 | turn it up / turn it down | volume_up / volume_down |
| 48 | timer {n} menit | timer |
| 49 | ingetin {n} menit lagi | timer; label jika disebut |
| 50 | alarm jam {n} / bangunin jam {n} | alarm |
| 51 | set a timer for {n} minutes | timer |
| 52 | mulai pomodoro / fokus {n} menit | pomodoro |
| 53 | batalin alarm / batalin timer | cancel jenis terkait |
| 54 | buka {app} | open_app melalui allowlist |
| 55 | jam berapa sekarang / what time is it | time_now |
| 56 | cuaca hari ini | weather; handler belum dibuat |
| 57 | tambah rapat besok jam {n} | calendar_add; handler belum dibuat |
| 58 | hari ini ada jadwal apa | calendar_today; handler belum dibuat |

## Delapan aturan sumber

1. Lowercase dan normalisasi tanda baca; buang awalan Kai serta filler di awal/akhir saja. Pertahankan judul di tengah kalimat. Perbaikan diperlukan untuk tanda negatif/desimal sebelum normalisasi merusaknya.
2. Varian puter/putar/putarin/mainin/play/setel/nyalain dipetakan ke aksi setara; parser tetap membedakan timer/volume dan lagu.
3. Sesudah kata kerja menjadi query. Pisah `by`, `dari`, `nya` untuk track/artist; jika salah pisah, cari query utuh sebagai fallback.
4. Tidak cocok → unknown dan tampilkan teks yang terdengar; jangan menebak aksi baru.
5. Rapidfuzz untuk artis/aplikasi salah dengar; allowlist aplikasi wajib. Skor bukan jaminan identitas.
6. `HINT_NAMES` membantu ejaan STT; nama sekarang hanyalah contoh, minta preferensi saat setup.
7. Angka kata/digit hanya dikonversi dalam konteks numerik. “Dua Lipa” dan “One Dance” tetap query lagu/artis.
8. Efek besar memerlukan konfirmasi singkat, dengan pengecualian sumber v1: batal timer/alarm langsung. Tidak ada perintah menghapus berkas yang ditambahkan.

## Perilaku baseline tambahan

Volume naik/turun umumnya 10, “dikit” 5. Pomodoro tanpa durasi menjadi 25 menit. Timer tanpa satuan numerik diasumsikan menit. Alarm yang waktunya sudah lewat dijadwalkan esok hari oleh handler. Nilai ini ditemukan dalam kode, bukan pilihan pengguna baru.

Baseline punya variasi bahasa lebih luas daripada 58 pola, tetapi hanya 98 contoh yang saat ini diuji. Tambahkan pemeriksaan bermakna untuk jam invalid, minus, desimal dan kalimat ambigu sebelum memperluas parser. Jangan mengganti regex dengan LLM untuk menyelesaikan masalah validasi ini.
