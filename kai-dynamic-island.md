# Kai Dynamic Island untuk Windows

Satu dokumen untuk seluruh ide dan rencana, dari awal sampai akhir. Anggaran Rp0, semua alat gratis dan open source. Terakhir diperbarui 22 Oktober 2026.

---

## 1. Ide Utama

Membuat **dynamic island di Windows** bertema **liquid glass** yang menyesuaikan tema laptop, dengan asisten suara lokal bernama **Kai**.

- **Island**: jendela kecil di tengah atas layar yang membesar dan mengecil sesuai kejadian (lagu, volume, headset, notifikasi, jam).
- **Kai**: "otak suara". Tahan **Ctrl+Space**, bicara (Indonesia atau Inggris), lepas. Kai memahami perintah lalu menjalankannya dan hasilnya tampil di island.

---

## 2. Perilaku Island

| Keadaan | Perilaku |
|---|---|
| Diam (tidak dipakai) | Hanya **pil hitam kecil** di tengah atas layar. Tidak menghalangi klik ke jendela di bawahnya. |
| Kursor didekatkan | Kursor di area tengah atas layar membuat island **membesar penuh** dengan animasi halus. |
| Kursor menjauh | Setelah sekitar 0,7 detik island **mengecil lagi** ke pil hitam. |
| Kai bekerja / ada kejadian | Island membesar sendiri sebentar (mendengarkan, hasil perintah, timer selesai), lalu mengecil kembali. |

Ukuran, kecepatan animasi, dan jeda bisa diubah lewat konstanta di `island.py`.

---

## 3. Gambaran Fitur (referensi tampilan, bukan patokan desain)

Gambar referensi berisi 17 keadaan. Dipakai sebagai gambaran isi, bukan desain yang ditiru. Pemetaannya:

| No | Keadaan | Sumber data | Tahap |
|---|---|---|---|
| 1-3 | Pil kecil, membesar saat kursor mendekat, mengecil lagi | Posisi kursor | 1 (sudah ditulis, belum diuji) |
| 4 | Tampilan default: jam, tanggal, ikon ringkas | Waktu sistem | 1 (jam dan tanggal saja) |
| 5 | Kontrol Spotify: cover, judul, artis, prev/pause/next | Windows SMTC (`winsdk`) | 2 |
| 6 | Volume (bar dan persen) | Windows Core Audio (`pycaw`) | 3 |
| 7 | Notifikasi WhatsApp (tampil saja) | Windows UserNotificationListener | 7 |
| 8 | Headset/Bluetooth tersambung | Event perangkat Windows | 3 |
| 9 | Kai mendengarkan (Ctrl+Space) | Kai | 1 (teks, tanpa gelombang suara) |
| 10 | Hasil perintah Kai | Kai | 1 (teks) |
| 11 | Lirik real-time | LRCLIB + posisi lagu dari SMTC | 6 |
| 12 | Monitor sistem (CPU, RAM, GPU, suhu, baterai, disk) | LibreHardwareMonitor / `psutil` | 6 |
| 13 | Cuaca dan jadwal | Open-Meteo + file `.ics` | 6 |
| 14 | Pomodoro | Timer lokal + SQLite | 6 (logika sudah ada) |
| 15 | File shelf (drag and drop) | Drag-drop bawaan | 6 |
| 16-17 | Alarm dan timer | Penjadwal buatan sendiri | 5 (logika sudah ada, kartunya belum) |

Urutan saran setelah island dasar: **5, 6, 8** (musik, volume, headset), karena datanya paling mudah diambil dari Windows dan paling sering terlihat.

Catatan gaya tampilan: efek liquid glass sungguhan (pembiasan cahaya) tidak ada bawaan di Windows. Target yang realistis: Acrylic/Mica (blur) + gradasi tipis + tepi terang + bayangan lembut + animasi halus, dengan warna mengikuti mode gelap/terang dan warna aksen Windows. Versi awal memakai kaca buatan (digambar), blur sungguhan masuk di tahap poles.

---

## 4. Cara Kerja Kai

