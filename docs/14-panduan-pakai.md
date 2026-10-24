# Panduan Kai 3.0

**Memory budget:** all-process 50 MiB remains unproven. See docs/07-status-dan-verifikasi.md for current resident/committed measurements. Older scope descriptions below the latest English contract are historical.

## Latest approved UI — 23 October 2026

English is now the primary interface language: navigation, settings, buttons, tooltips, clipboard/notes/Shelf statuses and conversion errors. Personal notes, copied text, filenames and song lyrics are never translated. Historical Indonesian documentation and inactive feature code remain archives.

The collapsed island is **plain opaque black, 72 × 24 DIP**. Other pages and the clock/logo hover are black. Opening the island brings its top edge to the physical screen edge, with flat upper corners and rounded lower corners. Clock/date and the user's robot identity remain on hover. The previous sleeping-eye/glossy capsule is superseded. While **Music is open and playing**, a static dark gradient follows the album cover; paused/no-cover/other pages return to black. A single 8 × 8 average is calculated from the already bounded 64px cover when the track/cover becomes available. No large blur, animation loop or extra image cache. Native composition/backdrop surfaces are no longer created for this opaque design.

Typography uses installed **Segoe UI Variable**; Qt confirmed this family resolves correctly. It follows the iPhone reference's clean hierarchy using Windows typography. Spring transitions retain velocity on reversal, stop when settled and respect Reduce motion. Long active lyrics wrap without ellipsis; a small scrollbar/wheel makes overflow accessible. Adjacent lines may scroll out of the viewport. Reference photos are retained in docs/references/music-lyrics-top-edge.jpg, iphone-island-motion.jpg and iphone-island-calendar.jpg; the calendar picture is visual inspiration and does not restore Calendar.

Fast Transform has **FROM / TO columns** and a center divider. FROM: PNG/JPG/PDF/Word; TO: PDF/MD/Word. Only the approved workflows remain: **JPG or PNG → PDF; PDF → MD; PDF → Word (.docx); Word (.docx) → PDF**. One input file and one output per job. PDF-to-JPG, other conversions, Notes input and MD/TXT input are removed. Incompatible output buttons are disabled automatically. PDF→Word extracts editable text; Word→PDF preserves basic paragraphs/headings/tables/images, with complex layout limits. No Word process or new dependency. Save or Clear removes temporary results; leaving/closing also cleans up after cancellation/reap. Original files and saved copies are retained.

Skills used selectively: ponytail full, emil-design-eng, apple-design and UI/UX Pro Max. The latter's design-system search was run; its landing-page/blue palette/web-font suggestions were discarded because the user's approved black native desktop brief takes precedence. Applied checks: grouping, contrast, pressed/focus/selected states, keyboard access, bounded image work and reduced motion. No web UI framework installed.

Verification: 37 unit tests plus six conversion fixture checks cover PNG/JPG→PDF, PDF→MD/DOCX, DOCX→PDF and scanned PDF→MD with real local Windows OCR. Disposable engine isolation/reap, one-file restriction, unsupported direction rejection, save/cleanup/cancel and English labels are checked. Native hover/click-through/focus/reentry/reversal and six-page navigation pass at current 150% DPI. tools/check_appearance.py captures owned widgets with generated cover/lyrics, verifies column fit, wrapping, top-edge attachment, installed font and disabled backdrop. Account playback/seek was not mutated. See the latest status for measured memory and its limits.


**Notes paling akhir:** + Catatan menampilkan satu input; ketik dan Enter. Lingkaran/Space menandai selesai, Hapus/Delete membuang catatan. Tidak ada cari, Edit, detail atau subheading. Autosave tetap. Pin melalui klik kanan. Untuk konversi catatan gunakan Dari Notes di Transform. Petunjuk editor/detail di bawah merupakan riwayat yang sudah diganti.

## Transform, Notes dan Musik — revisi terakhir

Ctrl+Alt+Space atau klik island membuka **Fast Transform**, pengganti Command. Tambahkan/drop 1–2 file atau Dari Notes; pilih PDF/MD/JPG lalu Ubah. Notes dan Shelf juga memiliki tombol Ubah. **Simpan hasil sebelum pindah/tutup**: salinan tersimpan tetap ada, file sementara dihapus saat simpan/proses berikutnya/Bersihkan/pindah/tutup. Satu worker, maksimal dua hasil; mesin konversi keluar setelah selesai. PDF/Word→JPG hanya dua halaman awal; input maksimal 20 MiB, PDF 50 halaman, detail batas di 18.

