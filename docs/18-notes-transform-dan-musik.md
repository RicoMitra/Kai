# Notes, Fast Transform dan kontrol Musik

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


## Latest approved UI — 23 October 2026

English is now the primary interface language: navigation, settings, buttons, tooltips, clipboard/notes/Shelf statuses and conversion errors. Personal notes, copied text, filenames and song lyrics are never translated. Historical Indonesian documentation and inactive feature code remain archives.

The collapsed island is **plain opaque black, 72 × 24 DIP**. Other pages and the clock/logo hover are black. Opening the island brings its top edge to the physical screen edge, with flat upper corners and rounded lower corners. Clock/date and the user's robot identity remain on hover. The previous sleeping-eye/glossy capsule is superseded. While **Music is open and playing**, a static dark gradient follows the album cover; paused/no-cover/other pages return to black. A single 8 × 8 average is calculated from the already bounded 64px cover when the track/cover becomes available. No large blur, animation loop or extra image cache. Native composition/backdrop surfaces are no longer created for this opaque design.

Typography uses installed **Segoe UI Variable**; Qt confirmed this family resolves correctly. It follows the iPhone reference's clean hierarchy using Windows typography. Spring transitions retain velocity on reversal, stop when settled and respect Reduce motion. Long active lyrics wrap without ellipsis; a small scrollbar/wheel makes overflow accessible. Adjacent lines may scroll out of the viewport. Reference photos are retained in docs/references/music-lyrics-top-edge.jpg, iphone-island-motion.jpg and iphone-island-calendar.jpg; the calendar picture is visual inspiration and does not restore Calendar.

Fast Transform has **FROM / TO columns** and a center divider. FROM: PNG/JPG/PDF/Word; TO: PDF/MD/Word. Only the approved workflows remain: **JPG or PNG → PDF; PDF → MD; PDF → Word (.docx); Word (.docx) → PDF**. One input file and one output per job. PDF-to-JPG, other conversions, Notes input and MD/TXT input are removed. Incompatible output buttons are disabled automatically. PDF→Word extracts editable text; Word→PDF preserves basic paragraphs/headings/tables/images, with complex layout limits. No Word process or new dependency. Save or Clear removes temporary results; leaving/closing also cleans up after cancellation/reap. Original files and saved copies are retained.

Skills used selectively: ponytail full, emil-design-eng, apple-design and UI/UX Pro Max. The latter's design-system search was run; its landing-page/blue palette/web-font suggestions were discarded because the user's approved black native desktop brief takes precedence. Applied checks: grouping, contrast, pressed/focus/selected states, keyboard access, bounded image work and reduced motion. No web UI framework installed.

Verification: 37 unit tests plus six conversion fixture checks cover PNG/JPG→PDF, PDF→MD/DOCX, DOCX→PDF and scanned PDF→MD with real local Windows OCR. Disposable engine isolation/reap, one-file restriction, unsupported direction rejection, save/cleanup/cancel and English labels are checked. Native hover/click-through/focus/reentry/reversal and six-page navigation pass at current 150% DPI. tools/check_appearance.py captures owned widgets with generated cover/lyrics, verifies column fit, wrapping, top-edge attachment, installed font and disabled backdrop. Account playback/seek was not mutated. See the latest status for measured memory and its limits.


## Historical specifications — superseded by the English contract above

23 Oktober 2026, lanjutan 3.0.0. Ini kontrak terbaru setelah docs/17. Pengguna mengoreksi kata Shelf: gambar checklist ditujukan untuk **Notes**, sehingga desain Shelf tidak diubah oleh permintaan tersebut. Pengguna juga menyetujui mengganti Command sepenuhnya dengan **Fast Transform**, meminta konversi 1–2 file lalu dibersihkan, dan klik progress/volume dalam Musik.

## Cakupan produk

Enam halaman: **Transform, Clipboard, Notes, Shelf, Musik, Pengaturan**. Quick Command tidak ada di nav/tray/default; Ctrl+Alt+Space kini membuka Fast Transform. Tidak ada pemindaian aplikasi Start Menu saat panel dibuka. Parser/kalkulator/CLI lama masih arsip/dev, bukan fitur pencarian produk aktif. Sistem tetap dihapus, suara/WhatsApp/waktu/cuaca/agenda/fokus tetap nonaktif. Stack Python/PySide6 dan compositor native dipertahankan.

