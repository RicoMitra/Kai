# Status dan verifikasi aktual

## Lyrics lookup correction — 24 October 2026

LRCLIB's expected HTTP 404 for a missing catalog match previously propagated as a raw task error. Kai now tries one bounded search after that response, accepts only normalized title/artist matches and a duration within two seconds when known, and renders distinct missing, instrumental and temporary-failure states. Plain lyrics are no longer labeled as synchronized. Positive results retain the existing 50-track disk bound; missing entries expire after six hours and transient errors back off for one minute, with retry available on click. Corrupt cache JSON is refetched. No new library, resident worker or polling timer is added. Exact live/remaster mismatches are deliberately not guessed.

Verification: **44 unit tests passed**, including five isolated LRCLIB/cache matching tests and a widget test proving that unavailable/instrumental/retry messages replace old lyric layouts and hide stale scrolling. Appearance checks also passed. Live read-only API probes returned a known track successfully and a synthetic absent track as get=404/search=200 with zero records; a separate transient attempt produced the retry state. Only status/counts were inspected; copyrighted lyric text was not copied into the repository. No account playback was changed. These checks do not establish catalog coverage for every new song. Primary API contract: https://lrclib.net/docs.

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


## Revisi terakhir — Notes sederhana, Transform, Musik

**Cakupan aktif:** enam halaman Transform/Clipboard/Notes/Shelf/Media/Atur. Command diganti Fast Transform; tidak ada index aplikasi saat panel dibuka. Sistem tetap dihapus. **Notes paling akhir hanya daftar, + Catatan/input sebaris/Enter, centang dan Hapus**, tanpa cari/editor/detail/subheading; Pin lewat klik kanan, autosave 350 ms/flush tetap. Ini mengungguli desain detail/checklist kuning di versi percobaan sebelumnya. Shelf tidak diubah oleh referensi yang dikoreksi pengguna menjadi Notes.

Fast Transform: satu worker, maksimal 2 input/hasil; PNG/JPG/PDF/DOCX/Notes/MD/TXT ke PDF/MD/JPG, batas/layout/OCR di 18. QtPdf/WinRT OCR tidak masuk parent. Hasil di disk milik Kai dibersihkan setelah save/proses baru/pindah/close; cancel/reap mendahului cleanup. Salinan tersimpan dan original tetap. 15 pasangan konversi file contoh (termasuk OCR Inggris nyata dan DOCX tabel/gambar) lulus signature/teks; worker reaped, UI save/cleanup/cancel dan parent tanpa engine lulus. Tidak menjalankan Word/LibreOffice/cloud/model baru.

Musik: klik progress seek sesuai durasi/start timeline, volume −/+ 5% dengan rail/mute. Widget/tick/sinyal diuji; playback akun/perangkat fisik belum dimutasi dalam tes. Pemberitahuan jika pemutar menolak seek, native/audio tetap on demand.

**35 unittest lulus** termasuk Notes tambah/centang dua arah/hapus/pin/flush tanpa search/editor, limit konversi dan seek/volume. check_productivity lulus enam halaman Transform baru, clipboard/Shelf/drag/autosave/paste. check_shelf_v3 lulus dedupe/unduhan/preview serta Notes sederhana. Bukti baru transform-verification.json, notes-list-reference.png dan fast-transform.png di artifacts/productivity. Bukan jaminan dokumen kompleks atau semua pemutar/tujuan/monitor telah teruji.

**RAM terbaru, tanpa trim:** cold commit **31,21 MiB**, private WS median 3,76 (1,61–16,55), total WS median 17,35 (3,27–53,20). Sesudah enam halaman dengan Notes sederhana: commit **38,80 MiB**, private WS median 1,71 (1,39–1,73), total WS median 3,28 (2,95–3,30). Resident sangat rendah/fluktuatif mencerminkan paging/tekanan Windows; **bukan klaim Kai hanya memakai 1–4 MiB**. Angka commit pascapanel turun dari 59–60 MiB tahap sebelumnya pada run ini, tetapi target privat resident stabil 20–40/hard cap belum terbukti. Dua proses dihitung, worker reaped; tidak termasuk DWM/sistem. Benchmark ini mengunjungi halaman tanpa melakukan konversi berat; RAM saat konversi akan naik sementara. Jangan mengganti angka lama dengan klaim ringan tanpa konteks metrik ini.