Word berarti `.docx`; `.doc` lama perlu disimpan sebagai .docx. Layout kompleks Word dapat berbeda, PDF→MD adalah ekstraksi teks, gambar→MD memakai OCR Windows lokal sesuai bahasa terpasang; periksa hasil. Tidak ada pengunduhan model/cloud. File asli tidak diubah. Konversi aktif tetap dapat memakai lebih banyak RAM daripada idle.

Notes menampilkan daftar lingkaran; klik lingkaran/Space untuk selesai, judul/Enter untuk isi. Isi memperlihatkan tanggal dan checklist kuning **tanpa subheading**. Edit membuka teks penuh; baris pertama menjadi nama di daftar, `- [ ]`/`- [x]` adalah checklist. + Checklist menambahkan item, Daftar kembali; Pin dan autosave tetap.

Musik: klik progress bar untuk maju/mundur ke posisi yang dipilih, −/+ untuk volume langkah 5%, rail dapat diklik/diseret, VOL untuk mute. Volume adalah output sistem. Seek memerlukan dukungan pemutar Windows; pesan error muncul jika ditolak. Media worker tetap hanya ketika Musik dibuka.

Panduan Command dan tata letak Notes lama di bawah adalah arsip. Lihat [18](18-notes-transform-dan-musik.md) dan [handoff](../handoff.md).

## Pembaruan 23 Oktober 2026

Sistem dihapus atas permintaan terakhir. Fitur sekarang: Command, Clipboard, Notes, Shelf dan Musik, plus Pengaturan; enam halaman. Petunjuk Sistem pada bagian lama di bawah tidak berlaku lagi.

Clipboard kini **teks dan URL saja**, termasuk kode sebagai teks. Gambar/screenshot/file tidak disimpan di history. Gambar clipboard, screenshot tersimpan dan file/folder clipboard masuk **Smart Shelf**. Jeda Clipboard hanya menjeda riwayat teks; pengecualian sumber tetap dihormati untuk semua intake.

File baru yang selesai diunduh ke Windows Known Folder Downloads otomatis masuk Shelf; file lama dan ekstensi sementara tidak diimpor. Folder download khusus di tempat lain belum dipantau. Gambar punya thumbnail asli dan preview ketika dipilih; file lain menampilkan metadata dan Buka memakai aplikasi default. Keluarkan/Bersihkan hanya menghapus referensi, bukan original.

Satu screenshot dari clipboard+folder kini disatukan berdasarkan isi piksel; file asli diprioritaskan. Duplikat lama pada daftar 100 item dikonsolidasikan saat Shelf pertama dibuka. PNG internal tidak direferensikan dibersihkan, screenshot asli tetap ada. Perubahan crop/resize/JPEG lossy tidak selalu dianggap gambar sama.

**Smarter Notes:** + Checklist menambah `- [ ] `, ketik nama tugas, lalu klik kotak centang pada daftar di bawah editor. Pin menempatkan catatan di atas. Autosave 350 ms dan flush saat ditutup tetap tersedia.

Menyalin URL menawarkan **Buka di Browser**; gambar/file menawarkan **Simpan / lihat di Shelf** yang telah menerima item otomatis. Mini island tidak mengambil fokus atau menimpa halaman kerja; browser hanya terbuka ketika penawaran diklik.

Pil idle terbaru kaca glossy dua mata **72 × 24 DIP**; hover jam/tanggal/logo tetap. Cold privat idle terukur 26,66 MiB, sesudah semua halaman 53,50 MiB pada run terbaru; target 20–40 belum terpenuhi setelah siklus tersebut. Detail dan metrik lain di 07. [Handoff lengkap](../handoff.md) dan [kontrak 3.0](17-revisi-shelf-notes-dan-context.md).

Bagian berikut mencatat panduan 0.3.0. Aturan gambar Clipboard/ukuran/angka lama yang bertentangan digantikan pembaruan di atas.

## Akses dan fitur terbaru

Buka Kai.exe atau shortcut Desktop/taskbar. Hover menampilkan **jam, tanggal dan logo**; klik membuka kontrol. **Ctrl+Alt+Space** membuka Command dan memfokuskan input. Navigasi: Command, Clipboard, Notes, Shelf, Musik, Sistem; Pengaturan dari header. ×/Escape menutup kontrol; tray → Keluar Kai menghentikan aplikasi.

