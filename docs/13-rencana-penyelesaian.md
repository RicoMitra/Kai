# Penyelesaian versi lokal Kai

Pengguna melanjutkan proyek setelah restart dan meminta penyelesaian. Pilihan awal model on demand kemudian digantikan: pengguna menonaktifkan suara dan menyetujui media/audio hanya saat dibuka, demi target 20–30 MiB privat idle. Kerjakan bertahap dalam satu sesi, tes bergantian; jangan mengulang rangkaian probe Acrylic berat sebelumnya.

1. Backend: data/settings di LOCALAPPDATA, timer/alarm persisten, kalender lokal/impor ICS, shelf referensi, validasi angka. Tes memakai database sementara tanpa menyentuh data pribadi.
2. Suara: PTT hanya membuka mikrofon ketika ditahan, stop nyata pada batas, satu pekerjaan; Whisper hidup dalam proses singkat dan proses ditutup pada hasil/error/timeout/keluar. CPU dibatasi; GPU gagal turun ke CPU. Tes lifecycle memakai recognizer tiruan dalam proses nyata, tanpa memuat model.
3. Integrasi: SMTC untuk metadata/transport, Core Audio untuk volume/perangkat, metrik sistem on demand, cuaca/lirik dengan timeout/cache terbatas. Ketiadaan akun/izin/sensor ditampilkan eksplisit.
4. Produk: kartu compact, kontrol dan panel pengaturan/manajemen; launcher normal dan demo terpisah, singleton, shutdown bersih. Pilihan lokasi/kalender/Spotify tersedia di pengaturan sehingga bukan data contoh yang diam-diam dipakai.
5. Verifikasi dan paket: regresi parser, backend dan UI; satu smoke Windows yang terbatas; satu pengukuran memori tanpa model. Buat ZIP source portabel tanpa venv/model/data pribadi, serta README/status yang membedakan implementasi dan integrasi yang belum diotorisasi pengguna.

Optional wake word/TTS tetap opsional dan mati secara default. Tidak memasang browser runtime atau mengubah autostart/izin sistem. Alarm tidak dijanjikan membangunkan laptop saat proses mati. Notifikasi lintas aplikasi harus mengikuti izin/capability Windows, tanpa API WhatsApp tidak resmi.

## Hasil pelaksanaan

- [x] Backend persisten dan validasi angka; regresi parser 98/98.
- [x] PTT/worker sempat diimplementasikan dan dites lifecycle, kemudian **dinonaktifkan pada entry point/panel/requirements** sesuai keputusan terbaru. Tidak memuat model nyata.
- [x] Media/audio dalam proses on demand; task integrasi sesaat; worker ditutup dan library native tidak berada di parent.
- [x] Delapan tab kontrol, perintah teks, tray, singleton, launcher normal/hemat/preview dan Setup di LOCALAPPDATA.
- [x] 25 unittest, native smoke dan pemeriksaan API publik dengan cache sementara; pengukuran default 22,64 MiB privat idle, metrik total dipisahkan.
- [x] Panduan/status/keputusan diperbarui dan script ZIP source allowlist + manifest disediakan.
- [ ] Penerimaan personal: akun Spotify/perangkat nyata, sleep/resume, semua DPI/monitor dan soak panjang.
- [ ] Native Acrylic, identitas paket/notifikasi, installer, cloud calendar dan fitur opsional backlog.

Checklist terakhir adalah batas versi lokal, bukan fitur yang diam-diam dihapus. Paket tidak boleh disebut seluruh ide asli selesai/teruji.
