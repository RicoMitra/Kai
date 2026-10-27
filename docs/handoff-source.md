# Handoff Kai — dari ide awal hingga versi 3.0

## Lyrics lookup correction — 24 October 2026

LRCLIB's expected HTTP 404 for a missing catalog match previously propagated as a raw task error. Kai now tries one bounded search after that response, accepts only normalized title/artist matches and a duration within two seconds when known, and renders distinct missing, instrumental and temporary-failure states. Plain lyrics are no longer labeled as synchronized. Positive results retain the existing 50-track disk bound; missing entries expire after six hours and transient errors back off for one minute, with retry available on click. Corrupt cache JSON is refetched. No new library, resident worker or polling timer is added. Exact live/remaster mismatches are deliberately not guessed.

Verification: **44 unit tests passed**, including five isolated LRCLIB/cache matching tests and a widget test proving that unavailable/instrumental/retry messages replace old lyric layouts and hide stale scrolling. Appearance checks also passed. Live read-only API probes returned a known track successfully and a synthetic absent track as get=404/search=200 with zero records; a separate transient attempt produced the retry state. Only status/counts were inspected; copyrighted lyric text was not copied into the repository. No account playback was changed. These checks do not establish catalog coverage for every new song. Primary API contract: https://lrclib.net/docs.

## Private GitHub publication — 24 October 2026

Owner requested publication to a private `RicoMitra/Kai` repository and a complete English explanation. The owner's external privacy guidance was read before publication and is not copied into the repository. Kai now has its own project-root Git history; the inherited user-folder repository and placeholder remote are untouched. Local commits use a GitHub noreply identity.

`README.md` is now generated from **`docs/readme-source.md`** by `tools/build_readme.py`, covering the current experience, all five feature destinations/Settings, four conversion workflows, setup, data paths, architecture, tests, memory evidence and limitations. **`docs/history/README-before-github.md`** preserves the previous root README. **`SECURITY.md`** states the actual desktop security model, local plaintext-at-rest limitation and reporting rules. **`docs/19-github-and-privacy.md`** maps every item of the owner's privacy checklist to applicable controls, scope, findings and remaining work. **`docs/20-kai-4-dynamic-island.md`** is the active Kai 4.0 design reference: floating Dynamic Island capsule, Apple system accents, spring/eye/magnet/slide motion tokens, logo-only-as-app-icon rule and acceptance limits.

The initial direct audit was clean, but the installed active closure revealed advisories in requests/urllib3/idna/certifi. Security-pinned versions 2.33.0/2.8.0/3.15/2026.10.19 are installed only inside Kai's runtime and pinned in requirements; older global Python packages remain untouched. pip-audit 2.10.1 then reported no known vulnerabilities across the 26-package active Python closure, without skipped packages. `tools/export_active_dependencies.py` reproduces that closure without scanning unrelated global speech/development packages. `artifacts/productivity/dependency-audit-verification.json` records package versions and advisory IDs without secrets. Gitleaks staged/history scans are required before push; reports and tooling remain outside the project. Weekly dependency checks are configured in `.github/dependabot.yml`.

Runtime/databases/settings/OAuth/cache/logs/models, original ZIPs, reference photos and generated release ZIPs are ignored by Git. Only selected generated-fixture screenshots and evidence are published. Historical documents can contain workstation paths or references to local-only material; review again before any later public visibility change. There is still no application-level local-data encryption and no verified 50 MiB whole-tree hard ceiling. Publication is not a claim that those engineering goals are finished.


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


## Final saved state and owner-requested shutdown

The final run passed 37 unit tests, six conversion checks, the owned-widget appearance check and Shelf/Notes/context acceptance (dedupe both orders/legacy repair, downloads, thumbnails, autosave and no focus stealing). The Shelf acceptance initially exceeded its five-second waits under load with tiny eight-row hash tiles; changing the tile to 64 rows reduced Qt call overhead while retaining a bounded strip buffer and exact digest, and the final acceptance passed. Native hover/navigation/worker checks from this work are retained separately; actual Spotify account playback/volume was not mutated.

Owner asked to close Kai and GPT-related applications because the laptop is lagging. The real Kai GUI processes and its owned child were closed, without restarting the app. Documentation/handoff/source ZIP are saved. Codex/ChatGPT close is scheduled only after the final message, with Task Manager left open and unrelated apps excluded. Reopen Kai.exe from the project folder when ready. The 50 MiB combined-process hard ceiling remains unresolved; preserve this limitation during handoff, do not describe it as complete.


## Latest verification and memory target — 23 October 2026

Current UI: English; black collapsed/other pages; album tint only in open, playing Music; wrapped/scrollable lyrics; flat upper corners attached to screen top. Notes is a simple checklist. Fast Transform has four workflows only: PNG/JPG→PDF, PDF→MD, PDF→DOCX, DOCX→PDF; one input and one output. Unsupported directions/Notes input were removed at the owner's request. Settings/clock/robot/Shelf/clipboard/music remain.

The owner explicitly targets **50 MiB for all Kai processes combined, including conversion**. This is **not a verified hard ceiling**. Latest whole-tree sample including media startup, all four conversion workflows and scanned-PDF OCR: **23.33 MiB peak private working set**, **39.39 MiB peak total working set**, **93.41 MiB peak private committed memory**. Sampled every 100 ms, maximum three simultaneous processes, generated 1600×900 image and one-page PDFs, harness excluded. Windows paging explains why resident memory can look far lower than allocated memory. Sampling misses short peaks; larger inputs, sustained use, different memory pressure, other monitors/DPI and compositor costs are not covered. No working-set trimming or memory-limit crash policy used. **Do not claim the all-input 50 MiB requirement achieved.**

Latest idle benchmark before the final conversion-direction restriction: startup private commit median 30.31 MiB; after all six pages close, 37.88 MiB. Private resident medians 1.12/1.58 MiB reflect severe paging, not a claim that Kai only needs 1–2 MiB. These are short tests, not a universal budget.

Implemented reductions: no backdrop/composition allocation for opaque black, one conversion worker, media worker reaped before conversion begins, lyrics task canceled outside Music, RGB32 dedupe in 64-row strips instead of another full bitmap, tiny bounded album-color sample, native delegate rows, bounded thumbnails and stopped idle animation timer. PDF text extraction uses QCoreApplication in its disposable worker, avoiding a GUI font environment; DOCX→PDF still uses Qt text/layout, scanned PDF extraction still uses local Windows OCR. One-file concurrency does not cap the memory required to decode that one file.

Evidence: artifacts/island/memory-active-verification.json; memory-core.json; memory-demand-after-panel.json; artifacts/productivity/transform-verification.json and appearance-verification.json. tools/measure_active_memory.py generates isolated fixtures, opens the real media worker read-only and measures the GUI/redirector/all descendants. No private user files, clipboard, login or account playback changes are used. tools/check_appearance.py verifies the final layout with synthetic artwork/lyrics. Remaining strict-budget work would require profiling and proving a lower-memory native conversion implementation; a framework rewrite is not automatically a guarantee and was not performed.

