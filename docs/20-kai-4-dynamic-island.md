# Kai 4.0 — Dynamic Island design reference

27 Oktober 2026. Arahan pemilik terbaru: UI 3.0 terasa kaku. Kai 4.0 mengikuti referensi Dynamic Island iPhone (kartu live activity hitam, kapsul mengambang, aksen warna sistem, gerak elastis). **Dokumen ini mengungguli aturan visual 3.0** (pil menempel tepi atas, navigasi garis putih netral, tanpa animasi idle). Fitur, batas data, privasi, worker on demand dan target memori tetap sama; yang berubah hanya bentuk, warna, gerak dan interaksi.

Referensi pemilik (tidak disalin ke repo): grid 12 live activity hitam (ride timer, activity rings, transit, kartu bank, buku, heart-rate, VR battery, UV chart, tennis score, washer), kartu saham/belanja, dan peta state Dynamic Island iPhone 14 Pro Max (lock, hotspot, AirDrop, Face ID, recording, AirPods, timer, silent/ring, Find My).

## Kai 4.0 layout refresh (27 October 2026)

Pages were rebuilt for a calmer Dynamic Island feel: header = accent dot, title, ••• menu, close (Settings moved into •••). Rows of buttons were removed; actions live in right-click and ••• menus. Fast Transform uses one drop zone with FROM/TO chips and a single Convert; Save/Clear appear only with a result. Notes has an always-visible New note field and a hover × per row. Clipboard, Notes and Shelf have a quiet two-click **Clear all** (Shelf drops references only; files stay). Hover capsule: large clock with breathing colon, weekday/date right-aligned; the Ctrl Alt Space chip was removed at the owner's request. `tools/check_appearance.py` now renders hidden and never moves the pointer. 45 unit tests pass.

## 1. Prinsip

| Prinsip | Artinya di Kai |
| --- | --- |
| Satu benda hitam yang hidup | Pil, hover, toast dan panel adalah satu kapsul yang berubah ukuran, bukan jendela berbeda. |
| Mengambang, bukan ditempel | Kapsul berjarak 8 DIP dari tepi atas di semua state, sudut membulat penuh seperti referensi. |
| Hitam murni + satu aksen | Latar `#000000`. Warna hanya untuk makna: halaman aktif, progres, status, tombol utama. |
| Gerak elastis tapi tenang | Spring sedikit underdamped (overshoot ±2–3%), lebar mendahului tinggi, isi muncul dengan fade + scale. |
| Interaktif sebelum diklik | Mata mengikuti kursor dan kapsul sedikit "tertarik" saat kursor mendekat; berkedip sesekali. |
| Hemat | Tanpa dependensi/web runtime baru. Frame hanya berjalan saat ada gerak; berhenti saat settled. |

## 2. Token

### Warna (Apple system dark)

| Token | Nilai | Pemakaian |
| --- | --- | --- |
| `surface` | `#000000` | Badan island |
| `fill-1` | `rgba(255,255,255,0.07)` | Baris list, input |
| `fill-2` | `rgba(255,255,255,0.12)` | Tombol sekunder, hover baris |
| `fill-3` | `rgba(255,255,255,0.20)` | Pressed / selected |
| `label` | `#FFFFFF` | Teks utama |
| `label-2` | `rgba(235,235,245,0.60)` ≈ `#9b9ba1` | Teks sekunder |
| `label-3` | `rgba(235,235,245,0.30)` ≈ `#5b5b60` | Teks tersier, titik nav |
| `green` | `#30D158` | Music, sukses |
| `orange` | `#FF9F0A` | Fast Transform, proses |
| `blue` | `#0A84FF` | Clipboard, link |
| `yellow` | `#FFD60A` | Notes, centang |
| `purple` | `#BF5AF2` | Shelf |
| `red` | `#FF453A` | Error |

Aksen per halaman: Transform orange · Clipboard blue · Notes yellow · Shelf purple · Music green · Settings abu-abu. Tombol utama memakai isi putih + teks hitam (seperti chip "Buy"/"Got it" di referensi), bukan aksen, agar tetap classy.

### Bentuk dan ukuran (DIP)

