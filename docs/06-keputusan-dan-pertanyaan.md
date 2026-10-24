# Keputusan dan pertanyaan

## Latest UI correction — 24 October 2026

The owner restored **two plain white eyes** in the collapsed black 72 × 24 DIP pill. They are vector-painted rounded strokes, with no blue/purple accents, glow, bitmap or idle animation. They fade during expansion; the existing clock/date/robot hover remains.

The five named footer tabs are replaced by **five neutral white line indicators**. A longer white marker slides left/right to the selected page in 180 ms, restarting from its current visible position when interrupted. Large transparent click areas, English tooltips/accessibility names, Tab/Enter and Left/Right keyboard navigation remain. Page headings still identify the open feature. Settings remains in the header. Reduce motion snaps the marker; its Qt animation stops once settled and is stopped on panel close. No new dependency or continuously running timer.

Fast Transform no longer displays “One file at a time · Word = .docx” or the permanent temporary-result reminder. Word format information and save/clear behavior are in tooltips. A short status appears only during conversion, when ready to save, or on an error; Save/Clear hides it again. The one-input/one-result limit and four supported workflows remain unchanged.

Verification on 24 October: **38 unit tests passed**, including exact white eye pixels, label-free navigation/tooltips, slide completion, reduced-motion snapping and keyboard selection. Owned-widget appearance, stationary-pointer Music navigation and six real conversion/cleanup checks passed. Captures and JSON are in artifacts/productivity. The new vector/animation UI was not given a new whole-tree memory benchmark; the strict combined 50 MiB ceiling remains unproven and the 23 October memory evidence remains historical.

| Before | After | Why |
| --- | --- | --- |
| Empty black collapsed pill | Two crisp white eye strokes | Owner's corrected identity reference |
| Named footer buttons | White line indicators with short slide | Quieter navigation matching the reference |
| Permanent converter implementation reminders | Tooltips and action-only status | Keep only useful information visible |


## Latest owner decisions — supersede the historical record below

- English primary interface/communication, preserving personal content unchanged.
- iPhone-inspired black native island, top-edge attachment, clean system typography and interruptible/stopped-when-idle springs. Album tint only in open Music while playing; no backdrop allocation. Clock and robot hover remain.
- Fast Transform two columns. Only PNG/JPG→PDF, PDF→MD, PDF→DOCX, DOCX→PDF. One input and one result. Other conversion directions and Notes input explicitly removed.
- Owner confirmed **50 MiB for every Kai process combined, even during conversion**, reducing the converter to one file. This remains a target, not a verified hard guarantee; sample active private WS and committed allocation are reported separately. No feature removals beyond the owner's explicit conversion changes; no forced paging or terminate-on-budget policy.
- Deduplication hashes RGB32 strips to avoid a full second bitmap. Conversion waits for retiring media workers; lyrics are canceled on leaving Music. These are implementation choices, not changes to user data/permissions.


Koreksi Notes paling akhir: pengguna menganggap alur terlalu rumit dan meminta hanya + Catatan, tanpa cari/edit; typo dihapus lalu dibuat ulang. Dipilih satu daftar, input sebaris saat tambah, lingkaran selesai, Hapus/Delete, autosave. Pin melalui klik kanan; tidak ada halaman detail/subheading. Keputusan ini mengungguli referensi judul/checklist kuning dan rancangan Edit sebelumnya.

## Koreksi terakhir: Notes, Transform dan Musik

Pengguna mengoreksi “Shelf” pada referensi checklist menjadi **Notes**; Shelf tidak diubah oleh permintaan visual tersebut. Notes mengikuti daftar dan tampilan isi checklist kuning, lalu pengguna meminta **menghapus subheading/judul besar**. Data/nama catatan tetap, judul hanya pada daftar.

Pengguna menyetujui **mengganti Command sepenuhnya dengan Fast Transform**, PNG/PDF/Word/JPG ke PDF/MD/JPG, maksimal 1–2 ekstraksi lalu dibersihkan. Dipilih satu worker/maksimal dua input/hasil dan cleanup scratch, engine yang sudah tersedia (QtPdf/Windows OCR/stdlib ZIP XML). Word yang didukung DOCX dengan layout sederhana, bukan .doc/Word fidelity penuh; batas dijelaskan di UI/18. Tidak memakai Office COM meskipun terdaftar agar tidak memulai proses Word berat.