## Notes sesuai dua referensi

**Koreksi terakhir pengguna mengungguli rancangan detail di bawah:** Notes disederhanakan menjadi satu daftar, **+ Catatan**, lingkaran selesai dan **Hapus**. Tidak ada pencarian, editor, subheading atau halaman detail. + Catatan menampilkan input sebaris, ketik lalu Enter; autosave 350 ms/flush tetap. Typo ditangani dengan hapus dan buat ulang. Pin tersedia lewat klik kanan agar toolbar tetap ringkas. Nama/isi lama tetap di DB dan dapat diekspor dari Dari Notes pada Transform. Rancangan detail/kuning/Edit berikut adalah riwayat yang sudah diganti, bukan UI aktif.

Daftar catatan memakai baris charcoal, lingkaran lavender, judul dan baris isi kedua jika ada. Klik lingkaran atau Space menandai seluruh catatan selesai; judul dicoret dan posisi tidak meloncat hanya karena dicentang. Pin tetap di atas. Nama/jam pada referensi hanya contoh, bukan jadwal otomatis.

The earlier detail/editor/yellow-checklist design was canceled. Notes now has only + Note, an inline input/Enter, the task list, check circles and Delete. Pin is in the context menu. Autosave/flush persist. There is no search, detail or editor page. Rows use a native delegate with no per-note widgets or blur. Older notes-edit-detail.png is historical; notes-list-reference.png and notes-black.png show the newer approach.

## Fast Transform lokal

| Input | PDF | MD | JPG |
| --- | --- | --- | --- |
| PNG/JPG | Gambar dalam halaman A4 | Teks OCR Windows lokal | JPG, alpha diratakan putih |
| PDF | Salinan PDF, original tetap | Ekstrak teks; OCR fallback untuk scan maksimal 2 halaman | Maksimal 2 halaman awal |
| Word `.docx` | Paragraf/heading/tabel/gambar dengan layout sederhana | Teks/heading/tabel; gambar diberi penanda | Layout sederhana menjadi PDF lalu maksimal 2 halaman awal |
| Notes/MD/TXT | Teks ke halaman PDF | Simpan teks | Teks ke PDF lalu maksimal 2 halaman awal |

Input **Word adalah `.docx`**, bukan binary `.doc`; simpan .doc lama menjadi .docx dahulu. Tidak memakai Microsoft Word/LibreOffice/webview atau menginstal paket baru. Header/footer, bentuk, chart, footnote dan layout kompleks Word belum direproduksi setara Word. DOCX maksimal 8 gambar tertanam, gambar diecilkan untuk mode hemat; gambar tidak di-OCR saat DOCX→MD. Markdown dari PDF mempertahankan teks, bukan tata letak/semantik sempurna. PNG→MD memakai OCR, bukan menyisipkan link gambar lalu mengklaim teks sudah diekstrak.

OCR menggunakan bahasa yang sudah terpasang di Windows; saat diperiksa laptop ini memiliki en-GB/en-US. Tidak mengunduh model atau mengirim dokumen ke jaringan. Hasil pengenalan perlu diperiksa, khususnya bahasa/tabel/rumus. PDF terkunci/rusak, format tidak didukung dan hasil OCR kosong menghasilkan error yang jelas.

## Batas dan pembersihan

