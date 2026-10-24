# Kai productivity — revisi 22 Oktober 2026

Arahan pengguna: hapus Fokus, Agenda, Waktu, Cuaca; tambahkan Smart Clipboard, Quick Command/Search, Quick Notes, Smart Shelf. Musik dan Sistem tetap ada. Target terbaru RAM privat idle 20–40 MiB. Referensi gambar adalah kebutuhan produk/desain, bukan instruksi untuk memasang software yang digambarkan.

## Desain dan batas

Satu island charcoal, rim lembut, aksen pearl/lavender yang terbatas; logo robot asli. Koreksi pengguna setelah preview: hover utama kembali menampilkan jam, tanggal dan logo Kai seperti sebelumnya; tombol Clip/Notes/Shelf tidak memenuhi tampilan utama. Jam tampilan dipertahankan, sedangkan fitur Waktu/timer/alarm tetap dihapus. Navigasi ringkas: Command, Clipboard, Notes, Shelf, Musik, Sistem; pengaturan dari header. Setiap halaman memiliki tinggi sesuai isi, bukan dialog terpisah. Hover dan tutup memakai spring interruptible; shortcut membuka kontrol tanpa menunggu animasi. Toast screenshot/salin/status lebih kecil daripada halaman kerja.

Clipboard: teks/link/kode dan gambar, pencarian, pin, salin/tempel ulang, pause/bersihkan. Hanya perubahan baru saat Kai hidup; tidak membaca riwayat OS lama. SQLite di data lokal, maksimal 80 item termasuk maksimal 20 pin; teks 64 KiB/item. Gambar disimpan sebagai PNG lokal, anggaran total 24 MiB dan maksimum 12 megapiksel per gambar; daftar tidak memuat seluruh gambar ke RAM. Format pengecualian clipboard Windows/password-manager dihormati bila disediakan aplikasi sumber. Password yang disalin sebagai teks biasa tidak dapat dikenali dengan pasti; tersedia Pause dan Hapus. Tidak mengirim clipboard ke layanan eksternal.

Command: Ctrl+Alt+Space, pencarian shortcut Start Menu dan aplikasi yang dikonfigurasi, membuka folder/file/URL pilihan pengguna, kalkulator aritmetika terbatas, perintah musik/volume. Tidak menjalankan shell arbitrer dari hasil pencarian. Fitur waktu/fokus/agenda/cuaca ditolak dalam jalur UI baru; data lama tidak dihapus. Indeks aplikasi dipindai saat Command dipakai, bukan seluruh disk saat idle.

Notes: tambah satu klik, autosave, edit, cari, tandai selesai, hapus; catatan sederhana lokal tanpa sinkron cloud. Simpan juga saat island ditutup agar input tidak hilang.

Shelf: screenshot otomatis, drop file/folder, gambar clipboard, pencarian/filter tipe, pin favorit, multi-select dan drag keluar. Menghapus item Shelf hanya menghapus referensi; file asli tidak dihapus. Thumbnail kecil dibaca bertahap dan jumlahnya dibatasi. Gambar clipboard yang dikelola Kai tetap dihitung dalam kuota disk.

Sistem: CPU/RAM/baterai/disk/GPU, laju jaringan dan proses RAM teratas melalui pekerjaan sesaat. Tidak ada pemantauan proses penuh saat idle. Media tetap worker proses hanya selama Musik dibuka.

## Keputusan implementasi

Dipilih: Qt native + SQLite + API clipboard/hotkey Windows, reuse worker dan compositor yang ada. Alternatif mempertahankan halaman lama tidak memenuhi instruksi; mengganti stack dengan webview menambah runtime dan ditolak oleh batas proyek. Tidak memasang dependensi baru. Pengembangan dijalankan sesuai permintaan implementasi pengguna, tanpa mengulang persetujuan arah yang sudah diberikan.

## Urutan pelaksanaan dan penerimaan

- [x] Migrasi SQLite aditif untuk clipboard/notes dan metadata Shelf; tes persistensi, dedupe, kuota/pin, pencarian dan penghapusan aman.
- [x] Layanan clipboard event-driven, gambar disk, native hotkey dan paste ke target sebelumnya; tes memakai data sementara.
- [x] Command index/calculator dan empat halaman baru; hapus halaman serta penjadwal lama dari runtime aktif.
- [x] UI charcoal lebih bersih, state kosong jelas, keyboard, autosave, thumbnail terbatas dan morph adaptif; capture hanya widget/pola milik tes.
- [x] Regresi native hover/klik/fokus, lifecycle worker, benchmark cold idle dan setelah siklus halaman. Laporkan private WS/total WS/commit terpisah; target bukan hard cap.
- [x] Perbarui panduan/status/AGENTS dan paket allowlist; jalankan versi GUI melalui launcher yang sudah diperbaiki.

## Review desain

| Before | After | Why |
| --- | --- | --- |
| Delapan tab dengan waktu/cuaca | Enam alat + Pengaturan | Cakupan baru pengguna |
| Tombol Clip/Notes/Shelf pada hover | Jam, tanggal dan logo | Koreksi pengguna |
| Ikon Shell dan banyak thumbnail | Vektor dan thumbnail terbatas | Cache rendah |
| Panel memendek lalu menutup Musik | Anchor kursor diam; lepas saat bergerak | Navigasi tetap stabil |
| Selalu bidang besar | Toast 290×56, hover 320×68, tinggi sesuai halaman | Adaptif terhadap aktivitas |

28 unittest dan native checks lulus. GUI cold private WS 26,60 MiB; setelah siklus seluruh halaman median 37,10 MiB. Worker reaped, cache pixmap 512 KiB; tanpa trim RAM. Batas integrasi akun/perangkat/semua aplikasi tujuan dicatat di 07.
