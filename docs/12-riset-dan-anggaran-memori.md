# Riset dan pengukuran RAM Kai

## Latest verification and memory target — 23 October 2026

Current UI: English; black collapsed/other pages; album tint only in open, playing Music; wrapped/scrollable lyrics; flat upper corners attached to screen top. Notes is a simple checklist. Fast Transform has four workflows only: PNG/JPG→PDF, PDF→MD, PDF→DOCX, DOCX→PDF; one input and one output. Unsupported directions/Notes input were removed at the owner's request. Settings/clock/robot/Shelf/clipboard/music remain.

The owner explicitly targets **50 MiB for all Kai processes combined, including conversion**. This is **not a verified hard ceiling**. Latest whole-tree sample including media startup, all four conversion workflows and scanned-PDF OCR: **23.33 MiB peak private working set**, **39.39 MiB peak total working set**, **93.41 MiB peak private committed memory**. Sampled every 100 ms, maximum three simultaneous processes, generated 1600×900 image and one-page PDFs, harness excluded. Windows paging explains why resident memory can look far lower than allocated memory. Sampling misses short peaks; larger inputs, sustained use, different memory pressure, other monitors/DPI and compositor costs are not covered. No working-set trimming or memory-limit crash policy used. **Do not claim the all-input 50 MiB requirement achieved.**

Latest idle benchmark before the final conversion-direction restriction: startup private commit median 30.31 MiB; after all six pages close, 37.88 MiB. Private resident medians 1.12/1.58 MiB reflect severe paging, not a claim that Kai only needs 1–2 MiB. These are short tests, not a universal budget.

Implemented reductions: no backdrop/composition allocation for opaque black, one conversion worker, media worker reaped before conversion begins, lyrics task canceled outside Music, RGB32 dedupe in 64-row strips instead of another full bitmap, tiny bounded album-color sample, native delegate rows, bounded thumbnails and stopped idle animation timer. PDF text extraction uses QCoreApplication in its disposable worker, avoiding a GUI font environment; DOCX→PDF still uses Qt text/layout, scanned PDF extraction still uses local Windows OCR. One-file concurrency does not cap the memory required to decode that one file.

Evidence: artifacts/island/memory-active-verification.json; memory-core.json; memory-demand-after-panel.json; artifacts/productivity/transform-verification.json and appearance-verification.json. tools/measure_active_memory.py generates isolated fixtures, opens the real media worker read-only and measures the GUI/redirector/all descendants. No private user files, clipboard, login or account playback changes are used. tools/check_appearance.py verifies the final layout with synthetic artwork/lyrics. Remaining strict-budget work would require profiling and proving a lower-memory native conversion implementation; a framework rewrite is not automatically a guarantee and was not performed.