- Satu worker konversi aktif, 1–2 input, maksimal 2 hasil. Ukuran input maksimal 20 MiB/file; gambar maksimal 24 megapiksel sebelum downsample (sisi terpanjang 2048). PDF maksimal 50 halaman, render JPG sisi terpanjang 1800. DOCX total isi ZIP 32 MiB, XML utama 4 MiB dan teks 200.000 karakter.
- PDF/dokumen banyak halaman→JPG menggunakan satu input per proses agar maksimal dua hasil; UI menyebut dua halaman awal. Untuk proses dua file, jangan menyelipkan dokumen multipage yang membutuhkan lebih dari batas hasil.
- QtPdf dan WinRT OCR hanya di worker `transform.py`, tidak diimpor parent. Selesai/error/cancel/timeout menutup/reap proses. Batas waktu 90 detik dari UI. Tidak ada daemon OCR atau model tersimpan dalam RAM.
- Hasil sementara maksimal dua path, bukan gambar/bytes besar di parent, berada di `%LOCALAPPDATA%/Kai/transform-temp/job-*`. Simpan Hasil menyalin ke folder pilihan tanpa overwrite nama yang sudah ada, lalu menghapus direktori sementara. Memulai proses baru, Bersihkan, pindah halaman atau menutup panel menghapus hasil sementara. Jika proses masih bekerja, pembatalan/reap didahulukan; cleanup menunggu worker selesai. Salinan yang sengaja disimpan dan original tidak dihapus.
- Worker aktif tetap dapat menaikkan RAM sesuai isi dokumen. Pembatasan 1–2 file dan pelepasan proses bukan jaminan total aktif di bawah 40 MiB. Crash paksa/listrik mati dapat meninggalkan direktori job; pembersihan lifecycle normal sudah diuji, bukan janji cleanup setelah setiap crash.

## Musik

Klik progress bar mengirim rasio 0–1 ke worker SMTC. Target timeline dihitung dari start_time + durasi, lalu diubah ke tick 100 ns untuk API Windows. Klik ke kiri/kanan dapat mundur/maju ke posisi yang dipilih. Tidak berpura-pura sukses jika pemutar menolak; tanpa durasi valid, seek tidak dikirim.

Volume mempunyai tombol **−/+** langkah 5%, rail klik/drag, dan VOL untuk mute. Tetap hanya aktif saat Musik dibuka. Tidak menambah listener idle atau proses suara. Kontrol ini mengubah volume output sistem yang sudah dipakai Core Audio, bukan volume per-aplikasi Spotify.

## Bukti dan batas pengujian

37 unittest lulus: termasuk Notes tambah/centang/hapus/pin/flush tanpa search/editor, konversi Note→PDF→MD di worker tanpa engine PDF parent, batas dua input, click seek 25%/75%, volume ±5 dan kalkulasi tick nonzero start. `tools/check_transform.py` menguji 20 pasangan dari PNG/JPG/PDF/DOCX/MD ke PDF/MD/JPG dengan file contoh yang dibuat sendiri, OCR Windows nyata, hasil signature/teks, engine tidak di parent, worker reaped, Save membersihkan sementara, pindah halaman membatalkan, dan hasil tersimpan tetap ada.

`tools/check_shelf_v3.py` tetap mencakup Shelf/clipboard/dedupe/download serta Notes daftar sederhana tanpa subheading/search/detail/editor. Native klik seek/volume pada widget diuji dengan state tiruan; perpindahan lagu/perubahan volume fisik Spotify pengguna belum dilakukan dalam tes, sehingga dukungan aplikasi pemutar nyata tetap perlu penggunaan personal. Konversi dokumen kompleks/arbitrary bukan dijamin hanya karena fixture dasar lulus. RAM terbaru dan hasil native lain di 07.

## Review UI

| Before | After | Why |
| --- | --- | --- |
| Daftar/editor berdampingan sepanjang waktu | Daftar vertikal; isi baca, Edit saat diminta | Mengikuti referensi dan mengurangi bidang kontrol serentak |
| Checkbox bawaan terpisah dari isi | Tanggal dan lingkaran kuning, tanpa subheading | Koreksi terakhir pengguna |
| Quick Command / indeks aplikasi | Fast Transform maksimal dua input/hasil | Keputusan penggantian pengguna |
| Progress hanya indikator | Progress dapat diklik, volume −/+ | Kontrol musik langsung tanpa perintah |

## Sumber primer yang diperiksa

[Qt QPdfWriter](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPdfWriter.html), [QImageReader](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QImageReader.html), [QPdfDocument](https://doc.qt.io/qtforpython-6/PySide6/QtPdf/QPdfDocument.html), [Windows OcrEngine](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine). API Word ExportAsFixedFormat sempat diperiksa sebagai alternatif, tetapi **tidak digunakan** agar tidak menjalankan Word sebagai proses eksternal yang lebih berat dan sulit dibatalkan bersih.