Sources checked: [Microsoft Working Set](https://learn.microsoft.com/en-us/windows/win32/memory/working-set), [SetProcessWorkingSetSize](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsize), [Qt QImageReader](https://doc.qt.io/qt-6/qimagereader.html). Working-set trimming affects paging; it does not remove the underlying allocations. Decoder scaling savings depend on the image format/plugin.


## Latest approved UI — 23 October 2026

English is now the primary interface language: navigation, settings, buttons, tooltips, clipboard/notes/Shelf statuses and conversion errors. Personal notes, copied text, filenames and song lyrics are never translated. Historical Indonesian documentation and inactive feature code remain archives.

The collapsed island is **plain opaque black, 72 × 24 DIP**. Other pages and the clock/logo hover are black. Opening the island brings its top edge to the physical screen edge, with flat upper corners and rounded lower corners. Clock/date and the user's robot identity remain on hover. The previous sleeping-eye/glossy capsule is superseded. While **Music is open and playing**, a static dark gradient follows the album cover; paused/no-cover/other pages return to black. A single 8 × 8 average is calculated from the already bounded 64px cover when the track/cover becomes available. No large blur, animation loop or extra image cache. Native composition/backdrop surfaces are no longer created for this opaque design.

Typography uses installed **Segoe UI Variable**; Qt confirmed this family resolves correctly. It follows the iPhone reference's clean hierarchy using Windows typography. Spring transitions retain velocity on reversal, stop when settled and respect Reduce motion. Long active lyrics wrap without ellipsis; a small scrollbar/wheel makes overflow accessible. Adjacent lines may scroll out of the viewport. Reference photos are retained in docs/references/music-lyrics-top-edge.jpg, iphone-island-motion.jpg and iphone-island-calendar.jpg; the calendar picture is visual inspiration and does not restore Calendar.

Fast Transform has **FROM / TO columns** and a center divider. FROM: PNG/JPG/PDF/Word; TO: PDF/MD/Word. Only the approved workflows remain: **JPG or PNG → PDF; PDF → MD; PDF → Word (.docx); Word (.docx) → PDF**. One input file and one output per job. PDF-to-JPG, other conversions, Notes input and MD/TXT input are removed. Incompatible output buttons are disabled automatically. PDF→Word extracts editable text; Word→PDF preserves basic paragraphs/headings/tables/images, with complex layout limits. No Word process or new dependency. Save or Clear removes temporary results; leaving/closing also cleans up after cancellation/reap. Original files and saved copies are retained.

Skills used selectively: ponytail full, emil-design-eng, apple-design and UI/UX Pro Max. The latter's design-system search was run; its landing-page/blue palette/web-font suggestions were discarded because the user's approved black native desktop brief takes precedence. Applied checks: grouping, contrast, pressed/focus/selected states, keyboard access, bounded image work and reduced motion. No web UI framework installed.

Verification: 37 unit tests plus six conversion fixture checks cover PNG/JPG→PDF, PDF→MD/DOCX, DOCX→PDF and scanned PDF→MD with real local Windows OCR. Disposable engine isolation/reap, one-file restriction, unsupported direction rejection, save/cleanup/cancel and English labels are checked. Native hover/click-through/focus/reentry/reversal and six-page navigation pass at current 150% DPI. tools/check_appearance.py captures owned widgets with generated cover/lyrics, verifies column fit, wrapping, top-edge attachment, installed font and disabled backdrop. Account playback/seek was not mutated. See the latest status for measured memory and its limits.


## Earlier implementation notes (historical)

The current English interface, four workflows and single-file limit above supersede the multi-format/Notes/two-file descriptions below. The original decisions are retained to explain the development history.

## Cakupan terakhir yang mengungguli catatan sebelumnya

**3.0.0, 23 Oktober 2026:** enam halaman **Transform, Clipboard, Notes, Shelf, Musik, Atur**. Fast Transform menggantikan Command sepenuhnya di nav/tray/default/Ctrl+Alt+Space; indeks aplikasi/kalkulator bukan fitur produk lagi. Sistem tetap dihapus. Scope suara/WhatsApp/waktu/fokus/cuaca/agenda tetap nonaktif.

**Notes paling akhir:** hanya satu daftar, + Catatan dan Hapus, lingkaran untuk selesai. Tidak ada cari catatan, editor, detail atau subheading. + Catatan menampilkan satu input; ketik lalu Enter, autosave 350 ms/flush tetap. Typo dihapus lalu dibuat ulang. Pin lewat klik kanan agar toolbar ringkas. Rancangan split-editor/detail kuning pada bagian riwayat di bawah sudah dibatalkan pengguna. Referensi yang sempat disebut Shelf dikoreksi menjadi Notes, jadi Shelf tidak diubah oleh gambar checklist tersebut.

**Fast Transform:** 1–2 input dan maksimal 2 hasil, PNG/JPG/PDF/DOCX/Notes/MD/TXT → PDF/MD/JPG/DOCX. Worker satu proses sesaat; QtPdf/OCR Windows hanya di anak dan direap. Simpan/Bersihkan/proses baru/pindah/tutup membersihkan scratch setelah worker selesai. Original dan salinan tersimpan tidak dihapus. .doc lama perlu .docx; DOCX memiliki layout sederhana, JPG dokumen maksimal dua halaman awal, PDF maksimal 50 halaman, ukuran input 20 MiB/file. OCR bergantung bahasa Windows yang tersedia (en-GB/en-US pada laptop ini), tanpa model baru/cloud.

**Musik:** progress bisa diklik untuk seek maju/mundur, volume −/+ langkah 5 dan rail drag/mute, tetap Core Audio/SMTC on demand. Dukungan pemutar nyata belum dibuktikan dari tes widget. **37 unittest** dan 20 pasangan konversi fixture/OCR nyata/cleanup/reap lulus. Angka RAM terbaru dan konteks paging ada di blok teratas 07, bukan hard cap.

Dokumen tambahan **`docs/18-notes-transform-dan-musik.md`** menjelaskan referensi Notes dan koreksi sederhana terakhir, penggantian Command, matriks konversi, batas/layout/OCR/cleanup, musik seek/volume, bukti dan sumber primer. Mengungguli cakupan Notes/Command pada 16/17.

Modul baru **`kai/transform.py`**: QPdfWriter/QtPdf, gambar bounded, OCR Windows, parser ZIP/XML DOCX (paragraf/heading/tabel/gambar), hanya dalam worker. **`kai/test_transform.py`**: Note→PDF→MD, batas dua input dan engine tidak di parent. **`tools/check_transform.py`**: 20 pasangan konversi asli milik tes, OCR, DOCX gambar/tabel, save membersihkan sementara/pindah membatalkan/salinan tetap/worker reaped. **`product_pages.py`** kini memuat NotesPage sederhana dan TransformPage; CommandPage dihapus. `quick_command.py` hanya helper regresi/arsip. `tasks.py` melayani transform sesaat dengan cleanup; Task di panel mempunyai event selesai untuk urutan cancel/reap/delete yang aman.

Cara pakai terbaru: klik island/Ctrl+Alt+Space → Transform; pilih/drop 1–2 file atau Dari Notes → format PDF/MD/JPG/DOCX → Ubah → Simpan hasil sebelum pindah/tutup. Shelf → pilih maksimal dua file → Ubah. Notes → + Catatan → ketik/Enter; lingkaran/Space centang, Hapus/Delete untuk membuang, klik kanan untuk Pin. Tidak ada halaman Edit. Cara kerja lama Command/detail Notes di bawah adalah jejak tahap pengembangan, bukan UI aktif.

Regresi tambahan: `tools/check_transform.py`, lalu `tools/check_shelf_v3.py` dan suite test_*.py. Jalankan native UI/benchmark bergantian. DOCX/PDF kompleks, seluruh pemutar/perangkat fisik, DPI lain, bahasa OCR selain yang tersedia dan soak harian belum tervalidasi. Untuk rilis gunakan build_handoff.py kemudian build_release.py; source ZIP menyertakan modul/test/docs baru tanpa data pribadi.

Disusun 23 Oktober 2026 untuk RICO dan pengembang/agen penerus. Root proyek: `C:/Users/RICO/OneDrive/ドキュメント/RICO/Kai`. Seluruh path relatif di dokumen ini berangkat dari root tersebut. Handoff adalah peta proyek dan keputusan, bukan perintah untuk mengaktifkan ulang fitur historis. Lampiran hasil generator mencatat setiap MD beserta semua judul bagiannya dan inventaris file proyek.

## 1. Kondisi yang harus dipahami dahulu

Kai adalah dynamic island desktop Windows, ringkas di atas tengah layar, untuk membantu aktivitas sehari-hari dan menjadi karya portofolio magang. Versi aktif **3.0.0** mempertahankan Python 3.12.4 + PySide6 6.10.1 dan lima alat: Fast Transform, Clipboard, Smarter Notes, Smart Shelf dan Musik; Pengaturan adalah halaman keenam. **Sistem dihapus atas permintaan terakhir pengguna**, termasuk navigasi, tray dan task aktif. Buka `Kai.exe`, bukan console. Hover memperlihatkan jam/tanggal/logo robot; klik atau Ctrl+Alt+Space membuka kontrol di dalam island.

Permintaan terbaru mengalahkan dokumen awal: Clipboard hanya teks/URL; gambar/screenshot/file masuk Shelf; unduhan baru masuk otomatis; Notes memiliki checklist dan pin. Pil idle mengikuti referensi **Glossy Sleeping Robot Capsule**, dua mata putih/lavender dalam kaca gelap, **72 × 24 DIP**. Referensi kapsul dengan robot utuh sebelumnya dibatalkan. Hover tetap 320 × 68 DIP, toast 290 × 56, bidang kontrol lebar 540 dan tinggi sesuai halaman.

Suara, mikrofon, model, WhatsApp, Fokus/pomodoro, Agenda/kalender, Waktu/timer/alarm, Cuaca dan Sistem **tidak aktif dalam produk**. Jam visual tetap ada. Keberadaan parser, helper, tabel atau tes lama bukan bukti fitur tersebut aktif. Jangan memulai Scheduler atau memasang hook Ctrl+Space. Ctrl+Alt+Space adalah hotkey Command. Anggaran pengembangan tambahan Rp0; tidak memakai LLM/Ollama, model Handy, Nemotron atau runtime web.

## 2. Riwayat dari awal sampai revisi terakhir

| Tahap | Kebutuhan/kejadian | Hasil dan status sekarang |
| --- | --- | --- |
| Ide asli | Island liquid glass dan asisten suara lokal ID/EN, PTT Ctrl+Space, 58 pola, 17 keadaan UI dan delapan tahap | Semua ide tersimpan utuh di `kai-dynamic-island.md`; status di sana historis |
| Baseline kode | Folder awal hanya ide, kemudian pengguna menambahkan `kai.zip` dan `kai-v2.zip` | ZIP asli dipertahankan; ZIP pertama berisi sembilan berkas, tanpa island yang disebut sumber; parser 98/98 adalah bukti parser saja |
| Perencanaan | Baca seluruh 12 bagian sumber dan referensi; kebutuhan, desain, arsitektur, workflow, tes, keputusan dan inventaris skill | MD 01–10 dibuat; dokumentasi selalu memisahkan ide/usulan/inspeksi/hasil uji |
| Island pertama | Pengguna memilih navy/glow, meminta animasi popup/hide/hover halus | Foundation Qt, critically damped spring interruptible, hover 700 ms, tray, demo, reduced motion dan native checks |
| Ukuran dan RAM | Pengguna menganggap UI besar, meminta kaca gelap mirip notifikasi Windows dan RAM sekitar 20–40 MB | Compact diperkecil; riset metrik memori dan pemisahan biaya UI/model |
| Suara dihentikan | Laptop lag; pengguna sempat meminta berhenti/restart, lalu melanjutkan; akhirnya suara dimatikan | Tidak ada mikrofon/model/voice hotkey pada entry point; STT worker hanya arsip implementasi |
| Media on demand | Pengguna menyetujui media/audio hanya saat Musik dibuka demi 20–30 MiB saat itu | Worker proses ditutup ketika tab/panel ditinggalkan; popup volume/headset di luar tab tidak aktif |
| Integrasi awal | Musik/lirik, waktu/fokus, agenda/ICS, cuaca, sistem, shelf sempat diimplementasikan | Data/backend lama dipertahankan; cakupan aktif kemudian dipersempit atas permintaan |
| Material/identitas | Pengguna menolak tampilan aplikasi biru, meminta kontrol menyatu di island dan klik tanpa CMD | Kaca charcoal pearl/lavender/champagne, native compositor, launcher GUI C#, shortcut, logo robot pengguna |
| Screenshot Shelf | Pengguna ingin 4–5 screenshot langsung bisa diseret dari Kai | Event Known Folder Screenshots, referensi file, multi-select/drag; original tidak dihapus |
| Bug launcher | Explorer/taskbar tidak menemukan runtime meski tes Codex berhasil | Akar sebab pengalihan AppData MSIX; fallback path fisik dan data anak; pengguna mengonfirmasi error hilang |
| Productivity 0.3.0 | Hapus Fokus/Agenda/Waktu/Cuaca; tambah Clipboard/Command/Notes/Smart Shelf; RAM 20–40 MiB | Tujuh halaman lazy; 28 unittest saat itu; cold privat 26,60 / pascahalaman 37,10 MiB adalah hasil versi sebelumnya |
| Koreksi hover/Musik | Pengguna suka jam/logo lama; klik Musik langsung menutup | Jam/tanggal/logo dipulihkan; akar sebab panel memendek memindahkan hot area, diperbaiki anchor kursor diam |
| Revisi 3.0 | Clipboard teks/URL saja, Shelf gambar+unduhan, Notes checklist/pin, contextual actions dan screenshot tidak dobel | Deduplikasi isi piksel lintas sumber, rekonsiliasi lama saat Shelf dibuka, preview/thumbnail terbatas, popup menjaga fokus; lihat 17 |
| Referensi idle terakhir | Kapsul robot utuh dibatalkan, diganti kapsul dua mata dan dibuat sedikit lebih lebar | Ukuran final 72 × 24 DIP, render Qt statis; jam/logo hover tetap |
| Penghapusan Sistem | Pengguna tidak memerlukan monitor sistem | Halaman/nav/tray/task Sistem dihapus, lima alat + Pengaturan; helper metrik lama hanya arsip/dev |

## 3. Seluruh konsep dari sumber asli dan nasibnya

Sumber terdiri dari 12 bagian: (1) ide island+Kai; (2) hover/idle/event; (3) 17 keadaan referensi; (4) alur suara/Whisper/keputusan tanpa LLM; (5) 58 pola; (6) Python/PySide6 dan opsi C#/WPF; (7) delapan tahap; (8) lirik/sistem/cuaca-agenda/pomodoro/shelf; (9) risiko notifikasi/material/akurasi/performa/persistensi/privasi; (10) alat open source; (11) klaim/status baseline; (12) tujuan portofolio. Semuanya tetap dapat dilacak lewat 01, 04, 08 dan sumber asli.

| Referensi UI awal | Status produk terakhir |
| --- | --- |
| 1–3 pil/hover/kembali kecil | Aktif; bentuk idle terbaru berbeda dari gambar awal |
| 4 jam/tanggal/ikon | Jam, tanggal dan logo aktif saat hover |
| 5 musik Spotify/SMTC | Musik aktif; akun/playback pengguna belum tervalidasi penuh |
| 6 volume | Kontrol dalam Musik; layanan otomatis di luar Musik mati pada default |
| 7 WhatsApp | Dihapus, jangan meminta izin notifikasi |
| 8 headset/Bluetooth | Informasi endpoint melalui layanan audio saat Musik; event perangkat fisik belum diuji menyeluruh |
| 9–10 suara/hasil perintah | Suara nonaktif; hasil perintah teks dan toast tetap tersedia |
| 11 lirik | LRCLIB atas permintaan, sinkron bila timeline tersedia |
| 12 sistem | Dihapus atas permintaan terakhir pengguna; helper/tes lama tidak menjadikannya aktif |
| 13 cuaca/agenda | Dihapus dari UI/runtime aktif |
| 14 pomodoro | Dihapus dari UI/runtime aktif |
| 15 file shelf | Ditingkatkan menjadi Smart Shelf, intake gambar/unduhan dan dedupe |
| 16–17 alarm/timer | Dihapus dari UI/runtime aktif; jam tampilan bukan fitur timer |

Face ID, AirDrop, Find My iPhone, hotspot dan rekam layar pada referensi Apple hanya contoh bentuk, tidak pernah menjadi kebutuhan Windows. Angka Jakarta, suhu, nama orang, lagu dan jadwal pada ilustrasi bukan data atau preferensi pengguna.

## 4. Letak semua kelompok berkas

| Letak | Fungsi |
| --- | --- |
| `Kai.exe` | Launcher GUI kecil; membutuhkan folder sumber/aset dan runtime, bukan aplikasi standalone lengkap |
| `Kai.cmd`, `Kai Hemat.cmd`, `Kai Preview.cmd` | Kompatibilitas CLI, paksa on demand, dan demo; bukan jalur harian yang diminta |
| `Setup Kai.cmd` | Buat venv Python 3.12 di LOCALAPPDATA dan pip requirements; jalankan dari Explorer untuk pemasangan normal |
| `kai.zip`, `kai-v2.zip` | Arsip kode asli pengguna; jangan overwrite sebagai rilis baru |
| `kai/` | Source aktif, helper legacy, requirements dan tes |
| `assets/` | Logo asli, PNG 64/128 dan ICO aplikasi |
| `docs/` | Semua MD teknis/desain/status; `docs/references/` berisi referensi gambar pengguna |
| `tools/` | Build, pemeriksaan Windows, benchmark, inventory skill, restart dan generator handoff |
| `artifacts/productivity/` | Bukti versi productivity, navigasi, hotkey, revisi Shelf/Notes/context dan gambar widget uji |
| `artifacts/island/` | Native smoke, controls, worker/integrasi dan JSON benchmark; banyak gambar/angka lama bersifat historis |
| `artifacts/redesign/` | Bukti native blur/kaca dan desain sebelumnya |
| `dist/` | ZIP v1 source, v2 desktop dan `Kai-v3-productivity.zip`; rilis sumber ber-allowlist |
| `.gitignore` | Mengecualikan pycache, venv, DB, settings, token, model dan dist |
| `handoff.md` | Hasil handoff di root; sumber narasi `docs/handoff-source.md`, generator `tools/build_handoff.py` |

Logo awal pengguna berada di `C:/Users/RICO/Downloads/Minimalist Robot Mascot Icon.png`, disalin sebagai `assets/kai-original.png` dan hash pernah dibuktikan identik. `assets/kai.ico`, `kai-64.png`, `kai-128.png` adalah turunan format/resolusi, bukan identitas yang digambar ulang. Referensi terakhir disimpan sebagai `docs/references/sleeping-robot-capsule.png`; referensi yang dibatalkan ada di `robot-capsule-superseded.png`. Gambar awal tersimpan sebagai `iphone-dynamic-island.png`, `kai-ui-states.png`, `windows-acrylic-reference.png`, `island-music-new.png`, `island-shelf-new.png`, `productivity-features.png`, `adaptive-island.png`, `widget-direction.png`.

## 5. Penjelasan setiap MD tanpa melewatkan berkas

Tabel ini menjelaskan fungsi dan cara memperlakukan masing-masing dokumen. Lampiran otomatis menampilkan seluruh heading aktualnya, termasuk bagian arsip. Bila ada konflik, gunakan permintaan pengguna terbaru, panduan agen aktif dan status teratas; jangan mengambil kalimat “terbaru” dari bagian arsip sebagai keputusan baru.

| MD | Isi dan cara membacanya |
| --- | --- |
| `AGENTS.md` | Aturan kerja RICO, purpose, stack, scope, keputusan, privasi, sumber data/akses dan workflow. Dibaca setiap sesi. Bagian Project Context lama jelas arsip; blok revisi 3.0 mengungguli 0.3.0. |
| `README.md` | Ringkasan produk, fitur aktif, launcher, RAM, tes dan jalur developer. Pintu masuk pengguna/pengembang; bukan seluruh riwayat. |
| `kai-dynamic-island.md` | Sumber ide asli lengkap 12 bagian, 17 keadaan, 58 pola, 8 tahap, teknologi/risiko/portofolio. Dipertahankan; klaim “sudah/belum” dan arahan suara di sini historis. |
| `THIRD_PARTY_NOTICES.md` | Versi/lisensi dependensi yang diperiksa, status suara nonaktif, distribusi source dibanding bundel biner, ABI Windows, hak logo dan referensi. Lisensi proyek Kai sendiri belum dipilih pemilik. |
| `kai/README.md` | Entry point, flag CLI/demo/dry, runtime dan penegasan modul STT nonaktif. README root/panduan 14 adalah petunjuk produk utama. |
| `docs/README.md` | Indeks/urutan baca seluruh dokumen, definisi sumber/terverifikasi/usulan/perlu jawaban dan cara memelihara. Bagian angka lama jangan mengalahkan status 07. |
| `docs/01-kebutuhan-dan-cakupan.md` | Tujuan dan batas, 17 UI, backlog, batas referensi iPhone, keterlacakan seluruh bagian sumber dan gap baseline. Header cakupan aktif mengungguli tabel status awal. |
| `docs/02-desain-dan-interaksi.md` | Analisis referensi, tiga arah visual, state/transisi, hit test/fokus, token DIP/material/motion dan acceptance desain. Navy, avatar belum dipilih, ukuran proposal serta PTT adalah riwayat; lihat 15–17 untuk desain aktif. |
| `docs/03-arsitektur-dan-data.md` | Stack dan alternatif, struktur/alur awal, threading/event, integrasi/cache/privasi, penjadwal dan sumber resmi historis. Nama usulan media.py/scheduler.py tidak dibuat; native.py/storage.py memegang tanggung jawabnya. Runtime aktif terbaru dipetakan di handoff ini. |
| `docs/04-roadmap-dan-workflow.md` | M0–M8 dan syarat bukti, langkah milestone, ide pekerjaan pertama serta portofolio. Ini roadmap sumber, bukan perintah mengerjakan lagi WhatsApp/suara/waktu yang sudah dibatalkan. |
| `docs/05-pengujian-dan-penerimaan.md` | Matriks UI/fokus/DPI/media/audio/PTT/parser/Spotify/kalender/Shelf, metode bukti dan usulan performa. Angka 25 tes dan skenario fitur lama historis; tambahkan tes relevan sesuai scope aktif dan hasil 07/17. |
| `docs/06-keputusan-dan-pertanyaan.md` | D01–D21, usulan P01–P08, pertanyaan awal, konflik yang dijelaskan dan revisi lanjutan. Jawaban navy/suara/semua fitur pernah benar kemudian diganti; jangan menanyakan ulang keputusan yang sudah jelas. |
| `docs/07-status-dan-verifikasi.md` | Catatan faktual implementasi, hasil/batas tes dan RAM terbaru, bug launcher MSIX, ketajaman logo, redesain dan baseline. Baca dari atas; arsip tidak menjelaskan kondisi aktif. |
| `docs/08-kontrak-perintah.md` | Semua nomor 1–58 sumber, intent, delapan aturan normalisasi, angka/filler/fuzzy dan perilaku baseline. Parser masih mengenali fitur lama untuk regresi; router aktif menolak waktu/cuaca/agenda. |
| `docs/09-pemetaan-skill-ui.md` | Ponytail, Emil, Apple, gpt-taste, brainstorming, projectstep/verifikasi; adaptasi aturan web ke Qt, kandidat relevan dan urutan kerja. Tidak memasang React/GSAP hanya demi skill. |
| `docs/10-inventaris-skill-lokal.md` | Metadata 345 SKILL.md, 197 nama unik, 42 nama dengan beberapa lokasi, direktori yang diperiksa dan kesalahan baca. Ini snapshot 22 Oktober, bukan audit isi seluruh skill atau scan seluruh laptop. Semua entri tetap ada di dokumen; tidak diduplikasi satu per satu dalam narasi handoff. |
| `docs/11-rencana-island-motion.md` | Lingkup M1, tes spring/hover/event/native, CLI/demo/tray dan referensi Skiper/Unlumen/SmoothUI/Magic/Vengeance. Arah navy dan ukuran awal historis; foundation motion masih relevan. |
| `docs/12-riset-dan-anggaran-memori.md` | Arti private WS/total WS/commit, metode semua proses, paging, hasil historis, pembanding, optimasi dan model Whisper nonaktif. Gunakan blok hasil terbaru dan JSON; jangan mengutip 8 MB atau 4–5 MB yang sudah dibuang sebagai footprint Kai. |
| `docs/13-rencana-penyelesaian.md` | Rencana backend/suara/integrasi/produk/tes/paket versi lokal terdahulu, checklist hasil dan batas penerimaan personal. Delapan tab, native Acrylic belum selesai dan fitur kalender adalah riwayat versi lama. |
| `docs/14-panduan-pakai.md` | Panduan launcher, Clipboard/Command/Notes/Shelf/Musik/Sistem, login PKCE, RAM, privasi, MSIX dan troubleshooting. Blok 3.0 mengungguli 0.3.0 serta bagian Arsip; jangan menjalankan instruksi timer/cuaca dari arsip. |
| `docs/15-redesain-island.md` | Mengganti panel terpisah dengan satu island charcoal, native composition, logo asli, GUI launcher dan screenshot event/multi-drag. Pernyataan delapan halaman/semua fitur selain suara/WhatsApp adalah tahap sebelum 16/17. |
| `docs/16-kai-productivity.md` | Revisi 0.3.0: empat alat baru, penghapusan empat fitur, jam/logo dikembalikan, quota/cache/lifecycle, bug Musik dan 28 tes/RAM saat itu. Gambar dalam Clipboard di dokumen ini digantikan pemisahan pada 17. |
| `docs/17-revisi-shelf-notes-dan-context.md` | Kontrak 3.0 terbaru: teks/URL, Shelf unduhan/gambar, pixel dedupe dan rekonsiliasi, checklist/pin, preview, popup tanpa fokus, pil mata 72×24, batas dan bukti baru. Ini rujukan subsistem aktif. |
| `docs/handoff-source.md` | Narasi sumber untuk dokumen ini, dapat diedit. Generator menambah inventaris file/heading dan menguji cakupan MD. |
| `handoff.md` | Keluaran gabungan narasi+lampiran inventaris; untuk penyerahan sesi/proyek. Jangan mengedit hasil lalu lupa memperbarui sumber. |

## 6. Peta seluruh modul Python

| Modul di `kai/` | Tanggung jawab dan titik perhatian |
| --- | --- |
| `start.pyw` | Entry GUI tanpa console, menyiapkan sys.path, menjalankan main, mencatat traceback startup dan dialog error. |
| `main.py` | Argumen desktop/demo/reduced motion/on demand/text/dry; default tidak mengimpor suara. |
| `config.py` | APP_VERSION, ukuran/interval/spring, allowlist aplikasi, callback/scopes Spotify. Konstanta HOTKEY/model/hint lama bukan jalur suara aktif. |
| `island.py` | QWidget overlay, spring/presence, geometri tetap, paint kaca/kapsul/jam, queued event, hit test/fokus, panel/tray/singleton, Clipboard/Shelf/watchers/hotkey dan shutdown. Anchor navigasi mencegah Musik menutup saat tinggi berkurang. |
| `glass.py` | Windows.UI.Composition Gaussian backdrop/Direct2D melalui ctypes, clip/radius dan cleanup. Layer native click-through; fallback Qt bila gagal. Blur/refleksi, bukan simulasi refraksi optik penuh. |
| `panel.py` | Enam halaman child/lazy, styling/nav/tinggi, pemanggilan tugas, Musik/Atur, pembatalan task dan flush Notes. Sistem dan halaman fitur lama sudah dihapus. |
| `product_pages.py` | UI Command/Clipboard/Notes/Shelf, custom delegate, checklist native, preview/thumbnail terbatas, pilihan jamak dan QDrag file URL. |
| `clipboard_service.py` | dataChanged debounce 80 ms, pengecualian sumber/password manager, riwayat teks/URL, pin/search/restore via Store, dan sinyal intake gambar/file ke Shelf. Tidak mengenkode/menyimpan gambar dalam history. |
| `capture_shelf.py` | Known Folders Screenshots/Downloads, directory events + stabilisasi file; ShelfIntake/worker encode+hash RGB32, antrean terbatas, dedupe/reconcile dan purge PNG milik Kai. Tidak memindai seluruh disk. |
| `desktop_shortcuts.py` | RegisterHotKey Ctrl+Alt+Space, ingat foreground eksternal, restore focus, SendInput Ctrl+V atas aksi pengguna; fallback copy bila Windows menolak. Bukan global keyboard hook suara. |
| `quick_command.py` | Katalog Start Menu maksimal 500 .lnk dan konfigurasi apps; hasil path/URL; kalkulator AST whitelist dengan batas ukuran/eksponen, tanpa eval/shell arbitrer. |
| `storage.py` | data_dir/settings atomic replace, SQLite context manager, migrasi aditif, file metadata/fingerprint, history bounded, Notes pin/checklist. Tabel jobs/sessions/calendar dan Scheduler adalah legacy tidak dimulai default. |
| `events.py` | Event payload kind/text/data; subscriber lokal. UI menerima lewat Bridge queued signal agar worker tidak mengubah widget langsung. |
| `desktop_worker.py` | Proses SMTC/Core Audio dengan pipe/proxy, start hanya Musik, stop/join/terminate saat ditutup agar native library dilepas. |
| `native.py` | Implementasi SMTC metadata/cover/timeline/transport dan Core Audio volume/mute/endpoint; normalnya hanya di worker. |
| `widgets.py` | MusicCard native custom painting dan input transport/volume/lirik serta helper logo/gambar. |
| `tasks.py` | Integrasi sesaat lewat multiprocessing spawn, timeout/cancel/pipe cleanup; apps, command, login, lyrics. Jalur system dihapus; weather/calendar lama tersimpan tetapi tidak tersedia sebagai fitur UI aktif. |
| `integrations.py` | LRCLIB/cache/parse LRC aktif. Helper metrik psutil/GPU/disk/baterai/jaringan/proses RAM, Open-Meteo/ICS hanya legacy/dev, bukan fitur produk sekarang. |
| `actions.py` | Spotify PKCE/playback/transport, volume dan allowlist apps; HANDLERS tidak lagi mendaftarkan waktu/cuaca/kalender. Helper lama dipertahankan untuk arsip/regresi. |
| `intents.py` | Parser murni 58 pola dan variasi, normalisasi dan validasi angka/jam. Tidak membuka mikrofon atau mengeksekusi aksi sendiri. |
| `stt.py`, `speech_worker.py` | Implementasi lama PTT/Whisper/worker; nonaktif. Tidak mengunduh/memuat model atau dipakai ulang tanpa permintaan baru. |
| `test_intents.py` | 98 contoh parser awal/regresi; terpisah dari jumlah unittest suite. |
| `test_backend.py` | Regresi backend/persistensi/validasi/integrasi/lifecycle legacy memakai data/recognizer tiruan. |
| `test_island.py` | Motion, CLI tanpa suara, geometri/event/fokus/panel dan penolakan fitur lama/flush Notes. |
| `test_productivity.py` | Quota/dedupe/pin/search/persistensi Clipboard/Notes/Shelf dan kalkulator aman. |
| `test_shelf_revision.py` | Teks/URL-only, kedua urutan sumber screenshot menjadi satu original, pin/checklist persisten. |
| `requirements.txt` | Versi paket desktop yang dipin. Paket suara tidak dipasang dari daftar ini; beberapa paket helper lama masih ada, bukan berarti dimuat saat idle. |

## 7. Alur runtime dan data

`Kai.exe → runtime/Scripts/pythonw.exe → kai/start.pyw → main.py → island.run_island`. Launcher berakhir setelah memulai GUI. QLockFile mencegah instance ganda. Parent Qt menjaga jam/kursor, event Clipboard dan event folder. Panel dibuat ketika diminta. Media hidup dalam proses anak hanya ketika Musik aktif. Tugas katalog/lirik/Spotify sesaat berakhir atau dibatalkan saat panel ditutup. Encoding/hash gambar memakai satu thread pool sesaat; jangan menahan banyak QImage/cover di RAM.

Alur teks: salin → pengecualian/debounce → Store.clipboard → UI search/pin/restore → Ctrl+V hanya atas tindakan pengguna. Alur gambar: salin/event screenshot/file baru → ShelfIntake → encode/hash atau inspect path → transaksi Store.add_shelf_image → satu referensi → thumbnail/preview saat terlihat. Browser tidak dibuka otomatis saat URL disalin; mini island hanya menawarkan tindakan.

Alur Notes: ketik → dirty → debounce 350 ms → save_note; pindah/close memanggil flush; centang per item mengubah Markdown lokal dan disimpan; pin memengaruhi urutan. Shutdown menghentikan watchers/hotkey/Clipboard/intake, flush panel, cancel/reap worker, unsubscribe event, tutup compositor/tray/jendela dan lepaskan lock.

Data logis: `%LOCALAPPDATA%/Kai/`. Di laptop ini setup melalui Codex MSIX pernah dialihkan secara fisik ke `C:/Users/RICO/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/Kai/`. Runtime logis `runtime/Scripts/python.exe` / `pythonw.exe` dan data tetap di luar source OneDrive. Launcher mencoba normal lalu fallback fisik; saat fallback, LOCALAPPDATA anak disesuaikan agar DB/settings/token lama tetap sama. **Keberhasilan dari Codex tidak membuktikan Explorer**; perbaikan pernah dikonfirmasi pengguna dan path diperiksa GetFinalPathNameByHandle.

| Di direktori data Kai | Sifat |
| --- | --- |
| `kai.sqlite3` | Clipboard teks, Notes, referensi Shelf, metadata dan tabel legacy; jangan dibagikan |
| `settings.json` | Preferensi, Client ID Spotify, on demand, riwayat Clipboard, reduced motion dan preferensi lama |
| `spotify-token.json` | Rahasia OAuth; jangan cetak/kirim ke chat, ZIP atau Git |
| `clipboard-images/` | Nama historis; sekarang PNG milik **Shelf**, bukan history Clipboard; kuota disk 24 MiB |
| `lyrics/`, cache legacy | Cache lokal; jangan menyamakan cache cuaca lama dengan fitur aktif |
| `logs/startup.log`, `logs/launcher.log` | Diagnosis startup/launcher; periksa tanpa menyalin data pribadi ke rilis |
| `logs/session.json` | Versi/PID/daftar fitur/jam/hotkey tersedia; tidak memuat isi clipboard/token |
| `runtime/`, `kai.lock` | Environment Python dan singleton; runtime bukan bagian source ZIP |

Original screenshot pada laptop ini: `C:/Users/RICO/OneDrive/Pictures/Screenshots`. Downloads berasal dari Windows Known Folder (umumnya `C:/Users/RICO/Downloads`); folder khusus browser di tempat lain belum dipantau. Jangan menghapus cache paket Codex tanpa migrasi/cadangan data pribadi. Setup dari Explorer dapat memasang runtime normal tetapi tidak otomatis memigrasikan DB/token dari lokasi lama.

## 8. Privasi, quota, performa dan batas

Riwayat 80 item termasuk 20 pin, teks 64 KiB. Kode adalah teks. Pengecualian Windows/KDE/password-manager dihormati jika sumber menandai; password yang disalin sebagai teks biasa tidak selalu dikenali. Jeda/Hapus/Bersihkan tersedia. Riwayat awal OS tidak diimpor. Gambar clipboard tidak masuk history; PNG Shelf maksimal 4 MiB/item, 12 MP input dan 24 MiB total disk. File screenshot/unduhan asli tidak disalin massal ke cache dan tidak dihapus oleh Keluarkan/Bersihkan. Pin Shelf dipertahankan; daftar maksimal 100. Gambar tak direferensikan dalam direktori internal boleh dipurge, original di luar direktori itu tidak.

Dedupe membandingkan dimensi+RGB32 piksel, bukan path atau byte PNG. Kompresi/metadata PNG berbeda tetap cocok; crop/rescale/JPEG lossy tidak dijanjikan cocok. Duplikat lama diperiksa saat Shelf pertama dibuka; 100 item terbaru saja, bukan seluruh koleksi hard disk. Intake clipboard menahan maksimal satu bitmap antrean, sehingga burst clipboard-only yang lebih cepat daripada encoding dapat mengganti kandidat antrean; screenshot tersimpan tetap terjaring folder. Thumbnail maksimal 12 terlihat, pixmap cache 512 KiB, preview gambar kecil; PDF/Office dibuka di aplikasi default, tanpa engine preview berat.

Target **20–40 MiB private working set saat idle**, bukan hard cap total semua biaya. Catat cold, pascahalaman, penggunaan gambar/media aktif dan commit secara terpisah. Benchmark PSAPI EX2 menjumlahkan semua descendant GUI (dua pythonw termasuk redirector), tidak cuma launcher. Total WS dapat menghitung shared pages dua kali; DWM/GPU/sistem/aplikasi lain tidak dihitung. Paging OS dapat menurunkan resident tanpa membebaskan commit. Jangan memakai EmptyWorkingSet/trim paksa untuk mengklaim ringan. Hasil mentah terbaru berada di JSON/status 07; angka 0.3.0 adalah arsip.

Tidak memasang dependensi baru untuk revisi 3.0. Tidak mengaktifkan mikrofon, WhatsApp, model, autostart Handy/Kai, izin notifikasi atau setting sistem. Spotify/LRCLIB memerlukan jaringan; fitur lokal tetap lokal. Logo/ref gambar hak pemilik; library UI web hanya referensi. Jika nanti membundel Python/Qt/DLL sebagai installer, periksa ulang kewajiban lisensi/notice biner; metadata notice sekarang bukan audit seluruh dependensi transitif.

## 9. Tools, cara menjalankan dan menguji

Pengguna: klik `Kai.exe`/shortcut Desktop/taskbar. Hover untuk jam/logo; klik membuka kontrol; Ctrl+Alt+Space untuk Transform; Escape/× menutup kontrol; tray → Keluar Kai menghentikan aplikasi. Memindahkan hanya EXE membuat folder source/aset hilang. Komputer baru memerlukan Python 3.12 x64 + Setup; installer standalone belum ada.

Untuk pengembang dari root PowerShell, pilih runtime yang benar. Contoh ini memakai path logis yang dapat diakses dari Codex, bukan menjamin path yang sama di Explorer:

```powershell
$kaiPython = Join-Path $env:LOCALAPPDATA 'Kai/runtime/Scripts/python.exe'
$env:PYTHONUTF8 = '1'
& $kaiPython -B kai/test_intents.py
& $kaiPython -B -m unittest discover -s kai -p 'test_*.py' -v
& $kaiPython -B tools/check_shelf_v3.py
& $kaiPython -B tools/check_productivity.py
& $kaiPython -B tools/check_navigation.py
& $kaiPython -B tools/check_island_windows.py
& $kaiPython -B tools/check_controls_windows.py
& $kaiPython -B tools/check_desktop_worker.py
& $kaiPython -B tools/measure_ui_memory.py --mode core
& $kaiPython -B tools/measure_ui_memory.py --mode demand --panel-cycle
```

Jalankan tes UI/benchmark **bergantian**, karena fokus/kursor/topmost bisa saling memengaruhi. Jangan menjalankan semua sebagai satu pekerjaan paralel. Tes memakai data sementara/fake clipboard dan widget/pola sendiri; jangan merekam clipboard/audio pribadi. Regresi legacy tidak menghidupkan fitur lama. Native checker dapat menggerakkan pointer/fokus sebentar; tutup pekerjaan sensitif sebelum memakainya.

| Tool | Fungsi |
| --- | --- |
| `tools/check_shelf_v3.py` | Piksel dua arah/kompresi, repair legacy, unduhan rename/partial/lama, Notes checklist/pin, preview/thumb dan context focus/action |
| `tools/check_productivity.py` | Alur utama enam halaman, teks/URL-only, gambar hanya Shelf, screenshot/drag, autosave dan paste native target uji |
| `tools/check_navigation.py` | Reproduksi dan regresi Musik menutup saat panel memendek; gerak keluar tetap menutup |
| `tools/check_island_windows.py` | Hover/reentry/retarget, fokus, click-through, geometri/timer animasi; DPR lokal |
| `tools/check_controls_windows.py` | Klik expanded dan enam halaman embedded; memverifikasi Sistem sudah dihapus |
| `tools/check_desktop_worker.py` | Audio read-only, library native/voice tidak di parent dan worker reaped |
| `tools/check_integrations.py` | API publik/metrik dan cache sementara; tidak membuktikan akun Spotify |
| `tools/check_launcher.py` | Launcher normal/directory lain dan error path; bukan pengganti uji klik Explorer |
| `tools/check_redesign.py` | Compatibility wrapper menuju check_productivity; bukan bukti jumlah tab versi lama |
| `tools/measure_ui_memory.py` | PSAPI EX2 seluruh proses GUI, core atau demand+semua halaman, 10 sampel, tanpa trim |
| `tools/probe_acrylic.py` | Eksperimen lama Acrylic/DWM; API sukses bukan bukti visual, jangan mengulang probe berat tanpa kebutuhan |
| `tools/probe_glass_redesign.py`, `tools/probe_host_glass.py` | Pola milik tes untuk membuktikan blur/click-through compositor dan cleanup |
| `tools/build_launcher.py`, `tools/KaiLauncher.cs` | Kompilasi EXE GUI .NET Framework dengan ikon, runtime fallback, logging dan startup; hasil melalui temporary lalu replace |
| `tools/create_shortcut.py` | IShellLinkW Unicode untuk Desktop; path Jepang harus tetap benar |
| `tools/restart_kai.py` | WM_QUIT hanya proses/jendela proyek yang cocok, tunggu cleanup, buka EXE lalu cek session. Jangan mematikan semua python pengguna |
| `tools/build_release.py` | ZIP allowlist + manifest SHA-256, verifikasi arsip, tanpa runtime/model/settings/token/DB |
| `tools/inventory_skills.py` | Snapshot metadata direktori skill konvensional; tidak scan seluruh disk atau mengaktifkan seluruh katalog |
| `tools/build_handoff.py` | Generate handoff dari narasi dan inventaris MD/file; `--check` memeriksa keluaran tetap sinkron |

## 10. Pengujian yang sudah ada dan yang belum

Suite baru berisi **31 unittest lulus**, parser awal 98 contoh diuji terpisah. Native revisi 3.0 membuktikan dua urutan screenshot menghasilkan satu item, PNG beda kompresi cocok, original dipertahankan, duplikat lama digabung, download final ditambahkan sementara/lama diabaikan, checklist clickable+pin+autosave, preview/thumb asli, serta mini island tidak mengambil foreground/fokus mengetik. Hasil status 07 dan JSON adalah acuan angka/waktu aktual; handoff ini tidak mengklaim tes akun atau soak yang tidak dilakukan.

Keberhasilan native paste di receiver milik tes tidak menjamin semua aplikasi target/elevasi menerima SendInput. Hotkey dapat tidak tersedia bila Kai/aplikasi lain sudah mendaftarkannya; gunakan tray. Sensor GPU/suhu bergantung perangkat/izin; unavailable tidak boleh menjadi nol palsu. Blur harus lolos bukti visual, bukan hanya HRESULT sukses.

Belum tervalidasi menyeluruh: login/playback Spotify dengan akun pengguna, token expired/403/429/device nyata, volume/headset fisik, setiap tujuan drag/drop/paste, monitor/DPI selain pengujian lokal 150%, exclusive fullscreen, sleep/resume dan pemakaian satu hari. Unduhan browser dengan folder khusus/temporary format lain, screenshot di folder di luar Known Folder, clipboard-only burst dan gambar lebih besar perlu uji sesuai batas. Tidak ada installer standalone/CI/distribusi publik atau lisensi proyek final.

## 11. Menangani masalah tanpa mengulang kesalahan lama

- Runtime tidak ditemukan: periksa root EXE beserta `kai/start.pyw`, path normal/fisik MSIX dan `logs/launcher.log`. Error runtime hilang berbeda dari source start.pyw hilang. Jangan memasang ulang atau menghapus cache/data secara membabi buta.
- Klik Musik menutup: periksa resize_deck/hot area/anchor, jalankan check_navigation. Jangan menonaktifkan auto-hide seluruh aplikasi untuk menutupi bug.
- Screenshot dobel: pastikan versi 3.0, intake gambar/folder sama, fingerprint terisi, buka Shelf untuk rekonsiliasi. Jangan menghapus screenshot asli; JPEG lossy/crop memang identitas berbeda.
- Gambar terlihat sebagai ikon: pilih item untuk preview, periksa file masih ada, decoding/format/limit dan thumbnail item terlihat. Jangan memuat gambar penuh seluruh history ke RAM.
- Unduhan tidak muncul: pastikan di Known Folder Downloads, dibuat setelah Kai hidup, ekstensi final, ukuran+mtime stabil dan penulis menutup file. File lama/folder khusus tidak diimpor otomatis.
- Notes belum tersimpan: periksa dirty/350 ms/flush close, bukan hanya timer.isActive di callback singleShot. Checklist Markdown dan pin disimpan di DB yang sama, bukan state widget semata.
- RAM naik: ukur proses keturunan/commit, pastikan media on demand dan worker selesai, cek cache/retensi/gambar aktif. Tutup melalui tray jika laptop berat. Jangan menyamakan seluruh sistem lag dengan penggunaan Kai.
- URL tidak terbuka otomatis: memang hanya penawaran; klik mini island. http/https valid saja. Jangan mengeksekusi clipboard sebagai shell.

## 12. Workflow penerus, rilis dan pemeliharaan handoff

Mulai dengan handoff → AGENTS → docs/README → blok terbaru 07 → 17 → subsistem terkait. Ikuti ponytail full untuk perubahan minimum, Emil/gpt-taste sebagai prinsip desain Qt, systematic-debugging saat bug, dan bukti sebelum klaim. Jangan memaksa AIDA/hero/font web/React/GSAP ke desktop. Jangan mengaktifkan semua skill lokal; inventaris bukan daftar tugas. Bahasa pengguna dan dokumentasi utama Indonesia.

Untuk perubahan: tulis acceptance, reproduksi bug, tes minimum bermakna, implementasikan, uji ulang sesuai dampak, ukur memori jika jalur lifetime/cache berubah, catat keputusan 06/status 07/kontrak 17/panduan 14. Permintaan pengguna terbaru lebih tinggi dari ide/arsip. Tanyakan hanya keputusan produk/akses yang belum jelas, bukan izin implementasi rutin yang sudah diberikan.

Untuk rilis: build_launcher hanya bila sumber launcher/aset ikonnya berubah; build_release setelah source/docs/bukti final. ZIP berada di `dist/Kai-v3-productivity.zip`, menyertakan source/aset/MD/EXE/notice/manifest dan bukti JSON yang di-allowlist, bukan environment/model/DB/token/cache pribadi. ZIP lama bukan installer. Source ZIP bukan bukti instalasi bersih komputer lain.

Sumber handoff adalah `docs/handoff-source.md`. Perbarui narasi lalu jalankan:

```powershell
& $kaiPython -B tools/build_handoff.py
& $kaiPython -B tools/build_handoff.py --check
& $kaiPython -B tools/build_release.py
```

Generator membaca hanya source/doc proyek, membuat daftar semua MD (dengan heading), memeriksa masing-masing disebut dalam penjelasan, dan menambahkan inventaris file. Tidak membaca DB/settings/token atau mengoperasikan aplikasi. Jika MD baru ditambah, tambahkan penjelasannya ke tabel agar tidak ada dokumen yang terlewat. Build ini mengubah handoff saja; tidak menjalankan ulang benchmark atau mengklaim hasil lama sebagai uji baru.
