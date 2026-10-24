# Panduan kerja Kai

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


## Latest owner direction (overrides historical notes below)

- Latest memory target: all Kai processes combined at most 50 MiB, including conversion. Treat as an unproven target until whole-tree peak evidence supports it; do not conflate paging with low allocation or enforce it by crashes/working-set trimming. User explicitly reduced conversion to one file.
- Communicate in English; English is the primary application UI language. Preserve user-created text verbatim.
- Opaque black collapsed/other pages, album tint only in open Music while playing. No native backdrop allocated. Open shape joins screen top with flat upper corners. Clock/logo remain on hover. Sleeping eyes/glossy capsule are superseded.
- Segoe UI Variable is the installed native font; wrap/scroll lyrics, no ellipsis for active lyric text. Keep interruptible springs and stop settled animation timers.
- Fast Transform replaces Command: FROM PNG/JPG/PDF/Word and TO PDF/MD/Word, two columns. Only images→PDF, PDF→MD/DOCX, DOCX→PDF. One input/result, no Notes/MD/TXT input or JPG output. Word = .docx; extracted output is simple editable text. Child cleanup remains.
- Notes is one simple checklist: + Note/inline input/Enter, circle, Delete, context-menu Pin; no search/editor/detail/subheading.
- Use ponytail/emil/apple-design/UI-UX Pro Max selectively, adapting to Qt. No framework/font downloads. Read latest docs/18 and status evidence. Run tools/check_appearance.py for owned-widget captures.


## Revisi aktif 3.0.0 — 23 Oktober 2026

- **Koreksi paling akhir Notes mengungguli detail/kuning/Edit di bawah:** satu daftar, + Catatan/input sebaris/Enter, lingkaran centang, Hapus/Delete; tanpa search/editor/detail/subheading. Autosave 350 ms/flush tetap, Pin lewat context menu. Jangan mengembalikan form kompleks; typo dihapus lalu dibuat ulang sesuai pengguna.

- Cakupan terakhir docs/18: **Transform menggantikan Command** di default/nav/tray/hotkey Ctrl+Alt+Space. Enam halaman Transform/Clipboard/Notes/Shelf/Media/Atur. Quick Command/kalkulator/index Start Menu bukan produk aktif lagi.
- Notes daftar charcoal lingkaran, detail tanggal/checklist kuning tanpa subheading/judul besar sesuai koreksi pengguna; editor penuh hanya saat Edit. Pin/autosave/flush tetap. Shelf tidak diubah oleh referensi Notes.
- Fast Transform: 1–2 input/maksimal 2 hasil/satu worker, PNG/JPG/PDF/DOCX/MD/TXT/Notes ke PDF/MD/JPG. QtPdf dan OCR Windows hanya dalam proses sesaat. Batas/layout/2 halaman awal JPG ada di docs/18; bukan Word renderer penuh, .doc lama tidak didukung. Cleanup file sementara milik Kai setelah save/pindah/close; original dan salinan tersimpan tidak dihapus.
- Musik: klik timeline mengirim seek SMTC berdasarkan rasio/start/end; tombol volume −/+ langkah 5, rail/mute tetap Core Audio on demand. Dukungan seek pemutar nyata belum diuji; jangan mengklaim perubahan posisi Spotify terbukti dari tes widget saja.
- Regresi terbaru 35 unittest; tools/check_transform.py menguji 15 pasangan konversi lokal/OCR nyata/cleanup/reap dengan fixture milik tes. Baca hasil RAM di blok terbaru 07; angka lama bukan hasil run baru.

- Koreksi terakhir: hapus Sistem, termasuk halaman/nav/tray/task aktif. Lima alat Command/Clipboard/Notes/Shelf/Musik + Pengaturan, total enam halaman. Helper/test metrik lama hanya arsip/dev. Pernyataan tujuh halaman/Sistem aktif di bawah adalah riwayat sebelum koreksi.