Jam tampilan tetap ada. Fokus, Agenda, Waktu/timer/alarm dan Cuaca sudah dilepas dari runtime/UI aktif; data lama tetap disimpan. Suara/WhatsApp tetap nonaktif. Jika halaman memendek, kursor diam tidak lagi membuat Musik tertutup; gerakkan kursor menjauh untuk auto-hide.

## Smart Clipboard

Salin teks/link/kode/gambar ketika Kai berjalan. Cari/filter, pin, salin/tempel ulang, hapus, jeda dan bersihkan tersedia. Pin menjaga item saat Bersihkan; Jeda disimpan lintas peluncuran. Tidak membaca clipboard awal atau mengimpor riwayat Windows lama.

Tempel/Enter mengembalikan konten dan mengirim Ctrl+V ke aplikasi sebelumnya. Jika Windows menolak fokus/input, konten tetap disalin: pilih tujuan dan Ctrl+V sendiri. Aplikasi tujuan harus menerima jenis data yang dipilih.

Batas: 80 item/20 pin, teks 64 KiB; gambar 12 megapiksel, PNG 4 MiB/item dan 24 MiB total. Gambar di disk, thumbnail terbatas. Hapus referensi Clipboard dan Shelf untuk melepas gambar yang dikelola Kai; file tidak terpakai dibersihkan saat gambar baru diproses. Original pengguna tidak dihapus. Riwayat dapat berisi informasi pribadi; gunakan Jeda/Hapus. Format pengecualian Windows/password manager dihormati jika tersedia, tetapi password teks biasa tidak selalu dapat dikenali. Kai tidak mengirim clipboard ke layanan eksternal.

## Command, Notes dan Shelf

Command menerima nama shortcut Start Menu, path file/folder, URL http/https, aritmetika dan perintah musik/volume. ↑↓ memilih, Enter menjalankan. Contoh `125*8`, `(450+250)/2`, path Downloads, `puter Tulus`, `volume 40`. Indeks dibatasi 500 shortcut saat digunakan, bukan seluruh disk. Tidak mengevaluasi kode Python/shell. Perintah fitur yang dihapus ditolak.

Notes: + Catatan, ketik, cari, tandai selesai/aktif atau hapus. Autosave 350 ms dan flush saat pindah halaman/menutup island; maksimal 20.000 karakter/item, 100 hasil daftar, tanpa cloud.

Shelf: screenshot baru yang disimpan sebagai file masuk otomatis dari folder Screenshots Windows/OneDrive. File lama tidak diimpor; gambar clipboard dan file/folder yang disalin, drag/drop, + File/+ Folder juga tersedia. Cari/filter tipe/favorit, Ctrl+klik/Ctrl+A untuk memilih lalu drag keluar. Keluarkan hanya menghapus referensi pilihan; Bersihkan menjaga pin pada 100 referensi terbaru. Original tetap ada.

## Musik, Sistem dan RAM

Musik tetap SMTC/transport/volume/mute/lirik dan Spotify PKCE. Worker hanya selama Musik dibuka. Pengaturan → Client ID → Simpan → Login Spotify; callback dashboard `http://127.0.0.1:8888/callback`. Token tetap lokal. Sistem mengambil CPU/RAM/baterai/disk/GPU, jaringan dan lima proses RAM teratas saat dibuka/Perbarui, melalui proses sesaat. Sensor yang tidak ada ditandai.

Target **RAM privat idle 20–40 MiB** bukan hard cap saat fitur aktif. Bukti GUI: cold 26,60 MiB, setelah seluruh halaman ditutup median 37,10 MiB; total WS/commit terpisah di 07. Gunakan tray jika Ctrl+Alt+Space dipakai aplikasi lain.

Runtime/data lama laptop ini berada di cache fisik MSIX Codex; launcher menjaga direktori settings/token/DB yang sama. Setup dari Explorer memakai runtime normal. Jangan menghapus cache paket Codex tanpa cadangan pribadi. Kai.exe belum installer mandiri; folder kai/assets tetap diperlukan. Log startup/launcher berada di direktori data lokal; session.json hanya versi/PID/fitur/status shortcut, tanpa isi clipboard/token.