Kontrak aktif di 18, panduan 14, handoff dibuat ulang dari sumber. Bagian di bawah adalah riwayat sebelum revisi terakhir.

## Aktif 3.0.0 — 23 Oktober 2026

Koreksi terakhir: Sistem dihapus dari halaman, nav, tray dan task runtime. Kini lima alat + Pengaturan (enam halaman); 31 unittest serta native check enam halaman lulus. Sebelum Sistem dihapus private WS pascasiklus 54,12 MiB; sesudahnya 53,50 MiB. Penurunan 0,62 MiB pada dua run, bukan bukti selisih eksak universal. Halaman metrik lama dan helpernya tidak aktif dalam produk.

Clipboard hanya menyimpan teks/URL; kode tetap teks. Gambar/file tidak masuk history. ShelfIntake menerima gambar, screenshot, file clipboard dan unduhan baru dari Known Folder. Event direktori, ekstensi sementara diabaikan, ukuran+mtime stabil dan pemeriksaan writer sebelum intake download. Fingerprint dimensi+RGB32 menyatukan screenshot clipboard/folder, memilih original dan menjaga pin. Rekonsiliasi duplikat lama saat Shelf pertama dibuka; hanya PNG tidak direferensikan dalam folder internal yang dipurge. File pengguna tidak dihapus.

Smarter Notes menambah checklist per item yang dapat diklik, pin di atas, autosave/flush tetap. Shelf memakai thumbnail asli maksimal 12 item terlihat, preview gambar embedded dan metadata/open untuk dokumen. Contextual action menawarkan Shelf/browser melalui mini island 290 × 56 tanpa mengambil fokus; halaman aktif tidak ditimpa. Referensi robot kapsul utuh dibatalkan oleh pengguna: pil final dua mata glossy **72 × 24 DIP**; hover jam/tanggal/logo tetap 320 × 68.

**Bukti:** 31 unittest lulus. tools/check_shelf_v3.py lulus dua urutan sumber screenshot, beda kompresi PNG, repair duplikat lama, original tetap ada, partial/lama diabaikan dan rename unduhan final masuk, checklist/pin/autosave, thumbnail/preview nyata, foreground/fokus mengetik tidak berubah dan click action. tools/check_productivity.py lulus dengan text-only history, gambar hanya Shelf, lima screenshot/drag, flush dan native paste sekali. tools/check_navigation.py tetap lulus Musik tidak menutup ketika panel menyusut dan gerak menjauh tetap menutup. Data uji sementara; tidak mengunduh file atau mengubah akun/perangkat/clipboard pribadi.

**RAM GUI terbaru:** cold median private WS **26,66 MiB**, total WS 65,89, private commit 30,93; setelah siklus enam halaman private WS **53,50 MiB**, total 128,59, commit 60,30; seluruh sampel pada run ini stabil. Dua proses GUI dihitung, worker reaped. Cold memenuhi target 20–40, **pascasiklus belum memenuhi**. Commit pascasiklus mendekati 60,17 versi sebelumnya, tetapi resident tidak lagi sama; nilai 37,10 lama tidak dijadikan klaim versi baru. Pemeriksaan lifetime menunjukkan panel ditutup/deleted, worker reaped, thread pool berakhir; tidak memakai trim paksa. Diagnostik sementara panel menunjukkan kenaikan ketika membuka Command, tetapi akar retensi native belum terbukti, sehingga tidak dilakukan rewrite spekulatif atau menjanjikan cap 40 MiB.