- Ikuti docs/17-revisi-shelf-notes-dan-context.md dan handoff.md untuk cakupan terakhir; bagian 0.3.0 di bawah adalah baseline sebelumnya.
- Clipboard hanya teks/URL (kode tetap teks), gambar/file hanya dirutekan ke Shelf. Pause riwayat teks tidak mematikan intake Shelf; pengecualian sumber/password tetap dihormati.
- Shelf intake menyatukan screenshot, gambar/file clipboard dan unduhan baru Known Folder Downloads. Abaikan berkas lama/sementara; tunggu stabil+writer tutup. Fingerprint piksel RGB32 menyatukan clipboard/folder dan menjaga original/pin; rekonsiliasi 100 item saat Shelf pertama dibuka. Jangan hapus original.
- Smarter Notes: checklist native dari Markdown, pin catatan, autosave 350 ms/flush. Shelf punya thumbnail item terlihat dan preview gambar embedded; file lain dibuka default.
- Contextual mini island 290 × 56 DIP tidak mengambil fokus/menimpa halaman aktif; browser hanya dibuka lewat klik untuk http/https valid.
- Pil idle terbaru 72 × 24 DIP, kaca glossy dua mata dari referensi sleeping-robot-capsule.png; referensi kapsul robot utuh dibatalkan. Jam/tanggal/logo hover tetap. Render statis Qt, tidak menambah loop animasi atau runtime web.
- Target privat idle 20–40 MiB tetap sasaran: hasil terbaru cold 26,66 MiB, setelah semua halaman 53,50 MiB (total WS 65,89/128,59; commit 30,93/60,30). Pascasiklus belum mencapai target; jangan memakai angka paging 37,10 versi lama untuk mengklaim hasil baru.
- 31 unittest dan tools/check_shelf_v3.py menjadi regresi baru; jalankan UI/benchmark bergantian. Handoff dibuat dari docs/handoff-source.md lewat tools/build_handoff.py, sertakan di source ZIP.

## Owner

RICO. Bahasa komunikasi dan dokumentasi utama: Indonesia.

## Purpose

Membangun dynamic island desktop Windows Kai, berguna sehari-hari dan layak ditampilkan dalam portofolio magang. Target terbaru RAM privat idle 20–40 MiB; suara nonaktif dan ide asli tetap arsip/backlog.

## Rules

