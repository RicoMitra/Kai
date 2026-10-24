# Kebutuhan dan cakupan

> Cakupan aktif 0.3.0: lihat [16](16-kai-productivity.md). Clipboard/Command/Notes/Smart Shelf/Musik/Sistem; jam dan logo tetap. Fokus/Agenda/Waktu/Cuaca di bawah adalah arsip sumber, bukan fitur runtime aktif.

> Pembaruan 22 Oktober 2026: Keputusan terbaru: mode suara dinonaktifkan; kebutuhan suara di bawah adalah sumber/backlog, bukan perilaku versi aktif. Media/audio hanya saat tab dibuka sesuai persetujuan demi RAM privat idle 20–30 MiB.

## Tujuan produk

Kai adalah island kecil di tengah atas layar Windows, mengikuti tema laptop dan membuka informasi sesuai konteks. Asisten suara memakai tahan Ctrl+Space → rekam → lepas → Whisper lokal → intent berbasis pola/fuzzy → aksi → hasil di island. Bahasa Indonesia dan Inggris; hasil deteksi Melayu diperlakukan sebagai Indonesia. Suara balasan dan wake word menyusul.

Biaya tambahan Rp0, alat gratis/open source, tanpa API berbayar. Spotify Premium disebut sudah tersedia. Audio tidak keluar laptop. Kata “offline” berlaku pada inti STT, parser, waktu, timer, dan kontrol sistem; Spotify, unduhan model, pencarian lirik, serta cuaca memerlukan jaringan. Cache tidak membuat data daring selalu mutakhir.

## Perilaku wajib dari sumber

1. Idle: pil hitam kecil yang tidak menghalangi klik ke aplikasi di bawah.
2. Kursor mendekati area atas tengah: island membesar halus.
3. Kursor menjauh: kembali kecil setelah sekitar 0,7 detik. Ini baseline sumber; teks 1–2 detik pada gambar adalah ilustrasi.
4. Mendengarkan, hasil perintah, dan kejadian penting dapat membuka island otomatis sebentar.
5. Ukuran, kecepatan animasi, dan jeda dapat diatur. Sumber menyebut konstanta `island.py`; usulan konfigurasi terpusat dibahas di arsitektur.
6. Ctrl+Space tetap diteruskan ke aplikasi aktif; hotkey dapat diganti di `config.py`. Handy tidak dipakai sebagai komponen Kai; status autostart Handy perlu diperiksa saat setup.
7. Model auto: NVIDIA → Medium; CPU → Small. Unduhan awal diperkirakan sumber sekitar 1,5 GB/0,5 GB, bukan ukuran unduhan yang sudah diukur. Waktu proses ditampilkan.

## Cakupan seluruh keadaan UI

