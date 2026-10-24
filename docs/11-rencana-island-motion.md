# Implementasi island dan motion

Pengguna meminta melanjutkan pengerjaan pada 22 Oktober 2026, khususnya popup, hide, dan muncul kembali saat kursor mendekat. Arah navy/glow sudah dipilih. Kerjakan langsung dalam sesi ini dengan prinsip ponytail; tidak ada migrasi web atau dependensi animasi tambahan.

## Lingkup

Bangun M1 yang dapat dijalankan: hover, jam/tanggal, status/event, demo mandiri, tray untuk keluar/mencoba status, reduced motion, dan launcher. Gunakan `kai-v2.zip` yang baru ditemukan sebagai fondasi island; arsip tetap utuh. Integrasi suara yang ada dipanggil hanya dalam mode suara, bukan demo. Media/volume/sensor asli tetap milestone berikutnya.

## Tugas dan verifikasi

1. Tambah `kai/test_island.py` memakai unittest dan QtTest yang sudah tersedia. Buktikan kegagalan awal untuk kontinuitas spring, delay hover, event yang membuka island, dan geometri jendela tetap.
2. Ubah `kai/island.py`: spring kritis yang mempertahankan posisi/velocity saat target berubah, controller hover dengan waktu monotonic, kanvas transparan tetap, navy/rim/glow, transisi isi tanpa meregangkan teks. Animation timer berjalan hanya ketika perlu. Overlay awal click-through; kontrol demo berada di tray.
3. Hubungkan `kai/main.py --island --demo`, `--island`, dan `--reduced-motion`. Demo tidak membuka mikrofon, login, mengunduh model, atau memutar media. Pertahankan `--text --dry` dan pengujian parser.
4. Tambah launcher `Kai.cmd` dan perbarui README serta status. Jalankan unittest UI, parser 98 contoh, pemeriksaan CLI, dan smoke test Windows nyata. Simpan capture collapsed/expanded/listening dari widget sendiri untuk inspeksi visual. Verifikasi fokus dan click-through lintas jendela bila memungkinkan.

## Referensi yang diperiksa

- [Skiper Dynamic Island](https://skiper-ui.com/v1/skiper2): referensi bentuk/variasi state, bukan kode yang dipindahkan ke Python.
- [Unlumen Hover Expand](https://ui.unlumen.com/components/hover-expand): spring serta isi yang masuk setelah ruang terbuka; diterapkan sebagai prinsip.
- [SmoothUI motion](https://smoothui.dev/docs/guides/animation-best-practices): respons cepat, gerak beralasan, reduced motion. Aturan performa CSS tidak diasumsikan identik dengan Qt.
- [Magic UI Dock](https://magicui.design/docs/components/dock): respons kedekatan pointer dan bentuk ringkas; tidak memasang React/Tailwind.
- [Vengeance UI](https://www.vengenceui.com/): katalog hover/glow/feedback sebagai referensi; tidak menyalin kode premium atau menambah dekorasi scroll.

Semua implementasi motion Kai ditulis untuk Qt. Tidak ada pembelian atau komponen berbayar yang dibutuhkan.