| State | Ukuran | Radius |
| --- | --- | --- |
| Collapsed | 72 × 24 | 12 (pil penuh) |
| Collapsed + kursor mendekat | s.d. 84 × 26 | pil penuh |
| Hover compact | 320 × 68 | 34 (pil penuh) |
| Toast / konteks | 290 × 56 | 28 |
| Panel | 540 × 280–356 | 30 |
| Jarak atas | 8 | — |

Tombol: radius 14 (pil). Input: radius 14. Baris list: radius 16. Cover: radius 14.

### Tipografi

Segoe UI Variable (terpasang). Jam compact 26 semibold; judul halaman 15 semibold; teks utama 13; sekunder 11; label kecil 9–10 dengan tracking huruf kapital.

## 3. Gerak

| Gerak | Spesifikasi |
| --- | --- |
| Buka/tutup kapsul | Buka: spring frekuensi 22, damping 0,78 (lebar). Tutup: critically damped frekuensi 26 tanpa pantulan. Tinggi memakai spring frekuensi 20, damping 0,85 sehingga lebar sedikit mendahului tinggi. Velocity dipertahankan saat arah berbalik. |
| Isi compact/toast | Opacity mengikuti progres, scale 0,92 → 1, naik 6 DIP. |
| Panel | Isi tidak lagi disembunyikan saat tinggi berubah; dipotong (mask) mengikuti badan sehingga terbuka seperti tirai. |
| Ganti halaman | Halaman baru meluncur 22 DIP dari arah navigasi, 260 ms OutCubic. |
| Indikator navigasi | Penanda berwarna aksen, 220 ms OutBack; memanjang di tengah perjalanan (efek "cair"). |
| Mata | Mengikuti kursor ±2,5 DIP, berkedip 120 ms setiap 4–9 detik (single-shot timer, bukan loop). |
| Tarikan magnet | Dalam radius 150 DIP dari zona hover, pil melebar s.d. +12 DIP. |
| Detik | Titik dua jam berdenyut tiap detik (memakai timer jam yang sudah ada). |
| Reduce motion | Semua spring snap, tanpa kedip, tanpa slide; mata tetap diam di tengah. |

## 4. State dan isi

- **Collapsed:** dua mata putih (identitas pemilik dipertahankan). Ekspresi hanya lewat arah lihat dan kedip.
- **Hover compact:** kiri jam besar; kanan hari (kapital kecil) + tanggal rata kanan. Saat ada sesi media: kartu live activity (cover, judul, artis, progres, kontrol). Tanpa logo dan tanpa chip hotkey.
- **Toast (shelf/result/error/context):** ikon lingkaran berwarna di kiri (✓ hijau, ! merah, tray ungu, ↗ biru), judul + detail, chip aksi berwarna di kanan bila bisa diklik.
- **Panel:** header (titik aksen + judul, menu •••, ×), halaman tanpa deretan tombol (aksi di klik kanan/•••, Clear all dua klik), navigasi titik + penanda aksen.
- **Music:** cover besar, progres warna dari cover, tombol play putih bulat dengan glyph hitam, lirik aktif putih tebal.
- **Notes:** lingkaran centang kuning; **Clipboard:** badge biru untuk link; **Shelf:** aksen ungu; **Transform:** pilihan format seperti segmented control putih.

## 5. Kontrak yang tidak berubah

Lima destinasi + Settings, alur Transform 4 arah/1 file, Notes sederhana, Clipboard teks/URL, Shelf intake/dedupe, media worker on demand, lirik LRCLIB, hotkey Ctrl+Alt+Space, click-through saat collapsed, tidak merebut fokus, Escape menutup, keyboard nav (Tab/Enter/←/→), tooltip/aksesibilitas. Target 50 MiB semua proses tetap belum terbukti; 4.0 tidak menambah worker, cache gambar besar, blur atau loop idle.

## 6. Penerimaan

- Unit test lulus (kontrak tepi atas 3.0 diganti: kapsul kini mengambang 8 DIP dan berujung bulat).
- Mata putih tepat di pusat ±6,5 DIP saat diam; kedip tidak terjadi dengan Reduce motion.
- Spring underdamped tetap stabil di 30/60/144 fps dan settle; default `Spring()` tetap critically damped.
- `tools/check_appearance.py` menghasilkan tangkapan baru di `artifacts/productivity`.
- Belum diukur: benchmark memori seluruh proses untuk 4.0, DPI selain 150%, rasa gerak di layar 120 Hz.