## Arsip panduan sebelum revisi productivity

Bagian di bawah adalah catatan versi lama. Fitur dan batas yang bertentangan dengan panduan 0.3.0 di atas tidak lagi berlaku.

Keputusan terbaru pengguna: tanpa suara, RAM privat idle ditargetkan 20–30 MiB, media/audio hanya ketika dibuka. Mode otomatis yang lebih mahal boleh dipilih kembali melalui Atur; bukan default.

## Mulai dan tutup

1. Klik dua kali `Kai.exe` atau shortcut Kai di Desktop; arahkan kursor ke pil atas tengah untuk membuka kartu.
2. Klik kartu untuk membuka kontrol di dalam island; klik kanan ikon tray juga menyediakan pilihan halaman. Menutup panel tetap membiarkan jam dan penjadwal hidup.
3. Pilih **Keluar Kai** dari tray untuk menghentikan seluruh layanan. Peluncuran kedua tidak membuat island ganda.

`Kai Hemat.cmd` memaksa media on demand. `Kai Preview.cmd` hanya contoh visual. Tutup Kai yang sudah hidup sebelum beralih mode karena aplikasi memakai singleton. Kontrol menyatu dengan island, tanpa jendela dialog terpisah. Musik sekitar 540 × 280 DIP, Shelf 540 × 270; halaman formulir menyesuaikan tinggi.

## Media, volume, musik

Buka tab Media, tunggu sesi Windows dibaca, lalu gunakan kontrol. Aplikasi pemutar harus menyediakan SMTC; tanpa sesi tidak ada lagu yang bisa dikontrol. Worker dihentikan ketika pindah dari Media atau panel ditutup. Popup perubahan volume/perangkat otomatis tidak tersedia saat worker mati. Mode ini mengutamakan RAM, sesuai pilihan pengguna.

Pencarian lagu spesifik memakai Spotify Premium dan app developer pengguna. Isi Client ID di Atur → Simpan → Login Spotify, lalu selesaikan browser yang dibuka. Callback dashboard harus sama dengan `http://127.0.0.1:8888/callback`. Token hanya disimpan lokal. Setelah login, kolom perintah menerima misalnya `puter Tulus` atau `play blinding lights`. Ketersediaan endpoint tergantung akses app/account Spotify dan belum diuji dengan akun pengguna. Putar acak saat ini mengambil maksimal 50 liked tracks; bukan seluruh pustaka.

Lirik diambil dari LRCLIB setelah tombol Ambil lirik ditekan, ditandai sesuai posisi jika data sinkron tersedia. Seek/track berubah bergantung timeline yang disediakan pemutar. Tidak ada lirik contoh yang dianggap data pengguna.

## Waktu dan fokus

Tab Timer menyediakan timer menit, alarm HH:mm, pilihan setiap hari, daftar item, jeda/lanjut dan batal per item. Kolom perintah menerima durasi yang lebih rinci. Timer/alarm disimpan di SQLite; kejadian yang terlewat diperiksa saat Kai hidup lagi. Aplikasi tidak membangunkan laptop dan tidak menjadwalkan tugas OS saat ditutup. Popup selesai ditahan hingga diklik/ditutup.

Fokus menerima durasi 1–180 menit. Siklus otomatis bersifat opt-in: fokus → istirahat 5 menit; jeda 15 menit setelah empat sesi hari itu. Statistik dihitung dari sesi yang benar-benar selesai; mulai fokus baru menggantikan fokus/istirahat aktif. Tidak ada statistik palsu dari parser.

## Jadwal, file, cuaca dan sistem

Kalender adalah acara lokal + impor `.ics` untuk 90 hari ke depan. Tambah judul/waktu melalui panel; perintah `tambah rapat besok jam 10` juga disimpan lokal. Tidak menulis ke Google Calendar. Impor ulang file yang sama mengganti acara dari sumber tersebut, tanpa menggandakan acara yang dipindah. Batas 10 MB/2000 hasil; recurrence lebih sering dari harian dan beberapa waktu per hari ditolak. Waktu file tanpa zona memakai zona lokal Windows. Kalender besar sebaiknya dipecah.

