# Kai sebagai island, bukan panel aplikasi

22 Oktober 2026. Arahan pengguna terbaru menggantikan warna navy/glow sebelumnya: kaca gelap, gradasi reflektif yang lebih halus, kontrol langsung seperti gambar musik/lirik dan shelf. Semua fitur dipertahankan kecuali WhatsApp dan suara; robot PNG pengguna menjadi identitas resmi. Perubahan ini adalah pelaksanaan arahan tersebut, bukan permintaan untuk mengubah stack.

## Desain yang dijalankan

Tiga keadaan dalam satu jendela: pil idle 56 × 20 DIP; hover bar compact 320 × 68; klik membuka bidang island 540 × 270–356 untuk kontrol. Bidang besar tetap tertambat di atas layar, bukan jendela panel/dialog terpisah. Kembali mengecil saat kursor menjauh; fokus input dan file picker menahan collapse. Escape kembali/menutup. Semua morph mempertahankan velocity dan reduced motion.

Kaca menggunakan charcoal, rim putih tipis dan pantulan pearl/lavender/champagne; tidak ada orb biru atau blok tombol biru tua. Media memadukan cover, judul/artis, progres dan transport di kiri serta potongan lirik di kanan. Shelf berupa ikon file dengan nama/ukuran dan drag keluar; tidak menyalin/menghapus file asli. Header kecil, navigasi halaman berupa tombol ringkas; timer/fokus, jadwal, cuaca, sistem dan pengaturan tetap fungsional. Tidak ada data musik/cuaca pribadi palsu sebagai default.

Alternatif yang dipertimbangkan: mempertahankan dialog lama (ditolak oleh arahan pengguna); menulis ulang ke web/WPF (menambah runtime tanpa bukti perlu); memperbarui overlay Qt dan memakai API compositor Windows (dipilih). Blur harus dibuktikan di atas pola milik tes; API menerima panggilan belum berarti blur berhasil. Tidak menangkap layar terus-menerus untuk blur palsu.

Logo asli disimpan tanpa menggambar ulang. Turunan PNG kecil/ICO hanya konversi format/resolusi untuk ikon, tray dan penanda island. `Kai.exe` adalah launcher Windows GUI yang langsung memulai Pythonw, tanpa CMD/PowerShell atau proses launcher yang ditahan selama aplikasi hidup. Runtime tetap di LOCALAPPDATA; source/data pribadi tidak dicampur. Tidak mengubah autostart.

Referensi yang diperiksa: [Animmaster Lib](https://animmasterlib.dev/), [Skiper UI](https://skiper-ui.com/components), [Unlumen](https://ui.unlumen.com/). Ambil prinsip material, hierarki dan motion; tidak menyalin komponen berbayar atau memasang React/GSAP.

## Rencana dan verifikasi

- [x] Aset logo + launcher GUI, uji klik aplikasi tanpa console dan error runtime melalui dialog.
- [x] Prototipe native glass terukur pada pola tes, pilih jalur yang benar-benar terlihat.
- [x] Overlay tiga keadaan; pindahkan panel menjadi isi island, desain ulang musik/shelf dan semua halaman sekunder.
- [x] Hapus UI/listener WhatsApp serta referensi aktif; suara tetap tidak dimuat.
- [x] Uji hover/retarget/fokus input/Escape/drop/worker; regresi backend; periksa screenshot widget sendiri.
- [x] Ukur RAM idle dan setelah bidang island ditutup, lalu perbarui panduan, status dan paket.

Target RAM privat idle 20–30 MiB tetap sasaran, bukan batas seluruh proses saat layanan berjalan. Biaya compositor dan sistem tidak disembunyikan.

## Screenshot otomatis — permintaan tambahan

Fokus pemantauan adalah file screenshot yang benar-benar disimpan ke Windows Known Folder Screenshots, termasuk pengalihan OneDrive. QFileSystemWatcher memakai event direktori; tidak polling saat idle. Dua pengamatan ukuran berkas menghindari file setengah ditulis, retry dibatasi. File lama diabaikan. Shelf menyimpan path SQLite, bukan duplikasi gambar; thumbnail kecil dibaca bertahap setelah morph. Ctrl+klik/Ctrl+A memilih beberapa item; QDrag mengirim URL lokal dengan CopyAction. Keluarkan/Bersihkan hanya menghapus referensi.

Bukti: tools/check_redesign.py memverifikasi lima screenshot melalui event folder asli di direktori sementara, penghapusan referensi mempertahankan file, tidak masuk ulang, serta payload drag empat item setelah satu dikeluarkan. Delapan halaman tetap berada sebagai child island. Bukti ini belum merupakan uji drop di setiap aplikasi pihak ketiga.

Blur menggunakan Windows.UI.Composition dengan Gaussian effect dan backdrop brush pada lapisan native yang click-through. tools/probe_host_glass.py mengukur pelembutan tepi pada pola milik tes; tidak mengambil latar desktop untuk rendering produksi. Jalur layered transparent diperiksa melalui hit testing native. Tanpa API tersedia, fallback transparansi Qt.
