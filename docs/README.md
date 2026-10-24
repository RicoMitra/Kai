# Dokumentasi pengembangan Kai

## Private GitHub publication

The new English [project README](../README.md) is generated from [readme-source.md](readme-source.md). See [19 — GitHub and privacy](19-github-and-privacy.md) for the owner-requested private publication, dependency/secret review, repository boundary and unresolved controls; [SECURITY.md](../SECURITY.md) for the current security model. The [preceding README](history/README-before-github.md) remains a historical record. Current UI, features and memory limitations below still apply.

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


**Koreksi Notes paling akhir:** hanya daftar/+ Catatan/centang/Hapus. Tidak ada cari, editor, detail atau subheading. Baca koreksi teratas 18; rancangan detail sebelumnya menjadi arsip. Transform tetap menggantikan Command, Sistem tetap dihapus.

**Cakupan terakhir:** [18 — Notes, Fast Transform dan Musik](18-notes-transform-dan-musik.md). Transform menggantikan Command; Notes daftar/detail checklist kuning tanpa subheading; Musik klik seek dan tombol volume. Enam halaman tetap, Shelf tidak berubah oleh referensi Notes. Baca blok teratas 07 dan handoff untuk bukti terbaru.

Koreksi terakhir 23 Oktober: **Sistem dihapus**, lima alat Command/Clipboard/Notes/Shelf/Musik + Pengaturan. Helper/tes metrik lama hanya arsip/dev. Lihat blok status terbaru sebelum memakai daftar fitur lama.

Aktif 23 Oktober 2026: **3.0.0**. Baca [handoff lengkap](../handoff.md), [revisi terbaru](17-revisi-shelf-notes-dan-context.md), dan blok teratas status 07. Clipboard kini teks/URL saja; gambar/unduhan di Shelf, Notes checklist/pin dan pil mata 72 × 24 DIP. Angka dan pilihan lama di bawah adalah jejak riwayat.

Disusun 22 Oktober 2026 dari seluruh 12 bagian [ide asli](../kai-dynamic-island.md), kedua gambar referensi pengguna, dan seluruh sembilan berkas dalam `kai.zip`. Dokumentasi ini mencakup rencana dan implementasi. Status terbaru berada di 07; proposal lama bukan bukti fitur selesai.

## Urutan baca