Data hasil: artifacts/productivity/shelf-v3-verification.json dan v3-*.png; memory-core.json dan memory-demand-after-panel.json. Batas: clipboard-only burst hanya satu bitmap antrean, PNG 4 MiB/12 MP/24 MiB disk; fingerprint persis bukan near-duplicate JPEG/crop; Known Folder saja; renderer dokumen eksternal. Akun Spotify/perangkat fisik/DPI lain/paste/drop semua aplikasi/soak harian tetap belum tervalidasi. Lihat docs/17 dan handoff.md. Bagian 0.3.0 dan angka di bawah adalah arsip.

## Aktif 0.3.0 — productivity, jam/logo dan navigasi Musik

Arahan terbaru menghapus Fokus/pomodoro, Agenda/kalender, Waktu/timer/alarm dan Cuaca. Halaman/menu/router aktif serta Scheduler sudah dilepas; data lama tidak dihapus. Tambahan aktif: Smart Clipboard, Quick Command, Quick Notes, Smart Shelf. Musik dan Sistem tetap ada; tujuh halaman termasuk Pengaturan. Koreksi pengguna mengembalikan hover ke jam, tanggal dan logo robot, tanpa tiga tombol Clip/Notes/Shelf.

Clipboard event-driven lokal mendukung teks/link/kode/gambar, pin/search/restore/paste/jeda/hapus. Batas 80 item/20 pin/64 KiB teks; gambar 12 MP, PNG 4 MiB/item dan 24 MiB total. Encoding gambar dilakukan di pool sesaat; tidak menyimpan semua gambar dalam RAM. Format pengecualian Windows/password manager dihormati jika ada; teks password biasa tidak dapat selalu dikenali. Tidak mengimpor clipboard awal atau riwayat OS lama.

Command memakai Ctrl+Alt+Space, indeks Start Menu maksimal 500 shortcut saat dipakai, path/URL, kalkulator AST terbatas serta perintah musik/volume. Tidak menjalankan shell arbitrer. Notes CRUD/search/status selesai, autosave 350 ms dan flush close. Shelf menerima screenshot baru, drop/file-folder clipboard/gambar, filter/search/pin dan drag beberapa URL. File asli tidak dihapus.

Sistem menambah laju jaringan dan lima proses RAM teratas melalui snapshot sesaat. Media tetap worker on demand; Sistem dibatalkan saat ditinggalkan. Cache pixmap dibatasi 512 KiB. Callback tugas dibatalkan/diputus saat panel ditutup, sehingga tidak memakai QObject yang sudah dihancurkan. Objek Python tidak terpakai dikoleksi setelah transisi; tanpa EmptyWorkingSet atau trim paksa.

Bug klik Musik ditunjukkan tes: halaman memendek sehingga posisi tombol keluar dari hot area dan auto-hide menutup panel. Perbaikan menahan state ketika kursor diam di posisi navigasi; gerakan keluar tetap menutup. tools/check_navigation.py gagal sebelum perbaikan dan lulus sesudahnya.

**RAM jalur GUI pythonw (dua proses, data sementara, 10 sampel):** cold private WS 26,60 MiB / total WS 65,99 / private commit 30,98. Sesudah seluruh tujuh halaman dibuka dan ditutup: private WS median 37,10 (36,56–37,71), total WS median 87,25, commit 60,17. Worker hadir lalu reaped terverifikasi. Pengukuran console sebelumnya memasukkan console host dan bukan jalur peluncuran pengguna. Target privat idle 20–40 tercapai pada sampel ini, bukan hard cap saat fitur aktif; DWM/sistem tidak dihitung dan total WS dapat menghitung halaman bersama dua kali.

**Verifikasi:** 28 unittest lulus. Native checks lulus untuk hover/retarget/fokus/click-through, tujuh halaman embedded, lima screenshot event/payload drag lima file, clipboard teks/link/kode/gambar/pause/pengecualian, autosave/flush, native Ctrl+V sekali ke target uji, serta worker reaped. Hotkey register/dispatch dibuktikan pada uji terisolasi; sesi GUI aktual 0.3.0 mencatat hotkey_available=true. Snapshot memakai data ilustrasi pada widget/pola sendiri; bukan media/clipboard pribadi pengguna.

