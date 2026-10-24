# Kai — island produktivitas Windows

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


**Memory budget:** all-process 50 MiB remains unproven. See docs/07-status-dan-verifikasi.md for current resident/committed measurements. Older scope descriptions below the latest English contract are historical.

## Latest approved UI — 23 October 2026

English is now the primary interface language: navigation, settings, buttons, tooltips, clipboard/notes/Shelf statuses and conversion errors. Personal notes, copied text, filenames and song lyrics are never translated. Historical Indonesian documentation and inactive feature code remain archives.

The collapsed island is **plain opaque black, 72 × 24 DIP**. Other pages and the clock/logo hover are black. Opening the island brings its top edge to the physical screen edge, with flat upper corners and rounded lower corners. Clock/date and the user's robot identity remain on hover. The previous sleeping-eye/glossy capsule is superseded. While **Music is open and playing**, a static dark gradient follows the album cover; paused/no-cover/other pages return to black. A single 8 × 8 average is calculated from the already bounded 64px cover when the track/cover becomes available. No large blur, animation loop or extra image cache. Native composition/backdrop surfaces are no longer created for this opaque design.

Typography uses installed **Segoe UI Variable**; Qt confirmed this family resolves correctly. It follows the iPhone reference's clean hierarchy using Windows typography. Spring transitions retain velocity on reversal, stop when settled and respect Reduce motion. Long active lyrics wrap without ellipsis; a small scrollbar/wheel makes overflow accessible. Adjacent lines may scroll out of the viewport. Reference photos are retained in docs/references/music-lyrics-top-edge.jpg, iphone-island-motion.jpg and iphone-island-calendar.jpg; the calendar picture is visual inspiration and does not restore Calendar.

Fast Transform has **FROM / TO columns** and a center divider. FROM: PNG/JPG/PDF/Word; TO: PDF/MD/Word. Only the approved workflows remain: **JPG or PNG → PDF; PDF → MD; PDF → Word (.docx); Word (.docx) → PDF**. One input file and one output per job. PDF-to-JPG, other conversions, Notes input and MD/TXT input are removed. Incompatible output buttons are disabled automatically. PDF→Word extracts editable text; Word→PDF preserves basic paragraphs/headings/tables/images, with complex layout limits. No Word process or new dependency. Save or Clear removes temporary results; leaving/closing also cleans up after cancellation/reap. Original files and saved copies are retained.

Skills used selectively: ponytail full, emil-design-eng, apple-design and UI/UX Pro Max. The latter's design-system search was run; its landing-page/blue palette/web-font suggestions were discarded because the user's approved black native desktop brief takes precedence. Applied checks: grouping, contrast, pressed/focus/selected states, keyboard access, bounded image work and reduced motion. No web UI framework installed.

Verification: 37 unit tests plus six conversion fixture checks cover PNG/JPG→PDF, PDF→MD/DOCX, DOCX→PDF and scanned PDF→MD with real local Windows OCR. Disposable engine isolation/reap, one-file restriction, unsupported direction rejection, save/cleanup/cancel and English labels are checked. Native hover/click-through/focus/reentry/reversal and six-page navigation pass at current 150% DPI. tools/check_appearance.py captures owned widgets with generated cover/lyrics, verifies column fit, wrapping, top-edge attachment, installed font and disabled backdrop. Account playback/seek was not mutated. See the latest status for measured memory and its limits.


**Notes terakhir:** cukup + Catatan → ketik → Enter, centang selesai, atau Hapus. Tanpa cari, editor, detail maupun subheading. Autosave tetap; Pin lewat klik kanan. Ini mengungguli rancangan Notes detail di bagian riwayat berikut.

Pembaruan terakhir: **Fast Transform menggantikan Command**. Ubah PNG/JPG/PDF/Word (.docx)/Notes/MD/TXT ke PDF/MD/JPG; maksimal dua input/hasil, worker sesaat dan hasil sementara dibersihkan saat simpan/pindah/tutup. Layout Word sederhana; .doc lama perlu .docx. Ctrl+Alt+Space membuka Transform. Notes kini daftar lingkaran/detail checklist kuning **tanpa subheading**. Musik mendukung klik progress seek dan volume −/+ serta rail. [Kontrak 18](docs/18-notes-transform-dan-musik.md) memuat batas/OCR/layout dan bukti; daftar Command di bagian lama berikut adalah arsip.

## Aktif 3.0.0 — 23 Oktober 2026

**Sistem sudah dihapus** sesuai permintaan terakhir. Navigasi sekarang Command, Clipboard, Notes, Shelf dan Musik, ditambah Pengaturan; enam halaman. Tidak ada task pengambilan metrik Sistem pada runtime produk.

Clipboard **teks/URL saja**; gambar/file ada di Smart Shelf. Shelf menyatukan screenshot clipboard+folder berdasarkan isi piksel, menerima unduhan baru yang selesai di Known Folder Downloads, dan menyediakan thumbnail/preview gambar asli. Smarter Notes menambah checklist clickable dan pin, dengan autosave tetap. Contextual mini island menawarkan Shelf/browser tanpa mengambil fokus. Pil idle terbaru kaca glossy dua mata **72 × 24 DIP**; hover jam/tanggal/logo tetap.