| Dokumen | Kegunaan |
| --- | --- |
| [01 — Kebutuhan dan cakupan](01-kebutuhan-dan-cakupan.md) | Seluruh fitur, batas biaya/privasi, 17 keadaan UI, keterlacakan sumber |
| [02 — Desain dan interaksi](02-desain-dan-interaksi.md) | Makna kedua referensi, state island, material, ukuran awal, animasi |
| [03 — Arsitektur dan data](03-arsitektur-dan-data.md) | Struktur kode, threading, integrasi, penyimpanan, kegagalan |
| [04 — Roadmap dan workflow](04-roadmap-dan-workflow.md) | Tahap sumber 1–8, urutan eksekusi, keluaran dan syarat selesai |
| [05 — Pengujian dan penerimaan](05-pengujian-dan-penerimaan.md) | Pembuktian fitur dan skenario Windows nyata |
| [06 — Keputusan dan pertanyaan](06-keputusan-dan-pertanyaan.md) | Yang sudah dipilih, yang diusulkan, dan verifikasi pengguna |
| [07 — Status dan verifikasi](07-status-dan-verifikasi.md) | Kondisi arsip/kode sebenarnya, perangkat, tes, celah implementasi |
| [08 — Kontrak perintah](08-kontrak-perintah.md) | Semua 58 pola sumber, intent, aturan normalisasi |
| [09 — Pemetaan skill UI](09-pemetaan-skill-ui.md) | Pemakaian gpt-taste, emil-design-eng, apple-design dan skill pendukung |
| [10 — Inventaris skill lokal](10-inventaris-skill-lokal.md) | Nama/deskripsi/lokasi seluruh skill pada direktori yang diperiksa, termasuk duplikasi |
| [11 — Implementasi island motion](11-rencana-island-motion.md) | Rencana M1 dan referensi library UI yang diminta pengguna |
| [12 — Riset dan anggaran memori](12-riset-dan-anggaran-memori.md) | Benchmark UI lokal, arti metrik, pembanding dan rancangan STT hemat RAM |
| [13 — Rencana penyelesaian](13-rencana-penyelesaian.md) | Cakupan versi lokal dan urutan pekerjaan |
| [14 — Panduan pakai](14-panduan-pakai.md) | Launcher, konfigurasi, privasi dan troubleshooting |
| [15 — Redesain island](15-redesain-island.md) | Arahan terbaru: kaca charcoal, logo robot, launcher GUI, screenshot Shelf |
| [16 — Kai productivity](16-kai-productivity.md) | Cakupan aktif: Clipboard/Command/Notes/Smart Shelf; jam/logo dan target RAM 20–40 MiB |
| [17 — Shelf, Notes dan konteks](17-revisi-shelf-notes-dan-context.md) | Kontrak aktif 3.0: dedupe piksel, unduhan, checklist/pin, preview dan mini island |
| [18 — Notes, Transform dan Musik](18-notes-transform-dan-musik.md) | Notes tanpa subheading, konversi lokal 1–2 file/hasil, cleanup worker, seek dan volume |
| [Handoff](../handoff.md) / [sumber](handoff-source.md) | Riwayat lengkap, penjelasan setiap MD/modul, lokasi data, tes dan inventaris otomatis |
| [Panduan agen](../AGENTS.md) | Konteks yang perlu dibaca setiap sesi kerja |

## Batas fakta dan usulan

- **Sumber**: keputusan/ide yang tertulis dalam dokumen pengguna.
- **Terverifikasi**: ditemukan dalam berkas atau diuji pada sesi ini; jenis buktinya selalu disebut.
- **Usulan**: rancangan untuk melengkapi kebutuhan; dapat direvisi sebelum implementasi.
- **Perlu jawaban**: pilihan yang berpengaruh pada perilaku, akses, atau cakupan produk.

Dokumen asli dan ZIP dipertahankan. Berkas hasil ekstraksi di `../kai/` adalah baseline kode. Gambar disalin ke [references](references/) agar tidak bergantung pada direktori Temp. Dokumen Markdown ini sendiri adalah sumber yang dapat diedit; tidak ada salinan hasil generate yang harus disinkronkan.

Keputusan aktif 0.3.0: kaca gelap reflektif, hover jam/tanggal/logo, enam alat Command/Clipboard/Notes/Shelf/Musik/Sistem. Fokus/Agenda/Waktu/Cuaca dihapus dari runtime/UI. Lihat 16; cakupan lama pada dokumen awal adalah arsip.

Revisi lanjutan pengguna: island dibuat lebih kecil dan kaca mendekati panel notifikasi Windows. Implementasi kini memakai kartu 320 × 68 DIP, pil 56 × 20 DIP, permukaan gelap transparan dan glow jauh lebih tipis. Target RAM harian diteliti di 12. Baca status terbaru sebelum bagian baseline historis.

## Cara memelihara

Saat ada keputusan pengguna, ubah 06 lalu dokumen teknis terkait. Saat ada implementasi/tes, ubah 07 dan kaitkan bukti dengan milestone 04. Jangan mengubah status menjadi selesai sebelum kriteria 05 terbukti. Saat menambah pola, perbarui 08 dan pengujian parser. Implementasi dan pengujian terbaru dicatat di 07; bagian baseline historis dipertahankan.

Keputusan terakhir: suara nonaktif, media/audio hanya ketika tab Media dibuka. Default baru terukur 22,64 MiB private working set idle; total WS 63,24 MiB. Gunakan panduan 14 untuk perilaku aktif; bagian suara dalam sumber/rencana lama adalah backlog.