Pengguna meminta klik maju/mundur posisi lagu dan naik/turun volume: seek SMTC dan −/+ 5% ditambahkan, tetap worker on demand. Akun/perangkat nyata belum dianggap teruji dari unit/native widget check.

## Keputusan aktif 23 Oktober 2026 — versi 3.0

Koreksi terakhir pengguna: **hapus Sistem karena tidak diperlukan**. Halaman, nav, tray dan jalur task Sistem dihapus. Lima alat + Pengaturan menggantikan cakupan sebelumnya yang mempertahankan Sistem.

Pengguna meminta Clipboard teks/URL saja, Shelf menangani gambar/screenshot/unduhan baru dengan thumbnail/preview dan deduplikasi lintas clipboard/folder; Notes checklist/pin/autosave; contextual mini island tidak mengganggu fokus. Screenshot duplikat diperbaiki di titik intake bersama berdasarkan piksel, original dipertahankan. Referensi `Glossy Robot Capsule Interface.png` kemudian dibatalkan dan diganti `Glossy Sleeping Robot Capsule.png`; pengguna meminta sedikit lebih lebar. Dipilih 72 × 24 DIP dengan dua mata, native Qt statis; jam/logo hover tidak diubah. Penamaan aplikasi 3.0.0 mengikuti permintaan versi 3.0. Detail 17; semua pilihan lama di bawah tunduk pada revisi ini.

Tanggal baseline: 22 Oktober 2026. Jawaban terbaru pengguna mengalahkan asumsi di dokumen ini.

## Keputusan dari sumber

| ID | Keputusan |
| --- | --- |
| D01 | Kai adalah island Windows atas tengah dengan suara lokal; biaya tambahan Rp0 |
| D02 | Python + PySide6 terlebih dahulu; C#/WPF-UI opsional |
| D03 | PTT Ctrl+Space, boleh diganti; hotkey diteruskan ke aplikasi aktif |
| D04 | Whisper lokal dengan Indonesia/Inggris, Melayu digabung ke Indonesia |
| D05 | Auto Medium di NVIDIA, Small di CPU; keputusan kinerja tetap harus diukur |
| D06 | Tanpa Ollama/LLM, tanpa model Handy, tanpa Nemotron sebagai jalur utama |
| D07 | Spotify Premium disebut tersedia; PKCE tanpa client secret; transport fallback Windows |
| D08 | Idle pil hitam; hover expand; collapse sekitar 700 ms setelah kursor pergi |
| D09 | Semua 17 keadaan dalam backlog; urutan fitur sumber 1–8 dipertahankan |
| D10 | Notifikasi WhatsApp tampil saja melalui akses notifikasi Windows |
| D11 | Wake word dan TTS opsional tahap akhir; liquid glass berupa pendekatan visual |
| D12 | Pengguna memasukkan `kai.zip`; arsip sudah ditemukan dan diperiksa |
| D13 | Pengguna meminta gpt-taste, emil-design-eng, ponytail dan pemilihan skill lokal relevan |
| D14 | Pengguna memilih navy dengan glow biru seperti referensi Kai; pilihan ini mengungguli rekomendasi awal kaca tenang |
| D15 | Pengguna mengizinkan implementasi dan meminta smooth popup/hide/reentry; Unlumen, Magic UI, SmoothUI, Skiper, Vengeance menjadi referensi |
| D16 | Setelah melihat prototipe, pengguna meminta ukuran lebih kecil dan material mendekati panel notifikasi Windows; implementasi direvisi ke 320 × 68 DIP dan pil 56 × 20 DIP dengan glow lebih tipis |
| D17 | Pengguna meminta penggunaan RAM rendah untuk harian dan riset pembanding 20–40 MB; metrik UI/model harus dipisahkan, tidak dijanjikan seluruh STT aktif dalam kisaran itu |

## Keputusan dan implementasi lanjutan