31 unittest dan native revisi 3.0 lulus. RAM privat cold **26,66 MiB**; pascasiklus seluruh halaman **53,50 MiB**, jadi target idle 20–40 belum terpenuhi setelah siklus. Total/commit dan batas uji di status 07. Angka/cakupan 0.3.0 di bawah adalah riwayat, terutama gambar di Clipboard dan ukuran idle lama.

Panduan lengkap: [handoff](handoff.md), [revisi 3.0](docs/17-revisi-shelf-notes-dan-context.md), [cara pakai](docs/14-panduan-pakai.md). Regresi baru: `tools/check_shelf_v3.py`. Handoff dapat dibuat ulang lewat `tools/build_handoff.py`.

Hover menampilkan **jam, tanggal dan logo Kai**. Klik kartu atau **Ctrl+Alt+Space** membuka kontrol di dalam island, tanpa CMD. Jalankan Kai.exe atau shortcut Desktop/taskbar. Klik kanan tray → Keluar Kai untuk berhenti.

## Fitur aktif 0.3.0

- **Quick Command:** pencarian shortcut aplikasi Start Menu, pembuka path/URL, kalkulator aritmetika, perintah musik/volume. Bukan shell arbitrer.
- **Smart Clipboard:** riwayat teks/link/kode/gambar, search, pin, salin/tempel, jeda dan hapus. Lokal, 80 item, 20 pin, teks 64 KiB; PNG maksimal 4 MiB/item dan 24 MiB total.
- **Quick Notes:** tambah, edit, cari, tandai selesai, hapus; autosave 350 ms serta flush saat ditutup. Maksimal 20.000 karakter/catatan.
- **Smart Shelf:** screenshot otomatis, drop file/folder, file/gambar clipboard, pencarian/filter/favorit dan drag beberapa file. Ctrl+klik/Ctrl+A memilih; Keluarkan/Bersihkan hanya menghapus referensi. Pin dipertahankan ketika Bersihkan.
- **Musik:** SMTC, transport, volume/mute, lirik atas permintaan dan Spotify PKCE. Worker hanya ketika Musik dibuka.
- **Sistem:** CPU/RAM/baterai/disk/GPU, laju jaringan dan lima proses RAM teratas; snapshot melalui proses sesaat.

Fokus/pomodoro, Agenda, Waktu/timer/alarm dan Cuaca sudah dilepas dari UI/runtime aktif. **Jam tampilan tetap ada** sesuai koreksi pengguna. WhatsApp/suara tetap nonaktif; tanpa mikrofon/model. Data lama dipertahankan.

## Tampilan dan RAM

Idle 56 × 20 DIP; hover 320 × 68; toast singkat 290 × 56; halaman menyesuaikan tinggi. Charcoal glass, logo asli, spring interruptible dan reduced motion. Bug Musik menutup akibat panel memendek sudah diperbaiki: kursor diam dipertahankan, gerakan menjauh tetap auto-hide.

Jalur GUI pythonw: cold idle **26,60 MiB private working set** dan median **37,10 MiB setelah seluruh halaman ditutup**. Target privat idle 20–40 tercapai dalam sampel lokal. Total WS 65,99/87,25 MiB; private commit 30,98/60,17 MiB. Dua proses GUI dihitung; DWM/sistem tidak termasuk dan WS total dapat menghitung halaman bersama dua kali. Bukan hard cap saat fitur aktif; tanpa trim paksa.

28 unittest lulus. Native checks mencakup hover/retarget/fokus/click-through, tujuh halaman embedded, clipboard/gambar/pause, autosave/flush, lima screenshot/payload drag lima file, shortcut, Ctrl+V pada target uji dan worker reaped. Akun Spotify, perangkat fisik, semua aplikasi tujuan, monitor/DPI lain dan soak harian masih membutuhkan penggunaan nyata.

## Runtime dan panduan

Runtime laptop ini sudah tersedia. Launcher menangani lokasi normal serta fallback cache MSIX Codex, terverifikasi oleh pengguna. Paket bukan installer mandiri: pada komputer baru pasang Python 3.12 x64 dan jalankan Setup Kai.cmd dari Explorer. Jangan memindahkan hanya EXE tanpa folder kai/assets. Autostart tidak diubah.

Lihat [panduan pakai](docs/14-panduan-pakai.md), [status](docs/07-status-dan-verifikasi.md), [desain productivity](docs/16-kai-productivity.md), dan [notice](THIRD_PARTY_NOTICES.md).

## Pengembang

Gunakan Python runtime LOCALAPPDATA/Kai/runtime/Scripts/python.exe dengan -B. Tes dan benchmark dijalankan bergantian:

- `-m unittest discover -s kai -p test_*.py`
- `tools/check_productivity.py`, `tools/check_navigation.py`
- `tools/check_island_windows.py`, `tools/check_controls_windows.py`, `tools/check_desktop_worker.py`
- `tools/measure_ui_memory.py --mode core` dan `--mode demand --panel-cycle`
- `tools/build_launcher.py`, `tools/build_release.py`

Benchmark memakai pythonw dan data sementara agar tidak menabrak sesi pengguna. Tes UI menggunakan data/clipboard palsu dan widget sendiri. Parser/kalender/suara lama dalam suite adalah arsip regresi, bukan fitur aktif.
