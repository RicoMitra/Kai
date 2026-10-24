# Pengujian dan penerimaan

Pengujian disesuaikan perubahan. Tidak perlu framework baru untuk mengulang tes parser yang sudah tersedia. Tes UI/integrasi Windows memerlukan observasi perilaku nyata; catat kondisi perangkat dan hasilnya.

## Verifikasi versi lokal

Perintah aktif berada di README root dan hasil lengkap di 07. Suite unittest `test_*.py`: 25 lulus; parser terpisah: 98/98. Smoke native hover/fokus/click-through dan expanded controls lulus DPR 1,5. Benchmark core/voice dilakukan terpisah, termasuk semua proses turunan launcher. Suara kini nonaktif; pengujian lifecycle lama tidak mengaktifkannya. Kontrol media akun nyata, event headset fisik, sleep/resume dan soak panjang belum dinyatakan lulus.

## Baseline yang telah dijalankan

Pada 22 Oktober 2026, Python 3.12.4, dari folder `kai/`:

```powershell
python -B test_intents.py
```

Hasil: `98/98 lulus`, exit code 0. Ini membuktikan contoh parser tersebut, bukan akurasi audio, keberhasilan aksi, UI, atau semua kemungkinan variasi 58 pola.

## Matriks penerimaan

| Area | Skenario penting | Lulus jika |
| --- | --- | --- |
| Pil/hover | Masuk/keluar tepi cepat, kembali sebelum 700 ms | Tidak flicker, tidak menumpuk animasi, geometri kontinu |
| Click-through | Klik aplikasi di balik pil dan sudut transparan | Klik diterima aplikasi; kartu expanded tetap dapat diklik |
| Fokus | Mengetik di editor saat toast otomatis | Caret/fokus tidak direbut; Ctrl+Space diteruskan sesuai sumber |
| DPI/monitor | 100%, 125%, 150%; monitor dicabut; work area sempit | Pusat dan target klik benar; island tetap di layar |
| Tema/aksesibilitas | Terang/gelap/accent, wallpaper ramai, reduced motion/transparency | Teks terbaca, fokus terlihat, tanpa ketergantungan warna/glow |
| Media | Spotify tutup, metadata kosong, cover gagal, session ganda | State kosong jelas, kontrol tidak mengklaim sukses palsu |
| Timeline/lirik | Pause, seek, next, lirik tidak tersedia | Progres/lirik mengikuti session dan tidak menampilkan track lama |
| Volume | 0/100, mute, tombol fisik, drag slider cepat, output berganti | Nilai sesuai sistem, tidak ada feedback loop event |
| Headset | Connect/disconnect/reconnect, Bluetooth non-audio | Hanya perangkat relevan; toast tidak berulang tanpa perubahan |
| PTT | Tekan singkat <0,4 s, lepas Ctrl dahulu/Space dahulu, tahan >20 s | Mikrofon benar-benar ditutup; tidak merekam tanpa indikator |
| STT | Diam, noise, Indonesia/Inggris/campuran, nama favorit | Tidak mengeksekusi halusinasi diam; unknown aman; latency dicatat |
| Worker | PTT berulang saat model sibuk, gagal model/CUDA, keluar saat aktif | Tidak ada transkripsi bersamaan tak terkendali; recovery/cleanup benar |
| Intent | Judul berisi angka, “dari”, filler; salah dengar; jam/durasi invalid | Nama lagu aman, slot tervalidasi, tidak mengubah angka negatif menjadi positif |
| Spotify | Token expired, offline, 403/429, tak ada device | Pesan spesifik; timeout; transport fallback tidak menukar pause menjadi resume diam-diam |
| Penjadwal | Restart, sleep/resume, jam sistem berubah, cancel bersamaan fire | State tersimpan, notifikasi selesai sekali, canceled tidak hidup kembali |
| Alarm | Jam sama dengan sekarang, pergantian hari, recurrence bila dipilih | Waktu target jelas; tidak menjanjikan bunyi saat proses mati |
| Kalender | `.ics` kosong/rusak, timezone, recurring event, UID sama | Jadwal tepat, impor ulang tidak menggandakan acara |
| File shelf | Path Unicode, folder, file hilang, item besar | Semantik sesuai keputusan; dismiss tidak menghapus file asli |
| Notifikasi | Izin ditolak/dicabut, toast tanpa body, pesan pribadi | Fitur mati dengan baik; tidak menyimpan isi pesan default |

## Performa: target usulan, belum hasil ukur

- Ukur idle tanpa STT, model loaded idle, saat mendengarkan, saat transkripsi, dan saat animasi secara terpisah.
- Catat CPU, RAM, VRAM, frame time dan waktu transkripsi p50/p95 pada sampel ucapan pendek. Jangan menyamakan benchmark audio panjang upstream dengan latency pengguna.
- Sasaran awal: animasi mengikuti refresh layar tanpa hitch nyata pada 60 Hz; budget frame sekitar 16,7 ms. Periksa juga layar refresh tinggi.
- Sasaran idle UI tanpa model: rata-rata CPU di bawah 1% pada laptop ini selama sampel 60 detik; ukur dahulu, revisi jika metode/OS memengaruhi hasil. Tidak menjanjikan batas RAM sebelum model dimuat dan diukur.
- Bandingkan Small CPU int8 dan Medium GPU float16/int8_float16 jika didukung runtime; pilih berdasarkan akurasi, latency, panas dan memori. GPU terdeteksi bukan alasan mengabaikan pengukuran.

## Bukti yang disimpan

Tiap hasil memuat milestone, perintah/langkah manual, environment, harapan, hasil aktual dan batas. Jangan menyimpan audio/transkrip pengguna secara default. Screenshot/rekaman demo harus memakai data contoh atau disetujui pengguna. Status “belum diuji” tetap dipertahankan jika jalurnya belum benar-benar dijalankan.
