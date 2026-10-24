# Desain dan interaksi Kai

> Cakupan aktif 0.3.0: lihat [16](16-kai-productivity.md). Clipboard/Command/Notes/Smart Shelf/Musik/Sistem; jam dan logo tetap. Fokus/Agenda/Waktu/Cuaca di bawah adalah arsip sumber, bukan fitur runtime aktif.

> Revisi aktif 22 Oktober 2026: lihat [15](15-redesain-island.md) untuk kaca charcoal, compositor native, kontrol child island, logo robot, Kai.exe dan Shelf screenshot otomatis. Desain navy/dialog di bawah merupakan baseline historis.

> Pembaruan 22 Oktober 2026: Default terbaru tanpa suara; caption aktif mengarahkan klik membuka panel. Media/audio hanya saat tab Media dibuka; popup volume/headset otomatis di luar tab nonaktif. Pil 56 × 20, expanded 320 × 68 DIP dan navy gelap tetap dipertahankan. Transparansi Qt aktif, native Acrylic belum lolos visual.

Status: pengguna memilih **navy dengan glow biru seperti referensi Kai** pada 22 Oktober 2026. Pilihan arah sudah diputuskan; nilai numerik dan detail interaksi berikut masih titik awal prototipe, belum hasil uji.

Revisi pengguna setelah melihat prototipe: **lebih kecil dan kaca gelap seperti panel notifikasi Windows**, dengan warna latar ikut terasa. Ini mengurangi dominasi navy/glow, bukan menambah efek neon. Implementasi compact sudah diuji pada scaling 150%; blur Acrylic native masih belum lolos verifikasi. Material aktif berupa transparansi Qt, belum blur latar sungguhan.

## Pembacaan referensi

![Referensi bentuk Dynamic Island](references/iphone-dynamic-island.png)

Gambar pertama menunjukkan satu wadah hitam yang berubah ukuran menurut tugas. Informasi compact memakai dua ujung; mode expanded memberi ruang bagi label dan kontrol. Warna menandai kejadian: hijau sukses/perangkat, biru aktivitas, kuning timer, merah rekam/peringatan. Ambil kontinuitas bentuk, kejelasan status, dan pengelompokan tindakan. Latar magenta, layanan iPhone, dan desain persisnya tidak menjadi target Kai.

![Referensi 17 keadaan Kai di Windows](references/kai-ui-states.png)

Gambar kedua menunjukkan posisi atas tengah yang stabil, permukaan navy transparan dengan rim terang, aksen biru, avatar Kai, metadata kiri, serta kontrol ringkas kanan. Semua 17 panel merupakan variasi waktu/konteks, bukan dashboard yang tampil sekaligus. Bentuk lebih lebar untuk musik/volume dan lebih tinggi untuk lirik/monitor/agenda. Angka jam, Jakarta, suhu, nama orang, lagu, perangkat, dan jadwal pada gambar adalah contoh, bukan preferensi atau data pengguna.

## Tiga arah yang dipertimbangkan

| Arah | Keuntungan | Biaya/risiko |
| --- | --- | --- |
| A — Kaca Windows yang tenang | Selaras sumber; pil hitam idle, kaca mengikuti tema saat expanded; aksen hanya saat relevan | Perlu uji kontras berbagai wallpaper |
| B — Hitam solid menyerupai referensi iPhone | Kontras kuat, rendering sederhana, cocok sebagai fallback | Lebih sedikit rasa liquid glass |
| C — Navy dan glow biru seperti gambar Kai, dipilih pengguna | Identitas visual kuat dan mudah didemokan | Intensitas glow dan kontras pada tema terang perlu diuji |

Keputusan: C sebagai arah utama. Pil collapsed tetap hitam; kartu expanded memakai permukaan navy dan rim/glow biru. Usulan intensitas: glow lembut saat expanded biasa, lebih kuat saat mendengarkan, tanpa pulse idle terus-menerus. B menjadi fallback solid untuk reduced transparency/high contrast. Cara mengikuti tema terang/accent Windows perlu diselaraskan tanpa menghilangkan pilihan navy pengguna. Avatar belum diputuskan; desain harus tetap jelas dengan ikon sederhana.

## State dan aturan transisi

Pisahkan **bentuk** (`collapsed`, `expanded`) dari **isi** (`default`, `media`, `volume`, `device`, `listening`, `processing`, `result`, `timer_due`, serta panel lanjutan). Tema bukan state aktivitas.

| Pemicu | Bentuk/isi berikutnya | Aturan |
| --- | --- | --- |
| Startup demo | Collapsed | Tidak mengambil fokus aplikasi |
| Kursor masuk zona aktivasi | Expanded/default atau media aktif | Buka dari geometri yang sedang terlihat |
| Kursor keluar | Tunda collapse 700 ms | Batalkan delay jika masuk kembali |
| Tahan Ctrl+Space | Expanded/listening | Indikator mikrofon segera tampil; jangan menunggu animasi |
| Lepas hotkey | Expanded/processing | Mikrofon tutup; progress jujur, bukan persen rekaan |
| Hasil/error perintah | Expanded/result | Usulan tampil 3 detik; detail lebih panjang boleh 5 detik |
| Volume berubah | Expanded/volume | Perbarui nilai kartu yang sama; usulan timeout 1,5 detik sejak perubahan terakhir |
| Headset tersambung/terputus | Expanded/device | Usulan tampil 3 detik; deduplikasi event perangkat |
| Timer/alarm jatuh tempo | Expanded/timer_due | Tetap tersedia sampai diakui; cara bunyi/ulang perlu keputusan |
| Escape/dismiss | Kembali ke konteks sebelumnya | Tidak membatalkan timer atau menghapus notifikasi Windows |