Shelf menyimpan referensi, menerima drop file/folder atau tombol tambah. Screenshot baru yang disimpan ke folder Screenshots Windows masuk otomatis ketika Kai berjalan; folder pada laptop ini adalah `C:/Users/RICO/OneDrive/Pictures/Screenshots`. Screenshot yang hanya ada di clipboard belum masuk sampai disimpan sebagai file. Foto lama sebelum Kai dibuka tidak diimpor otomatis.

Buka Shelf dari navigasi island atau menu tray. Gunakan Ctrl+klik atau Ctrl+A untuk memilih 4–5 screenshot sekaligus, lalu seret ke aplikasi tujuan yang menerima file. Tombol **Keluarkan** menghapus pilihan dari Shelf; **Bersihkan** menghapus referensi yang ditampilkan. File asli tetap ada, dan referensi yang dikeluarkan tidak dimasukkan kembali pada sesi yang sama. Buka melalui klik ganda/tombol; menghapus item hanya menghapus referensinya. Jika file asli dipindah, hapus referensi lama lalu tambahkan lokasi baru. Daftar menampilkan 100 referensi terbaru.

Isi kota di Atur dan simpan sebelum membuka Cuaca → Perbarui. Open-Meteo menggunakan cache 20 menit; data lama diberi penanda saat jaringan gagal. Pilihan lokasi pengguna belum diisi otomatis. Metrik Sistem hanya diperbarui atas permintaan; suhu/sensor yang tidak tersedia ditandai, bukan ditebak.

## Privasi dan data

Data dan runtime berada di `%LOCALAPPDATA%/Kai`: `kai.sqlite3`, `settings.json`, cache cuaca/lirik, token Spotify dan folder `runtime`. Tidak ikut ZIP/Git/OneDrive sumber. Tidak menghapus data ini ketika memperbarui source. Tidak ada perubahan autostart, pengaturan Handy, mikrofon atau sistem.

Mode suara tidak aktif dan dependensi suara tidak diperlukan. Kode suara lama disimpan nonaktif sebagai arsip. UI/listener WhatsApp dihapus sesuai permintaan; tidak ada permintaan izin notifikasi.

## Bila bermasalah

- **Tidak muncul:** periksa tray dan peluncuran ganda. Kesalahan startup dicatat di `%LOCALAPPDATA%/Kai/logs/startup.log` dan ditampilkan melalui dialog. Jangan memakai Python global jika dependensi dipasang di runtime Kai.
- **Runtime tidak ditemukan:** launcher membedakan runtime Python hilang dengan berkas start.pyw tidak tersedia dan mencatat lokasi/kode error Windows di logs/launcher.log. Versi baru juga menemukan runtime yang sempat dialihkan ke cache aplikasi Codex oleh Windows. Jika benar-benar belum ada runtime, jalankan Setup Kai.cmd dari Explorer dengan Python 3.12 x64 dan internet. Tidak perlu admin. Jangan hanya memindahkan EXE tanpa folder kai/assets.
- **Musik tidak terdeteksi:** buka Media dan pemutar yang mendukung sesi Windows. Pencarian Spotify butuh Client ID/login/perangkat Spotify aktif.
- **RAM naik:** pastikan mode on demand dicentang dan mulai ulang setelah mengubahnya. Tutup panel untuk menghentikan worker. Target 20–30 berlaku pada RAM privat idle dalam sampel lokal, bukan total working set atau batas saat fitur bekerja.
- **Laptop masih lambat:** keluar Kai melalui tray. Pada pengerjaan RAM sistem tersedia sempat hanya sekitar 180 MB; menonaktifkan suara Kai tidak membebaskan memori aplikasi lain.
- **Kaca tidak blur:** compositor Windows digunakan pada versi baru; jika API gagal, Kai memakai transparansi Qt. Tampilan bergantung wallpaper, Windows dan pengaturan transparansi. Tidak ada screenshot latar berulang untuk meniru blur.

Lihat 07 untuk bukti pengujian dan celah yang masih terbuka. Tidak ada klaim seluruh fitur portofolio atau integrasi akun sudah tervalidasi hanya karena aplikasi dapat dibuka.

Pada laptop ini runtime/data lama berada secara fisik di `%LOCALAPPDATA%/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/Kai`. Launcher menemukan lokasi ini otomatis dan mempertahankan settings/token/DB di sana. Jika Codex dihapus, cache paket dapat ikut hilang; simpan cadangan data secara pribadi dan gunakan Setup dari Explorer untuk pemasangan runtime normal. Jangan membagikan settings/token/DB.