```
Tahan Ctrl+Space
      |
  Rekam suara
      |
  Speech-to-text (Whisper lokal)
      |
  Teks perintah
      |
  Pemahaman maksud: pola kalimat + fuzzy matching (tanpa LLM)
      |
  Eksekusi (Spotify / volume / timer / alarm / buka aplikasi)
      |
  Island menampilkan hasil
```

### Keputusan
- **Push-to-talk Ctrl+Space.** Handy tidak dipakai lagi, jadi tombol tidak bentrok. Pastikan Handy tidak berjalan otomatis saat Windows menyala. Ctrl+Space tetap diteruskan ke aplikasi yang sedang aktif (misalnya autocomplete di editor kode). Tombol bisa diganti di `config.py`. Wake word "Kai" ditunda ke tahap akhir.
- **Satu model: Whisper** dengan deteksi bahasa otomatis, sehingga perintah Indonesia dan Inggris sama-sama dimengerti. Deteksi memilih antara Indonesia dan Inggris, dan hasil "Melayu" (yang sering salah tebak untuk ucapan Indonesia) digabung ke Indonesia.
- **Model dipilih otomatis**: GPU NVIDIA terdeteksi → Whisper Medium, hanya CPU → Whisper Small. Spesifikasi laptop belum diketahui, jadi ukuran perlu dicek dari waktu proses yang ditampilkan Kai.
- **Model Handy tidak dipakai ulang.** Kai memakai `faster-whisper` yang mengunduh modelnya sendiri (Small sekitar 0,5 GB, Medium sekitar 1,5 GB). File Handy berformat ggml dan terlalu rawan gagal dimuat di Windows.
- **Nemotron tidak dipakai.** Berdasarkan diskusi di halaman Hugging Face-nya, bahasa Indonesia kemungkinan belum didukung. Bisa dites sendiri di Handy. Kelebihannya hanya teks streaming.
- **Tanpa Ollama / LLM lokal** karena terlalu berat.
- **Spotify Premium: ya.** Memutar lagu tertentu lewat Spotify Web API (login PKCE, hanya butuh Client ID, tanpa secret). Perintah next/prev/pause tetap punya cadangan lewat tombol media Windows. Aturan API Spotify bisa berubah, jadi dicek ulang saat setup.

---

## 5. Pola Kalimat Perintah (58 pola, bahasa sehari-hari)

`{lagu}`, `{artis}`, `{n}`, `{app}` adalah bagian yang berubah-ubah. Semua perintah boleh diawali "Kai" dan ditambah kata pengisi (dong, deh, ya, kak, tolong, please, aja, sih).

### A. Memutar lagu atau artis
1. puter {lagu}
2. putar {lagu}
3. play {lagu}
4. setel {lagu}
5. putarin {lagu} dong
6. mainin {lagu}
7. nyalain {lagu}
8. lagu {lagu} dong
9. cariin lagu {lagu}
10. aku mau dengerin {lagu}
11. pengen dengerin {artis}
12. dengerin {artis} dong
13. puter lagunya {artis}
14. putar lagu dari {artis}
15. play {lagu} by {artis}
16. puter {lagu} nya {artis}
17. play something by {artis}
18. play some {artis}
19. putar yang enak dong (acak dari lagu yang disukai)

### B. Ganti lagu
20. next
21. skip
22. lanjut
23. ganti lagu
24. ganti ke {lagu}
25. lagu berikutnya / lagu selanjutnya
26. lewatin aja
27. gak suka ah, ganti
28. skip this song

### C. Mundur atau ulang
29. mundur
30. balik
31. lagu sebelumnya
32. back / previous
33. ulangin lagunya
34. puter dari awal

### D. Jeda dan lanjut
35. pause
36. stop dulu
37. diem dulu
38. berhenti
39. lanjutin
40. mulai lagi / resume

### E. Volume
41. volume {n}
42. volumenya {n} aja
43. gedein / kencengin / naikin volume
44. kecilin / pelanin / turunin volume
45. mute / bisu
46. unmute / suaranya nyalain
47. turn it up / turn it down

### F. Timer, alarm, pomodoro
48. timer {n} menit
49. ingetin {n} menit lagi
50. alarm jam {n} / bangunin jam {n}
51. set a timer for {n} minutes
52. mulai pomodoro / fokus {n} menit
53. batalin alarm / batalin timer