| ID | Referensi | Isi dan interaksi target | Data | Tahap sumber | Status faktual |
| --- | --- | --- | --- | --- | --- |
| UI01 | 1 | Pil idle hitam | State lokal | 1 | UI tidak ada di ZIP |
| UI02 | 2 | Expand saat kursor mendekat | Posisi kursor | 1 | Belum ada |
| UI03 | 3 | Collapse setelah kursor pergi | Delay | 1 | Belum ada |
| UI04 | 4 | Jam, tanggal; ikon ringkas bertahap | Waktu sistem | 1 | Aksi waktu berupa teks ada |
| UI05 | 5 | Cover, judul, artis, prev/pause/next, progres | SMTC | 2 | Aksi Spotify ada; SMTC/kartu belum |
| UI06 | 6 | Volume bar, persen, mute | Core Audio/pycaw | 3 | Aksi ada; listener/kartu belum |
| UI07 | 7 | Toast WhatsApp tampil saja, dismiss kartu | UserNotificationListener | 7 | Belum; akses dan packaging perlu spike |
| UI08 | 8 | Nama headset/Bluetooth dan status sambungan | Event perangkat | 3 | Belum |
| UI09 | 9 | Status mendengarkan; waveform opsional sesudah teks | Mikrofon/Kai | 1, 4 | Event teks ada; UI belum |
| UI10 | 10 | Hasil perintah, sukses/error, detail waktu relevan | Action result | 1, 4 | Output console ada; UI belum |
| UI11 | 11 | Lirik sinkron posisi lagu, opsional | LRCLIB + SMTC | 6 | Belum |
| UI12 | 12 | CPU, RAM, GPU, suhu, baterai, penyimpanan | psutil/LHM | 6 | Belum; sensor dapat tidak tersedia |
| UI13 | 13 | Cuaca dan agenda hari ini | Open-Meteo + `.ics` | 6 | Intent ada; handler placeholder |
| UI14 | 14 | Fokus, sisa waktu, siklus/istirahat, statistik | Penjadwal + SQLite | 6 | Timer fokus tunggal ada; siklus/statistik belum |
| UI15 | 15 | Drop file, daftar singgah, buka/keluarkan item | Drag/drop lokal | 6 | Belum; semantik file perlu pilihan |
| UI16 | 16 | Alarm aktif, jam, enable/disable; recurrence jika dipilih | Penjadwal | 5 | Alarm satu kali di memori ada |
| UI17 | 17 | Timer, countdown, mulai/pause/reset sesuai rancangan | Penjadwal | 5 | Mulai/batal di memori ada; kartu/pause belum |

Keberadaan tombol atau ilustrasi bukan bukti fitur sudah bekerja. Pengulangan alarm “setiap hari 06:00”, scrub media, dan siklus Pomodoro 1/4 pada gambar perlu kontrak implementasi tambahan; sumber hanya menyediakan logika dasar.

## Hal yang tetap disimpan dalam backlog

- Kalender: baca agenda dan perintah tambah rapat (pola 57), keduanya harus punya jalur produk. Impor `.ics` saja belum menentukan tempat menyimpan acara baru.
- Poles Acrylic/Mica, gradasi tipis, tepi terang, bayangan lembut, animasi dan tema gelap/terang + accent Windows. Tidak menjanjikan refraksi liquid glass fisik.
- Wake word “Kai” menggunakan openWakeWord pada tahap akhir, dengan evaluasi false trigger.
- TTS opsional Piper/SAPI; tetap lokal. Pemilihan voice/lisensi menyusul.
- Opsi UI C# + WPF-UI dan IPC lokal bila pengukuran menunjukkan PySide6 tidak cukup.
- Portofolio: bukti integrasi OS, suara, UI, keputusan arsitektur dan demo; estimasi 1–2 minggu di sumber adalah perkiraan lama, belum jadwal yang disepakati.

## Yang bukan kebutuhan Kai dari referensi iPhone

Face ID, AirDrop, Personal Hotspot, Find My iPhone, dan screen recording pada gambar pertama adalah contoh bentuk/state. Tidak ditambahkan menjadi fitur Windows. AirPods memberi contoh toast perangkat; bukan kewajiban membeli/mendukung perangkat Apple tertentu.

## Peta keterlacakan 12 bagian sumber

| Bagian sumber | Dokumen pelaksana |
| --- | --- |
| 1 Ide utama | 01, 03 |
| 2 Perilaku island | 02, 05 |
| 3 Gambaran 17 fitur dan material | 01, 02, 04 |
| 4 Cara kerja dan keputusan suara/Spotify | 03, 06, 07 |
| 5 Seluruh 58 pola dan aturan | 08, 05 |
| 6 Teknologi | 03, 06 |
| 7 Delapan tahap | 04 |
| 8 Lima fitur tambahan | 01, 03, 04 |
| 9 Risiko | 03, 05, 06, 07 |
| 10 Alat open source | 03, 09 |
| 11 Status dan langkah berikutnya | 07, 04; diperbarui berdasarkan ZIP |
| 12 Portofolio dan perkiraan durasi | 01, 04 |