- **D18 — pilihan sebelumnya, digantikan D20:** hemat RAM ketika model dibutuhkan. Implementasi mengakhiri proses STT setelah setiap ucapan, tanpa warm cache 60 detik. Tradeoff: loading ulang pada perintah berikutnya.
- **D19 — cakupan kerja:** pengguna meminta lanjut hingga selesai; versi lokal mencakup panel delapan tab, integrasi Windows, penyimpanan dan paket source. Login/izin tetap tindakan eksplisit di pengaturan; tidak mengubah autostart atau mengisi lokasi pengguna.
- **Implementasi rutin:** data/runtime di LOCALAPPDATA; file shelf berupa referensi persisten; kalender lokal + impor ICS tanpa cloud; siklus fokus lanjutan opt-in. Ini pilihan implementasi v1, bukan jawaban personal pengguna terhadap semua pertanyaan di bawah.
- **Revisi P02:** worker proses memang diperlukan untuk melepaskan alokasi Whisper. UI tetap satu proses Python/Qt, tanpa server/web runtime.

- **D20 — pilihan terbaru pengguna:** nonaktifkan mode suara; target RAM harian 20–30 MB. Entry point, launcher dan panel kini tidak memiliki jalur PTT/model aktif. Paket suara dihapus dari requirements aktif, kode dipertahankan sebagai backlog.
- **D21 — jawaban eksplisit pengguna:** “Ya, utamakan 20–30 MiB; media/audio saat dibuka”. Default media/audio hanya pada tab Media, dalam proses yang ditutup setelah tab/panel ditinggalkan. Popup volume/headset otomatis nonaktif di luar tab. Pengaturan dapat mengembalikan mode otomatis jika kelak pengguna memilih biaya RAM lebih tinggi.

## Usulan yang belum disahkan

| ID | Usulan | Alasan |
| --- | --- | --- |
| P01 | Navy/glow sudah dipilih; usulan detailnya glow lembut biasa dan lebih kuat saat listening | Menjaga identitas pilihan pengguna dengan feedback status jelas |
| P02 | Satu proses + worker + queued signal Qt; tanpa IPC awal | Memakai ulang baseline dan menghindari runtime tambahan |
| P03 | `%LOCALAPPDATA%\Kai` + SQLite bawaan untuk data | Data pribadi tidak ikut folder source OneDrive |
| P04 | File shelf mereferensikan path, tanpa move/delete file asli | Jalur paling sederhana dan dapat dipulihkan |
| P05 | Kalender impor `.ics` + acara lokal | Memenuhi baca dan tambah jadwal tanpa integrasi cloud awal |
| P06 | Satu transkripsi aktif; busy state untuk PTT berikutnya | Mencegah hasil bertumpuk dan penggunaan model bersamaan |
| P07 | Timer/alarm lewat deadline persisten; kejadian terlewat tampil setelah resume | Tidak menjanjikan bangun dari sleep tanpa dukungan OS |
| P08 | Fullscreen awal disembunyikan; monitor utama | Mengurangi gangguan; perlu jawaban pengguna |

## Pertanyaan berurutan

Tanyakan bertahap; tidak semuanya memblokir island demo.

| Prioritas | Yang perlu diputuskan | Saran awal | Menghalangi |
| --- | --- | --- | --- |
| 1 | Arah navy/glow sudah dijawab. Avatar karakter wajib atau ikon cukup? Bagaimana navy beradaptasi dengan tema terang? | Ikon dulu; navy dipertahankan dengan kontras yang diuji | Detail visual, bukan pilihan arah utama |
| 2 | Island pada monitor utama atau monitor aktif? Saat game/video fullscreen tetap tampil atau sembunyi? | Monitor utama; sembunyi fullscreen | Perilaku shell |
| 3 | Alarm cukup pulih setelah Kai hidup/resume, atau harus membangunkan laptop/berjalan ketika Kai ditutup? | Pulih sesudah resume; kemampuan lain dipisah | Penjadwal/packaging |
| 4 | Kalender hanya baca `.ics`, tambah acara lokal, atau harus langsung sinkron Google Calendar? | Impor + acara lokal | Fitur kalender |
| 5 | File shelf hanya shortcut sementara atau menyalin file? Harus bertahan setelah restart? | Referensi path; persistensi dipilih saat fitur dibuat | Shelf |
| 6 | Kota cuaca dan sumber `.ics` mana yang ingin digunakan? | Lokasi manual; jangan menganggap Jakarta dari gambar sebagai pilihan | Cuaca/agenda |
| 7 | Pomodoro mengikuti siklus 25/5 dengan jeda panjang setelah empat sesi, atau cukup fokus kustom? | Bahas saat M6a; sumber hanya punya fokus tunggal | Pomodoro lengkap |
| 8 | Mikrofon utama, aplikasi allowlist, artis/lagu untuk HINT_NAMES? Handy masih autostart? | Pilih perangkat saat setup; daftar saat ini contoh | Uji suara personal |
| 9 | Client ID Spotify sudah tersedia dan dashboard dapat dipakai? | Verifikasi lewat setup, jangan kirim token ke chat | Pemutaran lagu spesifik |
| 10 | Prioritas fitur tambahan dan bentuk distribusi portofolio: source, ZIP portable, installer? | Source + demo dahulu; packaging setelah stabil | Rilis |