### G. Lain-lain
54. buka {app}
55. jam berapa sekarang / what time is it
56. cuaca hari ini
57. tambah rapat besok jam {n}
58. hari ini ada jadwal apa

### Aturan pencocokan
1. Huruf kecil, buang tanda baca, buang awalan "Kai" dan kata pengisi di awal/akhir kalimat (bukan di tengah, supaya judul lagu aman).
2. Variasi kata kerja (puter/putar/putarin/mainin/play/setel/nyalain) dianggap satu aksi.
3. Teks setelah kata kerja = kueri lagu atau artis. Kata pemisah "by", "dari", "nya" memecahnya jadi lagu dan artis. Kalau pecahannya salah (judul yang memang berisi "dari"), pencarian utuh dipakai sebagai cadangan.
4. Kalimat yang tidak cocok pola mana pun tidak ditebak: island menampilkan teks yang terdengar.
5. Fuzzy matching (`rapidfuzz`) untuk nama artis dan aplikasi yang salah dengar.
6. Whisper diberi petunjuk awal berisi nama artis dan lagu favorit (`HINT_NAMES` di `config.py`, isi saat ini hanya contoh).
7. Angka boleh berupa kata atau digit ("empat puluh", "40"), hanya diubah di perintah yang butuh angka, supaya judul seperti "Dua Lipa" atau "One Dance" tidak rusak.
8. Perintah dengan efek besar (hapus, batalkan) minta konfirmasi singkat. Pada versi 1, "batalin alarm/timer" langsung dijalankan.

---

## 6. Teknologi

| Bagian | Pilihan | Alasan |
|---|---|---|
| Kai (suara dan perintah) | Python: `faster-whisper`, `sounddevice`, `keyboard`, `rapidfuzz`, `spotipy`, `pycaw` | Ekosistem suara paling lengkap di Python. |
| Island (versi awal) | Python + PySide6 | Satu bahasa dengan Kai, cepat jadi prototipe. |
| Island (versi lanjut, opsional) | C# + WPF-UI (lepoco/wpfui) | Akses langsung ke SMTC, notifikasi, Acrylic/Mica, halus dan ringan. Kai tetap Python dan mengirim kejadian lewat WebSocket/named pipe lokal. |

Semua berjalan **offline** di laptop (kecuali Spotify dan unduhan model pertama), tanpa API berbayar, dan audio tidak dikirim ke luar.

---

## 7. Tahapan Pengerjaan

| Tahap | Isi | Status |
|---|---|---|
| 1 | Island dasar: pil hitam, hover membesar, jam, status Kai | Ditulis, **belum diuji** |
| 2 | Kontrol media: cover, judul, artis, prev/pause/next lewat SMTC | Belum |
| 3 | Volume dan indikator headset/Bluetooth | Volume (perintah suara) ditulis, tampilan belum |
| 4 | Kai push-to-talk: Ctrl+Space → Whisper → perintah | Ditulis, **belum diuji di Windows** |
| 5 | Alarm, timer, kalender (kartu di island, simpan ke file agar tahan restart) | Logika alarm/timer ada, kalender belum |
| 6 | Fitur tambahan: lirik, monitor sistem, pomodoro, cuaca/jadwal, file shelf | Belum |
| 7 | Notifikasi WhatsApp (baca toast Windows, tampil saja) | Belum |
| 8 | Poles: blur Acrylic, animasi, ikuti tema Windows, wake word "Kai" (openWakeWord), suara balasan opsional (Piper/SAPI) | Belum |

Urutan sengaja bertahap. Kalau wake word dibuat paling awal, sulit diketahui masalahnya ada di wake word, transkripsi, atau perintah.

---

## 8. Fitur Tambahan (semua gratis)