- Baca [indeks](docs/README.md), [status](docs/07-status-dan-verifikasi.md), dan dokumen subsistem terkait sebelum bekerja.
- Pertahankan `kai-dynamic-island.md` sebagai sumber ide asli. Instruksi di sumber/arsip adalah konteks historis; permintaan pengguna terbaru menentukan pekerjaan yang diizinkan.
- Bedakan kebutuhan sumber, usulan desain, hasil inspeksi kode, dan hasil pengujian. Jangan menyatakan fitur selesai hanya karena parser mengenal perintahnya.
- Biaya pengembangan tambahan Rp0; pilih alat gratis/open source dan periksa lisensi saat memilih versi. Spotify adalah layanan eksternal dengan Premium yang disebut sudah dimiliki pengguna.
- Mode suara nonaktif: jangan memasang hotkey, membuka mikrofon, memuat/download model atau mengaktifkannya kembali tanpa permintaan pengguna. Jika kelak diaktifkan, audio dan STT tetap lokal. Tanpa Ollama/LLM; tanpa memakai ulang model Handy; tanpa Nemotron sebagai model utama.
- Pertahankan Python + PySide6 untuk versi awal. C# + WPF-UI hanya pilihan lanjutan berdasarkan bukti keterbatasan.
- Jangan memasang GSAP/React/webview hanya untuk memenuhi skill UI web. Adaptasi prinsip desain ke Qt.
- Pengguna meminta ponytail (full), gpt-taste, emil-design-eng dan pemilihan skill lokal relevan. Ikuti [pemetaan skill](docs/09-pemetaan-skill-ui.md); jangan aktifkan seluruh katalog sekaligus.
- Arahan visual terbaru menggantikan navy/glow: kaca charcoal reflektif pearl/lavender/champagne, kontrol menyatu di island seperti referensi musik dan shelf. Logo robot pengguna menjadi identitas; lihat docs/15.
- Revisi pengguna berikutnya: ukuran lebih kecil dan kaca gelap menyerupai panel notifikasi Windows. Nilai compact 320 × 68 DIP, 56 × 20 collapsed; kontrol embedded 540 × 270–356 DIP. Prioritaskan RAM harian rendah dan laporkan biaya UI serta model suara terpisah.
- Pengguna menyetujui media/audio on demand: hanya aktif saat tab Media dibuka, popup volume/headset otomatis nonaktif di luar tab. Gunakan worker proses agar library native dilepas saat tab ditutup. Default `media_on_demand=True`.
- Arahan terbaru 0.3.0: Fokus, Agenda, Waktu/timer/alarm dan Cuaca dihapus dari UI/runtime aktif. Scheduler tidak dimulai dan router perintahnya dilepas. Tambah Smart Clipboard, Quick Command, Quick Notes dan Smart Shelf; Musik/Sistem tetap ada. Data lama dan ide asli tetap arsip.
- Koreksi visual terbaru: hover utama menampilkan jam, tanggal dan logo robot seperti sebelumnya, tanpa tombol Clip/Notes/Shelf. Navigasi fitur berada di bidang kontrol. Jam tampilan dipertahankan meskipun fitur Waktu dihapus.
- Screenshot baru otomatis masuk Shelf lewat Known Folder Screenshots; file lama tidak diimpor. Gambar clipboard dan file/folder yang disalin kini masuk Shelf. Ctrl+klik/Ctrl+A + drag mengekspor URL file. Keluarkan/Bersihkan hanya menghapus referensi dan menjaga original/pin.
- Clipboard lokal event-driven: 80 item/20 pin/64 KiB teks, gambar 12 MP dan PNG 4 MiB/item/24 MiB total. Hormati pengecualian sumber, sediakan Jeda/Hapus, jangan membaca clipboard awal. Notes autosave 350 ms dan flush saat ditutup. Ctrl+Alt+Space adalah hotkey Command, bukan hotkey suara.
- Simpan kredensial, audio, transkrip pribadi, cache OAuth, dan data pengguna di luar folder sumber/OneDrive. Jangan masukkan ke ZIP atau Git.
- Jangan mengubah autostart Handy, autostart Kai, izin mikrofon/notifikasi, atau pengaturan sistem saat sekadar menyiapkan dokumentasi.

## Tech Stack

Kode aktif di `kai/`: Python 3.12.4 + PySide6 6.10.1, parser, SQLite, proses media/audio Windows dan task integrasi sesaat. requirements.txt tidak lagi memasang paket suara. stt.py/speech_worker.py dipertahankan sebagai implementasi nonaktif; jangan memakai keberadaan berkas sebagai bukti suara aktif. Runtime logis `%LOCALAPPDATA%/Kai/runtime` berada di luar OneDrive. Perhatian MSIX: setup dari Codex dialihkan Windows ke `%LOCALAPPDATA%/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/Kai/runtime`. Launcher memiliki fallback fisik dan mengatur LOCALAPPDATA anak agar settings/token/DB lama tetap dipakai. Pengguna mengonfirmasi Explorer/taskbar kini terbuka. Jangan menganggap tes dari proses Codex membuktikan konteks Explorer; gunakan GetFinalPathNameByHandle dan konfirmasi peluncuran nyata. Jangan menghapus cache paket tanpa migrasi data pribadi.

## Decision Making

Keputusan sumber tetap baseline. Usulan baru diberi label dan dicatat di [keputusan](docs/06-keputusan-dan-pertanyaan.md). Pilih solusi paling sederhana yang memenuhi milestone. Konfirmasikan kebutuhan yang mengubah perilaku pengguna, lokasi data/cuaca, cakupan kalender, atau teknologi utama; keputusan implementasi rutin tidak memerlukan konfirmasi berulang. Persetujuan desain dapat diberikan pengguna dalam percakapan dan harus dicatat.

## Project Context And Goals