Spesifikasi laptop tidak perlu ditanyakan ulang: sudah dibaca lokal di 07. Pertanyaan tentang kode/ZIP juga sudah terjawab. Tidak mengubah autostart atau izin perangkat untuk menjawab pertanyaan ini.

## Ketidakselarasan yang telah ditangani dalam rencana

- Klaim island telah ditulis belum didukung isi ZIP: milestone M1 tetap belum dibuat di baseline yang tersedia.
- “Semua offline kecuali Spotify” diperjelas: cuaca/lirik/unduhan juga jaringan.
- Gambar collapse 1–2 detik berbeda dari sumber 0,7 detik: gunakan 0,7 sebagai baseline.
- Impor kalender belum menyelesaikan perintah tambah rapat: kontrak penyimpanan masih perlu pilihan.
- Persistensi tidak membuat alarm bekerja saat proses berhenti/tidur: bedakan restore dengan wake/scheduler OS.
- Konfirmasi aksi besar pada sumber memiliki pengecualian v1 cancel timer/alarm langsung. Saat ini cancel berlaku ke semua item jenis tersebut; target per item perlu ditentukan ketika banyak timer didukung.

## Arahan terakhir: island kaca dan Shelf screenshot

- Pengguna meminta mengganti tampilan biru lama dengan kaca gelap reflektif seperti gambar musik/lirik dan shelf; klik aplikasi langsung tanpa CMD. Implementasi tetap PySide6, Kai.exe hanya launcher GUI kecil.
- Jawaban eksplisit pengguna: pertahankan semua fitur selain WhatsApp/suara. Listener/UI WhatsApp dihapus; suara tidak diaktifkan.
- Logo robot dari Downloads dipakai sebagai identitas aplikasi, tray dan island; konversi ukuran tanpa menggambar ulang.
- Screenshot baru otomatis masuk Shelf agar 4–5 file dapat dipilih dan diseret bersama. Implementasi menyimpan referensi; mengeluarkan pilihan tidak menghapus original. Clipboard-only dan screenshot lama tidak diimpor otomatis.
- Memakai event folder Windows agar tidak ada polling idle. Tidak mengubah pengaturan screenshot, autostart atau izin Windows.

## Koreksi runtime MSIX dan ketajaman logo

Runtime hasil penyiapan dari Codex dialihkan AppData MSIX; Explorer mendapat DirectoryNotFoundException. Launcher memakai fallback lokasi fisik yang sudah ada sambil menjaga direktori data. Pengguna mengonfirmasi error hilang setelah perubahan. Logo Downloads tetap asli; header DPR-aware dan aset island 128 piksel memperbaiki pembesaran pada scaling Windows.

## Revisi productivity 0.3.0

Pengguna mengganti Fokus/Agenda/Waktu/Cuaca dengan Smart Clipboard, Quick Command, Quick Notes dan Smart Shelf; Musik/Sistem tetap ada. Target privat idle terbaru 20–40 MiB. Koreksi setelah preview mengembalikan jam/tanggal/logo pada hover. Ctrl+Alt+Space membuka Command. Klik Musik yang menutup karena geometri mengecil sudah direproduksi dan diperbaiki dengan anchor kursor stasioner; gerakan menjauh tetap auto-hide. Data lama tidak dihapus. Lihat 16 dan 07 untuk implementasi/bukti/batas.
