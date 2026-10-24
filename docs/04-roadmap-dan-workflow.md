# Roadmap dan workflow

Status terbaru: versi lokal mencakup M1 serta implementasi desktop M2–M6; M4 suara kemudian dinonaktifkan atas pilihan pengguna; pengujian akun/audio/perangkat fisik masih terbuka. M7 memerlukan identitas paket Windows; M8 blur native/installer/fitur opsional belum selesai. Bukti terperinci dan batas tersedia di 07. M1 diuji pada Windows, scaling 150%. Ukuran compact dan material gelap transparan sudah direvisi sesuai pengguna; blur native masih terbuka. Seluruh tahap asli dipertahankan. Bagian urutan di bawah berasal dari perencanaan awal; lihat 07 untuk bukti implementasi terbaru.

## Milestone dan syarat selesai

| Milestone | Tahap sumber | Pekerjaan | Bukti yang harus ada |
| --- | --- | --- | --- |
| M0 — Baseline | Sebelum 1 | Inventaris sumber/ZIP, perangkat, parser dan gap | Sudah: sembilan berkas, 98/98 parser, spesifikasi lokal; detail di 07 |
| M1 — Island demo | 1 | Sudah: pil compact, hover, collapse 700 ms, jam/tanggal, popup, tray, reduced motion | 8 tes UI dan native smoke DPR 1,5 lulus; monitor/DPI lain belum diuji |
| M2 — Musik | 2 | SMTC session, metadata/cover, prev/pause/next, posisi | Spotify desktop nyata; tanpa media, pause, session berganti, judul panjang |
| M3 — Volume/perangkat | 3 | Callback volume/mute, kartu, headset connect/disconnect | Slider/tombol fisik, ganti output, deduplikasi event |
| M4 — Suara stabil | 4 | PTT lifecycle, stop limit, worker tunggal, Whisper, CPU fallback, hasil di island | Rekaman Indonesia/Inggris/campuran dan hotkey release diuji; log latency |
| M5 — Waktu tersimpan | 5 | Penjadwal persisten, kartu alarm/timer, pause/cancel, restore; fondasi kalender | Restart/sleep/resume dan deadline terlewat; keputusan kalender dicatat |
| M6a — Fokus | 6 | Pomodoro dengan statistik SQLite; siklus/istirahat sesuai keputusan | Fokus/pause/selesai, statistik tidak dobel setelah restart |
| M6b — Panel sistem | 6 | CPU/RAM/disk/baterai; GPU/suhu jika sensor mendukung | Data valid dan unavailable state, polling panel tersembunyi |
| M6c — Cuaca/agenda | 6 + kalender 5 | Lokasi, cache cuaca, impor `.ics`, baca agenda/tambah acara sesuai keputusan | Offline/stale, zona waktu, recurrence, tidak ada duplikasi |
| M6d — Lirik/shelf | 6 | Lirik sinkron; file shelf dengan semantik yang dipilih | Seek/track berubah; file hilang/drop/buka/dismiss |
| M7 — Notifikasi | 7 | Spike manifest/izin; filter WhatsApp; kartu tampil saja | Denied/revoked, pesan panjang, privasi, tidak ada aksi WhatsApp tidak resmi |
| M8 — Poles | 8 | Acrylic, tema/accent, aksesibilitas, packaging; wake word/TTS opsional | Performa terukur, fallback solid, uji perangkat nyata, demo portofolio |

M4 ditunda/nonaktif atas pilihan terbaru pengguna; kode PTT dan worker on-demand disimpan, dengan tes lifecycle tiruan. Default terbaru memprioritaskan 20–30 MiB privat idle dan layanan media/audio on demand. Pemeriksaan STT secara terpisah boleh dilakukan lebih awal untuk mengurangi risiko, tanpa menunggu seluruh M2/M3. Wake word tetap akhir. Urutan M6 dapat dipilih berdasarkan manfaat pengguna, tanpa menghapus fitur lain.

## Workflow setiap milestone

1. Baca status dan keputusan terbaru; telusuri fungsi yang sudah ada sebelum menambah berkas/dependensi.
2. Pilih satu keluaran yang dapat diamati, contoh: “kursor pergi 700 ms → pil mengecil tanpa kehilangan klik aplikasi”.
3. Tuliskan acceptance singkat dan pilih pengujian yang dapat membuktikannya. Gunakan tes parser yang ada untuk regresi; tes tambahan hanya untuk logika yang bermakna.
4. Implementasikan jalur minimum lengkap; gunakan data tiruan untuk UI sebelum API/mikrofon.
5. Uji gagal, kosong, dan transisi cepat selain happy path. Pada integrasi OS, tes unit saja tidak cukup.
6. Perbarui 07 dengan perintah, tanggal, hasil dan keterbatasan; perbarui 06 bila pengguna memutuskan perilaku.
7. Catat progres nyata. Buat ZIP rilis hanya dari source/runtime yang diperlukan, tanpa token, database pribadi, venv, atau model.

## Pekerjaan pertama yang konkret

Setelah arahan desain ditinjau: tambahkan PySide6 ke environment terisolasi, bangun `island.py` minimum, hubungkan opsi `--island --demo` ke main, dan gunakan event tiruan. Opsi ini belum ada sekarang. Jangan menjalankan contoh dari dokumen asli sebagai perintah yang sudah valid.

Setelah demo lulus, hubungkan bus event melalui signal Qt, lalu integrasi satu per satu. Pertahankan CLI `--text --dry` untuk menguji parser tanpa efek samping. Jangan membuat ulang parser yang sudah bekerja.

## Catatan portofolio dan waktu

Simpan bukti demo alur idle → hover → media → PTT → hasil serta ringkasan keputusan dan pengukuran resource. Screenshot saja tidak membuktikan integrasi. Estimasi sumber 1–2 minggu belum dapat dikonfirmasi sebelum M1 dan benchmark suara selesai; jangan menjanjikan seluruh delapan tahap dalam rentang tersebut.