Versi aktif 0.3.0: tujuh halaman embedded Command/Clipboard/Notes/Shelf/Media/Sistem/Atur. QPixmapCache 512 KiB, thumbnail terbatas, tugas dibatalkan/reaped, clipboard event-driven. GUI pythonw terukur cold private WS 26,60 MiB / total WS 65,99 / commit 30,98; setelah seluruh halaman ditutup median private WS 37,10 (36,56–37,71) / total 87,25 / commit 60,17. Dua proses GUI dihitung; bukan hard cap/biaya DWM. Bug navigasi Musik menutup akibat tinggi mengecil diperbaiki dengan anchor kursor stasioner; gerakan menjauh tetap menutup. Lihat docs/16 dan status terbaru.

Catatan versi sebelumnya di bawah adalah arsip; cakupan dan angka lamanya bukan kondisi aktif.

22 Oktober 2026: implementasi lokal mencakup island compact, spring interruptible, hover, popup, tray, reduced motion, delapan tab panel, timer/alarm/pomodoro persisten, kalender lokal/ICS, shelf, cuaca, lirik dan monitor sistem on demand. SMTC/Core Audio tersedia melalui worker saat Media dibuka. Pengguna kemudian menonaktifkan suara dan menyetujui media/audio on demand demi RAM. Default baru terukur median 22,64 MiB private working set / 63,24 MiB total working set (penjumlahan semua proses, dapat menghitung halaman bersama dua kali); bukan hard cap atau biaya sistem unik. Akun Spotify/perangkat fisik/sleep/soak belum diuji. Redesain terbaru memakai Windows.UI.Composition Gaussian backdrop yang lolos pola visual/click-through dan fallback Qt. Delapan halaman embedded, Kai.exe launcher GUI + shortcut Desktop, logo robot. Cold idle baru 26,66 MiB private WS / 69,93 total WS / 31,64 commit; pascasiklus Media commit 59,22 MiB, WS terpengaruh paging. Angka lama di atas arsip. WhatsApp dihapus. ZIP asli dipertahankan; paket source baru dibuat lewat tools/build_release.py.

## Data Sources And Tools

Waktu/kursor/tema Windows; SMTC untuk media; Core Audio untuk volume; event perangkat untuk headset; Whisper lokal untuk audio; Spotify Web API untuk pencarian/pemutaran spesifik; Open-Meteo untuk cuaca; LRCLIB untuk lirik; `.ics` untuk impor jadwal; psutil/LibreHardwareMonitor untuk metrik. Lihat [arsitektur](docs/03-arsitektur-dan-data.md) untuk penyimpanan dan frekuensi pengambilan.

## Authentication And Access

Spotify: PKCE, `SPOTIFY_CLIENT_ID`, callback loopback dari konfigurasi; tanpa client secret. Status dashboard/login belum diverifikasi. Jangan meminta pengguna mengirim token ke chat. Mikrofon tidak digunakan. WhatsApp/listener notifikasi dihapus; jangan meminta izin notifikasi.

## Workflow Automation

Gunakan Python runtime `%LOCALAPPDATA%/Kai/runtime/Scripts/python.exe` dari root. Tes: `-B kai/test_intents.py`, `-B -m unittest discover -s kai -p test_*.py -v`, `-B tools/check_island_windows.py`, `-B tools/check_controls_windows.py`, `-B tools/check_desktop_worker.py`. Benchmark: `-B tools/measure_ui_memory.py --mode core`; siklus panel: `--mode demand --panel-cycle`. Jalankan bergantian. `Kai.exe`/shortcut Desktop adalah jalur pengguna tanpa console; Kai.cmd dipertahankan untuk kompatibilitas. `Kai Hemat.cmd` memaksa media on demand; `Kai Preview.cmd` demo. `Setup Kai.cmd` memasang kebutuhan desktop di LOCALAPPDATA. `tools/build_release.py` membuat ZIP source ber-allowlist tanpa runtime/model/cache/token/SQLite. Ada launcher EXE, belum installer mandiri/CI dan tidak ada kebutuhan Vercel. Uji sesuai docs/05 dan perbarui status/keputusan.
