# Kai 3.0 — Clipboard, Shelf, Notes dan konteks

> Revisi terakhir di [18](18-notes-transform-dan-musik.md): Command diganti Fast Transform; Notes mengikuti daftar/detail checklist tanpa subheading; Musik memiliki seek dan −/+ volume. Kontrak Shelf/Clipboard/dedupe di bawah tetap.

23 Oktober 2026. Permintaan pengguna ini menggantikan cakupan Clipboard/gambar dan tampilan idle pada 0.3.0. Nomor aplikasi kini **3.0.0**, sesuai penamaan versi 3.0 pengguna. Stack, media on demand, jam/tanggal hover dan target RAM privat idle 20–40 MiB tetap.

**Koreksi terakhir:** pengguna meminta menghapus Sistem karena tidak diperlukan. Halaman, navigasi, tray dan jalur task sistem dilepas. Kini lima alat Command/Clipboard/Notes/Shelf/Musik + Pengaturan (enam halaman). Helper/test metrik lama tetap arsip/dev; tidak ada pengambilan metrik sistem di runtime produk.

## Kontrak aktif

- **Smart Clipboard:** riwayat teks dan URL saja. Kode tetap teks, bukan objek/biner. Tidak ada gambar, screenshot atau file dalam tabel/UI Clipboard. Batas 80 item, 20 pin dan teks 64 KiB tetap. Jeda hanya menghentikan riwayat teks; intake gambar/file Shelf terpisah. Pengecualian password/sumber tetap dihormati sebelum keduanya diproses. Tidak membaca clipboard awal.
- **Smart Shelf:** menerima screenshot tersimpan, gambar clipboard, file/folder clipboard/drop/manual serta file baru dari Windows Known Folder Downloads. Tidak mengimpor file lama saat startup. Event direktori, bukan polling terus-menerus. Ekstensi sementara `.crdownload`, `.part`, `.partial`, `.tmp`, `.download` diabaikan. Ukuran+mtime harus stabil dan file unduhan tidak boleh masih dibuka untuk menulis. Folder unduhan khusus di luar Known Folder belum dicakup.
- **Thumbnail/preview:** gambar asli didekode dalam ukuran kecil sesuai rasio. Thumbnail mengikuti item yang terlihat, maksimal 12 sekaligus; gambar lepas layar kembali ke ikon. Preview gambar berada dalam Shelf; dokumen/file lain menampilkan metadata dan dibuka di aplikasi default. Tidak ada renderer PDF/Office tambahan. Multi-select, pin, filter/search, drag URL dan penghapusan referensi tetap tersedia.
- **Smarter Notes:** checklist Markdown `- [ ] Tugas` / `- [x] Selesai` tampil sebagai kotak centang native yang dapat diklik. Tombol + Checklist menambah item. Pin mengurutkan catatan di atas yang tidak dipin. Autosave 350 ms, flush pada pindah/close, batas 20.000 karakter tetap. Status seluruh catatan dan centang per item berbeda.
- **Contextual Actions:** URL menawarkan Buka di Browser; gambar/file memberi akses Simpan / lihat di Shelf yang sudah menerima item otomatis. Tindakan browser hanya saat diklik dan hanya http/https valid. Popup 290 × 56 DIP, sekitar 4 detik, tidak mengaktifkan jendela/mengambil fokus. Popup konteks diabaikan ketika bidang kerja Kai terbuka agar tidak menimpa aktivitas.
- **Idle:** referensi terakhir `references/sleeping-robot-capsule.png` menggantikan `robot-capsule-superseded.png`. Pil menjadi **72 × 24 DIP**, kapsul reflektif dan dua mata putih/lavender. Digambar native Qt secara statis tanpa video/animasi loop atau raster besar. Logo robot resmi di hover/header/tray tetap dipakai. Hover 320 × 68 dan bidang kerja 540 DIP tetap.

## Akar sebab dan deduplikasi

Sebelumnya PNG hasil clipboard dan file screenshot asli memiliki path berbeda. Primary key `files.path` hanya mencegah path yang sama, sehingga satu gambar menjadi dua item.

Kini `ShelfIntake` menyatukan seluruh sumber otomatis. Worker menghitung SHA-256 piksel RGB32 beserta dimensi, sehingga metadata, kompresi PNG dan variasi alpha clipboard tidak membentuk identitas berbeda. SQLite menyimpan `files.fingerprint`; transaksi menggabungkan referensi dengan identitas sama, menjaga pin/jumlah buka dan memilih file asli dibanding PNG sementara milik Kai. Urutan clipboard→folder maupun folder→clipboard menghasilkan satu item. Ini pencocokan piksel persis, bukan pencarian kemiripan visual/JPEG lossy.

Migrasi memindahkan referensi gambar Clipboard lama ke Shelf dan menghapus baris gambar dari history; file asli tidak dihapus. Duplikat lama dalam daftar Shelf dikonsolidasikan saat Shelf pertama dibuka. Pembersihan disk hanya menyentuh PNG tidak direferensikan dalam direktori milik Kai `clipboard-images`, bukan file screenshot/unduhan pengguna. Rekonsiliasi dibatasi daftar 100 item; tidak memindai seluruh disk.

Gambar clipboard tetap maksimal 12 MP, PNG 4 MiB/item, total disk 24 MiB. Encoding/hash berlangsung di satu worker thread sesaat. Hanya satu bitmap menunggu selain pekerjaan aktif; gambar berikut mengganti bitmap antrean agar burst clipboard tidak menahan banyak gambar penuh. Screenshot file tetap diproses melalui antrean path maksimal 100. Tidak memasang dependensi baru.

## Review tampilan

| Before | After | Why |
| --- | --- | --- |
| Orb kecil dalam pil 56 × 20 | Kapsul mata 72 × 24 | Arahan gambar terakhir dan keterlihatan |
| Gambar bercampur dalam Clipboard | Teks/URL di Clipboard; gambar di Shelf | Pemisahan yang diminta |
| Duplikat karena path berbeda | Identitas piksel dengan prioritas original | Satu screenshot, satu item |
| Enam thumbnail awal saja | Thumbnail item terlihat dan preview embedded | Gambar dikenali tanpa cache seluruh daftar |
| Notes teks + status global | Checklist per item dan pin catatan | Daftar kerja sederhana dengan autosave |

## Verifikasi dan batas

`tools/check_shelf_v3.py` menguji gambar clipboard dan folder dalam dua urutan/kompresi, perbaikan duplikat lama, original tetap ada, unduhan rename final, pengecualian file lama/sementara, checklist/pin/autosave, thumbnail/preview asli, popup tidak mengambil foreground/fokus dan klik action. Semua memakai file/clipboard/jendela milik tes. Bukti: `artifacts/productivity/shelf-v3-verification.json`, `v3-*.png`.

`tools/check_productivity.py` disesuaikan agar gambar hanya di Shelf. Regresi parser/backend/motion, benchmark dan batas integrasi terakhir berada di 07. Uji rename download lokal bukan bukti setiap browser/download manager; clipboard-only burst, download folder khusus, JPEG lossy, akun Spotify, perangkat fisik, DPI lain dan soak harian tetap perlu penggunaan nyata.

Kode utama: `clipboard_service.py`, `capture_shelf.py`, `storage.py`, `product_pages.py`, `island.py`, `panel.py`. Data/settings/token tidak dimasukkan ke rilis. Tidak menyalakan suara/WhatsApp, mengubah izin Windows atau autostart.