Bukti: artifacts/productivity/*verification.json dan *.png; artifacts/island/memory-core.json, memory-demand-after-panel.json, panel-cycle-verification.json. tools/restart_kai.py menutup hanya jendela proyek melalui WM_QUIT, menunggu cleanup lalu membuka launcher dan memeriksa sesi baru. Data/settings/token tidak diubah atau dikemas.

Batas: akun/playback Spotify, perangkat fisik, setiap aplikasi tujuan paste/drop, monitor/DPI lain dan soak harian belum diuji. Kalkulator dibatasi; indeks bukan pencarian seluruh disk. Paket source + launcher bukan installer mandiri. Bagian versi sebelumnya di bawah merupakan arsip.

## Perbaikan launcher Explorer/taskbar — 22 Oktober 2026

Pengguna melaporkan runtime tidak ditemukan ketika membuka Kai.exe dari taskbar dan folder proyek. Pemeriksaan dari Codex sebelumnya berhasil, tetapi itu bukan bukti peluncuran Explorer. Log dari peluncuran pengguna menunjukkan GetFileAttributes error Windows 3 / DirectoryNotFoundException. GetFinalPathNameByHandle membuktikan runtime logis LOCALAPPDATA/Kai sebenarnya berada di LOCALAPPDATA/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/Kai karena pengalihan AppData MSIX.

Launcher kini mencoba runtime normal dahulu, kemudian lokasi fisik runtime yang sudah ada dalam LocalCache paket Codex. Untuk fallback ini, LOCALAPPDATA proses anak diarahkan ke induk fisiknya agar SQLite/settings/token tetap memakai data yang sama. Tidak menyalin atau menghapus data/kredensial, tidak memasang ulang dependensi, tidak mengubah autostart atau izin. Fallback bergantung pada runtime yang masih ada di cache paket; Setup yang dijalankan pengguna di luar Codex tetap memasang runtime konvensional. Uninstall Codex dapat menghapus cache tersebut.

**Konfirmasi pengguna:** “Sudah terbuka, error hilang”. Proses baru teramati memakai pythonw dari path fisik LocalCache. Tes launcher juga lulus dari working directory berbeda; salinan EXE tanpa start.pyw menghasilkan kode 3, bukan salah melaporkan runtime hilang. Percobaan otomatis meniru konteks Explorer tidak berhasil memisahkan virtualisasi, sehingga tidak dipakai sebagai bukti. Runtime hilang sungguhan berkode 2 dan error startup mencatat detail di logs/launcher.log.

Logo asli Downloads identik SHA-256 dengan assets/kai-original.png. Header kini dirender pada jumlah piksel sesuai DPR (36 piksel untuk 24 DIP pada 150%), penanda island memakai turunan 128 piksel, dan resampling gambar memakai SmoothPixmapTransform. Efek blur kaca latar tetap dipertahankan; perbaikan ini menajamkan identitas/logo.

## Versi aktif: island kaca + screenshot Shelf — 22 Oktober 2026

Arahan terbaru menggantikan navy/glow lama. Kai memakai kaca charcoal reflektif, logo robot pengguna, launcher GUI **Kai.exe** dan shortcut Desktop. Launcher telah dijalankan: dua proses pythonw runtime/redirector terdeteksi, proses Kai.exe berakhir setelah memulai aplikasi; tanpa shell console. Shortcut disimpan/dibaca ulang memakai IShellLinkW Unicode agar folder Jepang tetap benar. Runtime tetap Python/PySide6; tidak ada installer mandiri atau perubahan autostart.

Kontrol delapan halaman kini child island, tanpa dialog aplikasi terpisah. Media 540 × 280 DIP dan Shelf 540 × 270; formulir menyesuaikan tinggi hingga 356. Pil idle tetap 56 × 20, hover 320 × 68. Musik/lirik berdampingan, file berupa thumbnail, ikon dan pilihan jamak. WhatsApp UI/listener dihapus; suara tidak diaktifkan atau dimuat. Semua fitur lainnya dipertahankan.

Screenshot Shelf otomatis memakai Windows Known Folder Screenshots (OneDrive/Pictures/Screenshots pada laptop ini). Event folder, debounce dan ukuran stabil menghindari polling idle dan file setengah ditulis. Lima screenshot baru masuk melalui event native pada folder sementara; file lama diabaikan. Mengeluarkan satu referensi mempertahankan original dan tidak menambahkannya kembali. Payload drag pilihan empat item setelah penghapusan lulus. Drag ke setiap aplikasi pihak ketiga belum diuji; aplikasi tujuan harus menerima file. Clipboard-only belum dicakup.

Blur nyata memakai Windows.UI.Composition/Gaussian backdrop, bukan screenshot latar atau webview. Probe pola milik tes: tepi warna tajam 101 menjadi 3, kontras tetap 81. Layer native memakai layered transparent sehingga tidak memblokir hit testing. Tiga siklus tutup/buka compositor lulus. Jika API gagal, transparansi Qt menjadi fallback. Ini material blur/refleksi, belum simulasi refraksi optik fisik penuh.

**Verifikasi:** 25 unittest dan 98 parser lulus; native hover, retarget, jeda 700 ms, fokus tidak direbut, click-through, klik expanded, delapan halaman embedded, screenshot event dan worker reaped lulus pada DPR 1,5. Interval timer p50 11,96 ms/p95 13,20 ms bukan ukuran frame display. Probe memakai widget/data sementara; contoh musik pada capture bukan playback Spotify pengguna. Akun Spotify, volume/perangkat fisik, sleep/resume, monitor/DPI lain dan soak harian tetap belum diuji.

**RAM desain baru:** cold idle median private WS 26,66 MiB / total WS 69,93 / private commit 31,64 (10 sampel, seluruh descendant proses). Setelah Media dibuka lalu ditutup: worker terverifikasi hadir lalu berakhir; private commit 59,22 MiB. Private WS pascasiklus 2,59–22,50 sangat dipengaruhi paging OS; tidak diklaim sebagai footprint beberapa MB. Target 20–30 bukan batas keras dan DWM/sistem tidak dihitung. Tidak memakai EmptyWorkingSet atau trim paksa.

Bukti aktif: `artifacts/redesign/redesign-verification.json`, `glass-verification.json`, `host-glass.png`; `artifacts/island/verification.json`, `controls-verification.json`, `desktop-worker-verification.json`, `panel-cycle-verification.json`, `memory-core.json`, `memory-demand-after-panel.json`. Paket `dist/Kai-v2-desktop.zip` menyertakan launcher/aset/source dengan allowlist, tanpa runtime, token, settings atau DB.

Bagian berikut adalah catatan versi sebelumnya; klaim material/navy/dialog/WhatsApp dan angka memori lamanya sudah digantikan di atas.

## Arsip sebelum redesain kaca — 22 Oktober 2026

**Keputusan terbaru:** pengguna menonaktifkan suara dan menyetujui media/audio hanya saat tab Media dibuka demi RAM 20–30 MiB. `Kai.cmd` kini memakai default tersebut. Tidak ada hook Ctrl+Space, stream mikrofon atau model di jalur aktif. Paket suara dihapus dari requirements aktif; kode lama tetap nonaktif sebagai backlog.

Runtime Python berada di LOCALAPPDATA/Kai/runtime, di luar folder source OneDrive. Dependensi versi aktif dipin; runtime yang diuji mewarisi paket global melalui system-site-packages dan ditambah paket yang diperlukan. Setup baru membuat env mandiri; instalasi bersih komputer lain belum diuji. Model tidak diunduh/dimuat dalam pengerjaan ini. Kedua ZIP pengguna dan ide asli dipertahankan.

## Implementasi dan bukti

| Area | Implementasi aktif | Yang sudah dibuktikan / batas |
| --- | --- | --- |
| Island | 56 × 20 / 320 × 68 DIP, navy gelap transparan, hover 700 ms, spring interruptible, popup/tray/reduced motion | Native Windows DPR 1,5: hover/reentry/retarget, timer animasi berhenti, fokus tidak direbut, click-through dan klik expanded lulus |
| Panel | Delapan tab, kolom perintah teks, lazy creation | Konstruksi, navigasi, capture dan klik membuka panel lulus; tidak memakai data contoh sebagai data pengguna |
| Media/audio | SMTC metadata/cover/timeline/transport; Core Audio volume/mute/perangkat di proses on demand | Read-only service mendapat endpoint audio; tidak ada media aktif saat tes. Library native tidak terimpor di parent; worker reaped setelah stop. Belum memutar/mengubah volume/perangkat fisik pengguna |
| RAM | Tidak ada STT; worker media berakhir saat tab/panel ditinggalkan; task cuaca/lirik/ICS/sistem/Spotify sesaat | Default median private working set 22,64 MiB; total WS 63,24; private commit 26,80. Seluruh proses launcher dihitung; bukan hard cap. Lihat 12 |
| Waktu | SQLite timer/alarm harian, pause/resume/cancel, scheduler terlewat, popup selesai | Persist/reopen, due sekali, pause/resume/cancel dan durasi invalid lulus di DB sementara. Sleep/resume/alarm perangkat nyata belum diuji |
| Fokus | Fokus kustom, statistik, siklus 5/15 opt-in | Dasar persistensi/statistik diimplementasikan; siklus satu jam nyata belum diuji |
| Jadwal/shelf | Kalender lokal + ICS 90 hari, referensi file | UID dedupe, pindah waktu/reimport, recurrence harian, reject SECONDLY; hapus referensi menjaga file asli lulus |
| Cuaca/lirik/sistem | Open-Meteo cache/stale, LRCLIB sinkron, psutil/nvidia-smi on demand | API cuaca kota uji + LRCLIB 40 baris sinkron + skema metrik sistem merespons. Cache di direktori sementara; bukan kota/lagu pilihan pengguna |
| Spotify | PKCE loopback, token LOCALAPPDATA, pencarian/playback + fallback transport | Import/runtime dipasang; dashboard, login akun dan playback pengguna belum diuji. Random liked tracks terbatas 50 |
| Notifikasi | Kode listener tetap ada; tidak aktif pada default hemat | Portable belum memiliki package identity/capability. Fitur belum tersedia, tidak meminta izin seolah siap |
| Material/distribusi | Transparansi Qt; launcher normal/hemat/preview + Setup; ZIP source allowlist dan manifest | Acrylic/SCA/DWM probe menerima API tetapi tampilan solid, jadi blur native belum diaktifkan. Paket bukan installer/EXE dan tidak menyertakan runtime/token/model/database |

25 unittest backend/UI lulus dan 98/98 contoh parser lulus. Suite mencakup tes lifecycle kode suara nonaktif; hasil itu tidak berarti mode suara diaktifkan. Bug angka negatif/desimal/jam 25 pada baseline sudah diperbaiki. Timer daemon lama diganti penyimpanan persisten.

## Berkas bukti dan pemeriksaan

- `artifacts/island/verification.json`: native hover/fokus/click-through; interval timer bukan frame display.
- `controls-verification.json`: hit testing expanded, klik panel dan delapan tab.
- `desktop-worker-verification.json`: endpoint audio terbaca, native/voice imports tidak di parent, proses dihentikan.
- `integrations-verification.json`: cuaca/lirik/sistem dengan cache sementara dan tanpa akun.
- `memory-core.json`: default terbaru. `memory-demand-after-panel.json` + `panel-cycle-verification.json`: panel benar dibuka/ditutup dan worker hilang.
- `current-expanded.png`, `current-volume.png`, `current-panel.png`: capture widget sendiri, bukan layar pribadi pengguna.

Perintah repeatable ada di README. Tes dijalankan bergantian. Tidak memakai EmptyWorkingSet/memaksa trim, tidak mengubah autostart/izin Windows dan tidak merekam audio pengguna. RAM tersedia sempat 180 MB sehingga pengujian model nyata tidak dilakukan, lalu pengguna menonaktifkan suara sepenuhnya.

## Pekerjaan yang masih terbuka

Acrylic native yang terbukti visual, identitas paket/notifikasi, uji akun Spotify dan pemutar aktif, volume/headset fisik, sleep/resume, monitor/DPI/fullscreen lain, aksesibilitas lanjutan serta soak harian. Wake word/TTS dan cloud calendar tetap backlog; suara dinonaktifkan atas permintaan pengguna. Default jam tidak menampilkan semua detail cuaca/baterai pada referensi; data terkait tersedia di panel. Jangan menyebut seluruh 17 state/integrasi selesai hanya karena fondasi UI dan parser sudah lulus.

## Baseline arsip awal (sebelum implementasi)

Baseline diperiksa 22 Oktober 2026. Ini hasil inspeksi dan tes terbatas; aplikasi penuh belum dijalankan.

## Berkas yang tersedia

Pengguna menambahkan `kai.zip` setelah pemeriksaan awal folder. Arsip diekstrak ke `kai/` dengan pemeriksaan path dan tanpa overwrite. Isinya sembilan berkas: `README.md`, `actions.py`, `config.py`, `events.py`, `intents.py`, `main.py`, `requirements.txt`, `stt.py`, `test_intents.py`. Semua sudah dibaca. Dokumen ide asli dan ZIP tetap disimpan.

Tidak ada `island.py`, dependensi PySide6, SMTC, opsi `--island`, atau opsi `--demo` dalam baseline ini. Pernyataan sumber bahwa island pernah ditulis mungkin merujuk berkas terpisah yang belum tersedia. Rencana saat ini memperlakukan UI sebagai belum ada dalam kode yang diterima.

## Perangkat yang dibaca lokal

| Item | Hasil |
| --- | --- |
| Sistem | Windows 11 Home Single Language, versi 10.0.26200, build 26200 |
| Laptop | Acer Predator PHN16-71 |
| CPU | Intel Core i9-13900HX, 24 core, 32 logical processor |
| RAM | Sekitar 15,7 GiB terbaca OS (kelas 16 GB) |
| GPU diskret | NVIDIA GeForce RTX 4060 Laptop GPU |
| VRAM | 8188 MiB dilaporkan `nvidia-smi` |
| GPU lain | Intel UHD Graphics |
| Python | 3.12.4; Python, py launcher, git dan nvidia-smi ditemukan |

Metode: CIM Win32_OperatingSystem/ComputerSystem/Processor/VideoController; `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader`; `python --version`. Tidak membaca nomor seri atau kredensial. Ketersediaan CUDA/cuDNN untuk faster-whisper belum diuji; tidak ada model diunduh atau dependensi dipasang dalam sesi dokumentasi ini.

## Verifikasi yang dijalankan

| Pemeriksaan | Hasil | Batas |
| --- | --- | --- |
| `python -B test_intents.py` di `kai/` | 98/98 lulus; exit 0 | Parser dan slot pada contoh tersedia saja |
| Parser `timer -5 menit` | Menghasilkan timer 300 detik | Tanda minus hilang pada normalisasi; perlu validasi sebelum aksi |
| Parser `alarm jam 25` | Menghasilkan alarm jam 01:00 | Jalur modulo 24 menerima jam invalid |
| Parser `timer 1.5 menit` | Menghasilkan timer 300 detik | Titik dinormalisasi sebagai pemisah jam; dukungan desimal tidak konsisten |
| Inventaris skill lokal | 345 berkas, 197 nama unik, 0 kesalahan baca | Metadata; bukan pembacaan penuh setiap skill atau scan seluruh disk |

Tiga kasus parser terakhir hanya diparse dengan `intents.py`; tidak membuat alarm/timer nyata. Masalah ini belum diperbaiki dalam tugas dokumentasi.

## Temuan inspeksi kode untuk pekerjaan berikutnya

| Area | Temuan | Tindak lanjut minimum |
| --- | --- | --- |
| UI | Tidak ada island/Qt di ZIP | M1 demo dan jembatan event Qt |
| PTT | Callback berhenti menambah buffer setelah 20 detik, tetapi stream tetap terbuka sampai hotkey dilepas | Tutup rekaman otomatis pada batas dan tampilkan state akhir |
| PTT error | `_recording` diset sebelum stream berhasil dibuka; error pembukaan tidak dipulihkan | Cleanup lewat finally/jalur error; pilih mikrofon yang valid |
| Konkurensi | Satu daemon thread dibuat tiap pelepasan PTT tanpa busy guard | Serialisasi transkripsi, cegah hasil tumpang tindih |
| CUDA | Deteksi device ada; konstruktor model gagal tidak dibungkus fallback CPU | Uji load nyata dan fallback eksplisit |
| Bahasa | ID/MS/EN dipilih jika `detect_language()` berhasil; exception membiarkan deteksi Whisper biasa | Uji signature versi paket dan akurasi bahasa campuran |
| Event | Listener sinkron di thread pengirim; hasil berupa teks saja | Queued signal Qt dan payload minimum untuk kartu |
| Error aksi | String “Gagal” dikirim sebagai event `result` biasa | Bedakan sukses/gagal secara terstruktur |
| Timer/alarm | `threading.Timer` daemon; tidak persisten; item selesai tidak dikeluarkan dari daftar | Penjadwal + state tersimpan; hitung hanya yang aktif |
| Cancel | Semua timer/alarm pada jenis terkait dibatalkan langsung | Jelaskan perilaku; pilih target per item bila dibutuhkan |
| Pomodoro | Fokus satu kali; belum ada jeda, siklus, pause atau statistik | M6a setelah timer stabil |
| Kalender/cuaca | `_not_yet()` mengembalikan teks placeholder | Implementasi belum ada walau intent lulus tes |
| Spotify fallback | Pause/resume dapat memakai tombol toggle pada error | Jangan menjamin keadaan akhir tanpa pembacaan playback |
| Random lagu | Hanya mengambil maksimal 50 saved tracks | Jelaskan batas atau pagination saat fitur dilengkapi |
| Spotify runtime | Pencarian/context artist, scopes, device dan endpoint belum diuji dengan akun pengguna | Uji Client ID sebenarnya dan API yang masih tersedia |
| Aplikasi | Allowlist ada, fuzzy cutoff 80; target dibuka melalui cmd start | Uji target instalasi; jangan pakai teks suara sebagai command mentah |
| Packaging | Requirements tanpa pin versi; belum ada PySide6/winsdk | Buat environment dan pin versi yang sudah dibuktikan kompatibel |

Ini temuan inspeksi, bukan klaim seluruh bug runtime telah direproduksi. Jangan mengubah baseline diam-diam saat menyiapkan rencana.

## Perintah yang tersedia sekarang

Jalankan dari `kai/`:

```powershell
python -B test_intents.py
python -B main.py --text "puter tulus" --dry
```

Tes parser pertama sudah dijalankan. Contoh CLI dry di atas tersedia menurut kode, tetapi belum dijalankan dalam sesi ini. `python main.py --login`, `python main.py`, dan `--text` tanpa `--dry` dapat memicu login, mikrofon, unduhan atau aksi nyata; belum diuji. `python main.py --island --demo` dan `--island` belum valid pada baseline.

## Langkah berikutnya

Tinjau arah visual dan perilaku monitor/fullscreen, lalu M1 demo tanpa mikrofon/API. Sesudah itu integrasi media/volume dan pengujian suara sesuai roadmap. Hasil 98/98 tetap baseline regresi, bukan sertifikat kesiapan produk.