Usulan urutan saat event bersamaan: alarm/timer selesai → mendengarkan/proses Kai → hasil/error aksi → volume → perangkat → notifikasi → media/default. Jika alarm datang saat PTT, tampilkan penanda alarm dan bunyi sesuai kebijakan, tutup rekaman sebelum berpindah kartu, jangan putus audio diam-diam. Finalisasi kebijakan ini saat implementasi state controller.

Jangan menutup kartu saat pengguna menyeret slider, drag file, menavigasi keyboard, atau sedang melakukan tindakan di kartu. Setelah toast habis, pulihkan media/default bila kursor masih di atas island; jika tidak, collapse. Hanya satu kartu utama; event sejenis digabung agar tidak berkedip dan mengantre tanpa batas.

## Hit testing dan fokus

Collapsed harus click-through. Karena click-through menghalangi hover native biasa, zona aktivasi dideteksi terpisah melalui posisi kursor global dengan interval hemat daya. Expanded hanya menerima input di bentuk island; sudut transparan tidak boleh menjadi kotak penangkap klik. Gunakan zona keluar sedikit lebih besar untuk menghindari expand/collapse berulang di tepi.

Jendela tanpa frame, tetap di atas jendela biasa, tanpa merebut fokus ketika toast muncul. Akses keyboard diberikan melalui jalur eksplisit, dengan fokus terlihat dan Escape untuk keluar. Kebijakan fullscreen, lock screen, monitor kedua, dan posisi taskbar masih perlu keputusan. Jangan menjanjikan tampil di atas aplikasi exclusive fullscreen.

## Token awal (logical pixels/DIP)

| Token | Usulan awal |
| --- | --- |
| Pil collapsed | 56 × 20, radius 10 (revisi pengguna) |
| Jarak dari tepi atas | 8; pusat horizontal pada monitor utama |
| Default expanded | 320 × 68 (revisi pengguna) |
| Kartu musik/volume | Lebar 400–460; tinggi 76–96 sesuai isi |
| Panel rinci | Lebar sampai 520, tinggi sampai 220; clamp ke work area |
| Padding/gap | 16 / 8–12 |
| Radius expanded | 23 pada kartu compact; mengikuti ukuran saat morph |
| Font | Segoe UI Variable bila tersedia, fallback Segoe UI |
| Teks | Compact: primer 14–15, sekunder 10–11, jam 23; uji keterbacaan DPI lain |
| Target tombol | Sekitar 32–36, indikator fokus jelas |
| Warna gelap awal | Dasar #10151F; primer #F4F7FB; sekunder #B5C0CF; aksen biru #5BA4FF |

Nilai warna belum merupakan rasio kontras terukur. Uji pada wallpaper terang, gelap, dan ramai; tingkatkan opasitas sebelum menambah efek. Light mode memakai permukaan terang dan teks gelap yang diuji tersendiri. Warna sukses/peringatan/error selalu disertai ikon/teks.

## Material dan motion

- Tahap awal: kaca buatan dengan fill, gradasi halus, tepi terang tipis dan shadow lembut. Acrylic/Mica diuji terpisah; jangan mengandalkan CSS blur pada aplikasi Qt.
- Pil idle tetap hitam sesuai sumber. Expanded memakai navy dan glow biru sesuai pilihan pengguna; accent Windows dapat memengaruhi detail sekunder setelah diuji. Usulan glow lembut pada kartu biasa dan lebih kuat pada status listening, dengan opsi mengurangi glow.
- Morph berjangkar atas tengah; lebar/tinggi/radius berubah serempak, teks tidak diregangkan bersama wadah. Isi crossfade setelah ruang cukup.
- Usulan morph 180–260 ms, pergantian isi 100–160 ms; tanpa bounce default. Angka disetel dari uji, bukan dianggap rumus wajib.
- Animasi dapat dibalik dari nilai layar saat ini, termasuk hover cepat; tidak ada antrean animasi yang wajib selesai.
- Feedback klik/slider langsung. Pemicu keyboard tidak diberi jeda dekoratif. Bila state island perlu morph, indikator “Mendengarkan” tampil segera dan aksi tidak menunggu morph selesai.
- Reduced motion: transisi singkat/static tanpa pegas. Reduced transparency: solid. Hentikan repaint animasi saat idle.

## Kriteria desain

Judul panjang dipotong dengan jalur melihat teks penuh. Angka waktu memakai lebar stabil bila tersedia. Cover yang hilang memakai placeholder lokal. Metrik tak tersedia menunjukkan “Tidak tersedia”, bukan nol. Tidak memakai emoji sebagai aset ikon produksi. Seluruh UI harus tetap dapat dipahami tanpa avatar, animasi, blur, atau koneksi internet.

Lihat [pemetaan skill](09-pemetaan-skill-ui.md) untuk aturan yang dipakai dan penyesuaian desktop.