Sources checked: [Microsoft Working Set](https://learn.microsoft.com/en-us/windows/win32/memory/working-set), [SetProcessWorkingSetSize](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsize), [Qt QImageReader](https://doc.qt.io/qt-6/qimagereader.html). Working-set trimming affects paging; it does not remove the underlying allocations. Decoder scaling savings depend on the image format/plugin.


> Revisi paling akhir Notes tanpa editor + Transform: cold commit 31,21 MiB, privat resident median 3,76 (1,61–16,55); pascaenam halaman commit 38,80 MiB, privat resident median 1,71 (1,39–1,73). Resident dipengaruhi paging kuat, **bukan footprint 1–4 MiB**. Ukur konversi aktif terpisah; run panel ini tidak mengonversi file besar. Worker reaped, tanpa trim paksa. Konteks/metrik lengkap di blok teratas 07; angka berikut adalah riwayat.

> Run GUI 3.0 terbaru 23 Oktober 2026: cold private WS 26,66 / total WS 65,89 / commit 30,93 MiB. Setelah seluruh halaman ditutup private WS 53,50 / total 128,59 / commit 60,30. Target 20–40 tercapai cold tetapi belum pascasiklus. Worker reaped; tidak trim paksa. Commit dekat versi sebelumnya tetapi resident berbeda, jadi 37,10 lama bukan hasil baru. Lihat 07 dan JSON untuk detail; seluruh angka berikut arsip.

> Aktif 0.3.0 (GUI pythonw, dua proses, data sementara): cold private WS 26,60 MiB / total WS 65,99 / commit 30,98; setelah seluruh halaman ditutup median private WS 37,10 / total 87,25 / commit 60,17. Target privat idle terbaru 20–40 tercapai pada sampel, bukan hard cap fitur aktif. DWM/sistem tidak dihitung; detail di 07. Angka lama di bawah arsip.

> Benchmark terbaru redesain kaca: cold idle private WS 26,66 MiB, total WS 69,93 dan private commit 31,64. Setelah siklus Media, commit 59,22 MiB; worker berhenti. Private WS pascasiklus terpengaruh paging kuat sehingga tidak dipakai sebagai klaim footprint beberapa MB. DWM/sistem di luar pengukuran; target privat idle bukan hard cap. Bukti JSON terbaru dan konteks ada di [07](07-status-dan-verifikasi.md). Angka lama di bawah adalah arsip.

22 Oktober 2026. Pilihan pengguna terbaru: **suara nonaktif**, media/audio hanya ketika tab Media dibuka, prioritas **20–30 MiB RAM privat idle**. Rancangan Whisper on-demand sebelumnya digantikan keputusan ini; model tidak dimuat maupun diunduh.

## Hasil lokal terbaru

`tools/measure_ui_memory.py` memakai Windows PSAPI EX2 dan menjumlahkan launcher serta seluruh turunannya. Ini penting: executable venv merupakan launcher, sehingga membaca PID itu saja sempat menghasilkan angka keliru 4–5 MiB. Hasil tersebut sudah dibuang/diganti. Tidak memakai EmptyWorkingSet, working-set trim, atau trik menyembunyikan helper.

| Konfigurasi | Private working set median | Total working set median | Private commit median |
| --- | --- | --- | --- |
| Default terbaru: tanpa suara, media/audio on demand | **22,64 MiB** | 63,24 MiB | 26,80 MiB |
| Varian on demand eksplisit, sebelum perapian terakhir | 22,46 MiB | 63,04 MiB | 26,58 MiB |
| Histori: media/audio selalu hidup, tanpa suara | 41,50 MiB | 94,82 MiB | 48,37 MiB |
| Histori: layanan selalu hidup + hook PTT, tanpa model | 47,85 MiB | 104,28 MiB | 54,48 MiB |

Default: warmup 3 detik, 10 sampel berjarak 1 detik. Private working set pada semua sampel default 22,64 MiB; total WS 63,23–63,24. File mentah `artifacts/island/memory-core.json`; angka historis bukan mode suara yang masih tersedia di launcher.

Skenario buka Media pada 1,5 detik, tutup pada 5 detik, sample sesudah detik 9 memastikan panel benar terbuka, worker sempat hidup dan kemudian hilang (`panel-cycle-verification.json`, semua true). Setelah panel: private commit 32,12 MiB; resident privat median 7,97 MiB dan total WS 23,50 MiB. **Angka resident rendah setelah panel tidak dijadikan janji footprint 8 MB**: OS sedang mengalami tekanan RAM dan memindahkan halaman keluar. Kenaikan commit dibanding startup menunjukkan cache/allocator Qt tidak seluruhnya kembali ke baseline meskipun proses native sudah mati. Tes ini satu siklus, belum membuktikan bebas leak harian.

## Metrik dan batas klaim

Working set mencakup halaman resident proses, termasuk yang bisa dibagi. Menjumlahkan WS beberapa proses dapat menghitung halaman shared dua kali; ini bukan ukuran RAM sistem unik. Private working set mengukur resident privat; private commit mengukur alokasi privat dengan backing dan tidak harus semuanya berada di RAM. [Microsoft Working Set](https://learn.microsoft.com/en-us/windows/win32/memory/working-set), [PROCESS_MEMORY_COUNTERS_EX2](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex2).

Kolom Memory Task Manager sering mengacu ke private working set; bandingkan metrik yang sama. [Microsoft Edge memory investigation](https://blogs.windows.com/msedgedev/2021/01/13/investigate-microsoft-edge-memory-usage/). Satuan di sini MiB (2^20 byte), bukan MB desimal.

Target 20–30 tercapai pada **RAM privat idle dalam sampel pendek ini**, bukan hard cap total memori. Fitur aktif akan menaikkan penggunaan sementara. DWM/GPU, biaya sistem, halaman shared dan aplikasi lain tidak dapat disimpulkan dari satu angka proses. Run berikutnya dapat berbeda karena pressure OS, DPI, font, cache dan workload. Pada sesi ini RAM tersedia sempat hanya sekitar 180 MB; tidak ada model berat yang dimuat untuk benchmark.

## Penghematan yang benar-benar diterapkan

1. Entry point tidak lagi memiliki jalur suara aktif; tidak ada keyboard hook, mikrofon, model, CUDA atau numpy yang dimuat untuk idle. Paket suara tidak diperlukan requirements aktif.
2. SMTC/Core Audio hidup dalam worker proses hanya pada tab Media; keluar tab/panel menutup proses dan library native miliknya. Di luar itu tidak ada popup volume/headset otomatis, sesuai jawaban pengguna.
3. Cuaca, lirik, impor ICS, metrik dan aksi Spotify berjalan dalam proses sesaat dengan timeout. Menutup panel membatalkan task yang masih aktif. Parent Qt tidak menahan seluruh library integrasi setelah digunakan.
4. Panel dibuat saat dibuka; animasi timer berhenti setelah morph. Idle memakai pemeriksaan kursor/jam, bukan redraw terus menerus.
5. Tidak ada webview/React/GSAP/server, capture layar terus menerus, semua cover/lirik ditahan sekaligus atau riwayat audio/transkrip.
6. Data/cache/runtime di LOCALAPPDATA, bukan ribuan berkas environment di OneDrive. Ini mengurangi beban sinkronisasi, bukan klaim pengurangan RAM langsung.

Tidak melakukan rewrite C#/WPF karena target privat idle bisa dicapai dengan runtime Qt yang ada. Memperkecil kartu membantu render tetapi bukan pengganti pengukuran.

## Riset pembanding dan suara historis

Pembanding aplikasi pengguna dengan klaim 20–40 MB belum disebutkan namanya; tidak dapat memverifikasi workload/metrik identik. Proyek [Dynamic Island for Windows](https://github.com/sarthakaksh/Dynamic-Island-for-Windows) menunjukkan Win32/Direct2D dapat menghindari runtime web/Python, tetapi bukan bukti angka tepat untuk Kai. Pindah WPF tidak otomatis ringan: [proyek WPF ini](https://github.com/nazimferragh/windows-dynamic-island) melaporkan sekitar 200 MB pada setup tiga monitor penulisnya, bukan benchmark kita.

[faster-whisper benchmark primer](https://github.com/SYSTRAN/faster-whisper) melaporkan Small CPU int8 sekitar 1477 MB RAM pada workload mereka. Itu alasan membedakan model dari UI dan kemudian mengikuti pilihan pengguna untuk menonaktifkan suara. Kode proses STT yang sudah dibuat tetap disimpan nonaktif; akurasi audio/CUDA lokal belum diuji. Jangan memakai angka benchmark upstream sebagai prediksi tepat laptop pengguna.

## Pemeriksaan lanjutan

Ukur hover/popup berulang, buka/tutup semua panel, media/cover aktif, task gagal/offline, sleep/resume serta soak satu jam. Pantau private commit dan seluruh worker, bukan hanya kolom resident yang dapat turun karena paging. Jika memory terus bertambah, cari retensi sebelum menambah framework/menulis ulang stack. Jangan mengaktifkan kembali suara atau pemantau otomatis tanpa pilihan pengguna.