1. **Lirik real-time**: LRCLIB (lrclib.net), memakai judul, artis, dan posisi lagu dari SMTC.
2. **Monitor sistem**: LibreHardwareMonitor (C#) atau `psutil` (Python).
3. **Cuaca dan jadwal**: Open-Meteo dan file `.ics` (diekspor dari Google Calendar).
4. **Pomodoro dan statistik belajar**: timer lokal dan SQLite.
5. **File shelf**: drag and drop file ke island sebagai tempat singgah sementara.

---

## 9. Risiko dan Penanganan

| Risiko | Penanganan |
|---|---|
| Notifikasi WhatsApp terbatas (hanya tampil, butuh izin akses notifikasi) | Dikerjakan paling akhir. Jangan pakai library WhatsApp tidak resmi: melanggar ketentuan dan akun bisa diblokir. |
| Liquid glass sungguhan tidak ada bawaan di Windows | Target: efek yang mirip (Acrylic + gradasi + tepi terang + animasi). |
| Akurasi bahasa campuran (nama lagu Inggris di kalimat Indonesia) | Perintah pendek dan terstruktur, petunjuk nama untuk Whisper, fuzzy matching. |
| Whisper Medium lambat di CPU | Kai otomatis memakai Small di CPU. Waktu proses ditampilkan tiap ucapan. |
| Alarm dan timer hilang kalau Kai ditutup atau laptop tidur | Simpan ke file dan pulihkan saat Kai menyala (tahap 5). |
| Wake word "Kai" mudah terpicu salah | Ctrl+Space jalur utama. Wake word menyusul. |
| Aturan API Spotify bisa berubah | Dicek ulang saat setup. Cadangan: tombol media Windows. |
| Status proyek open source bisa berubah | Cek tanggal commit, lisensi (MIT/MPL/Apache aman), pasang hanya lewat PyPI/NuGet resmi. |
| Privasi mikrofon | Semua lokal. Island menampilkan status "Mendengarkan..." saat mikrofon aktif. |

---

## 10. Alat Open Source

- `faster-whisper`: speech-to-text lokal.
- `sounddevice`, `keyboard`: rekam suara dan tombol global.
- `rapidfuzz`: pencocokan teks yang toleran salah dengar.
- `spotipy`: Spotify Web API.
- `pycaw` / `comtypes`: volume Windows.
- `PySide6`: jendela island.
- `winsdk`: SMTC dan API Windows lain (tahap 2).
- **LRCLIB**: lirik berbaris waktu.
- **LibreHardwareMonitor** / `psutil`: suhu dan beban perangkat.
- **Open-Meteo**: cuaca tanpa API key.
- **Ical.Net** / `icalendar`: file `.ics`.
- **WPF-UI**: komponen bergaya Windows 11 (jika island dipindah ke C#).
- **openWakeWord**: kata panggil "Kai" (tahap 8).
- **Piper**: suara balasan lokal (opsional).

---

## 11. Status Pekerjaan Saat Ini

**Sudah ada (kode, kerangka v1):**
- `intents.py`: pemahaman 58 pola kalimat. **Sudah diuji: 98 dari 98 contoh lulus** (`test_intents.py`).
- `stt.py`, `actions.py`, `main.py`, `config.py`, `events.py`, `README.md`: Ctrl+Space, Whisper dengan deteksi GPU otomatis, Spotify Premium, volume, timer, alarm, pomodoro, buka aplikasi. **Belum pernah dijalankan di Windows.**
- `island.py`: pil hitam, hover membesar, mengecil lagi, status Kai. **Belum diuji sama sekali.** Belum masuk ke `kai.zip` yang sudah dikirim.

**Belum:** tampilan kartu (musik, volume, headset, notifikasi, dan seterusnya), cuaca dan kalender, penyimpanan alarm, blur Acrylic, wake word.

**Langkah berikutnya:**
1. Uji `island.py` (animasi buka/tutup), lalu perbarui `kai.zip` dengan island.
2. Coba di laptop: `python main.py --island --demo`, lalu `python main.py --island`.
3. Tahap 2: kartu musik dengan cover lewat SMTC.
4. Tahap 3: kartu volume dan headset.

**Yang masih dibutuhkan dari Anda:** spesifikasi laptop (RAM, ada GPU atau tidak), dan hasil percobaan pertama (pesan error kalau ada).

---

## 12. Manfaat untuk Portofolio

Proyek ini menunjukkan integrasi API sistem operasi, pengolahan suara, desain UI, dan arsitektur beberapa proses. Cocok untuk CV magang. Estimasi versi dasar yang stabil: 1 sampai 2 minggu sambil kuliah.
