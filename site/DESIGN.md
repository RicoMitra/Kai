# Kai download site — design reference

Patokan visual dan konten untuk website download Kai (`site/`). Disusun 28 Oktober 2026 dari tiga referensi pemilik:

1. **Halaman download Claude** — struktur: hero terpusat dengan judul serif besar, satu kalimat, tombol download utama putih + tombol sekunder bergaris; lalu bagian "Get started" dengan kartu berisi baris platform + tombol Download di kanan.
2. **Hero Sentry** — hitam ke biru: badge kecil bergaris di atas judul (`SOC 2 …`, `STATUS: ● MONITORING`), judul dua baris (baris pertama abu-abu, kedua putih), tombol biru bergradien dengan panah, bidang isometrik bergaris tipis dan cahaya biru dari kanan bawah, baris "Trusted by" bernada redup.
3. **Luminai** — biru elektrik di atas navy, kata kunci miring berwarna biru di judul, kartu UI kaca gelap dengan label kapital kecil, angka besar sebagai bukti (10x, 65%).

Tujuan: orang paham Kai dalam lima detik dan bisa download dalam satu klik, dengan rasa elegan dan classy, bukan ramai.

## Prinsip

| Prinsip | Penerapan |
| --- | --- |
| Satu aksi utama | "Download for Windows" selalu terlihat: hero, nav, dan bagian Get started. |
| Jujur | Kai bukan installer mandiri: perlu Windows 10/11 64-bit dan Python 3.12. Ditulis jelas di dekat tombol. |
| Tenang | Hitam + satu biru. Warna aksen Kai (oranye, biru, kuning, ungu, hijau) hanya sebagai titik kecil per fitur. |
| Produk sebagai bintang | Island animasi di hero dan screenshot asli di fitur. Tanpa ilustrasi stok. |
| Ringan | HTML/CSS/JS statis, tanpa framework/build. Deploy gratis di Vercel. |

## Token

| Token | Nilai |
| --- | --- |
| `--bg` | `#05070d` (hitam kebiruan) |
| `--surface` | `rgba(255,255,255,.04)` dengan border `rgba(255,255,255,.09)` |
| `--text` / `--muted` / `--faint` | `#f5f7fb` / `#9aa3b5` / `#5d6577` |
| `--blue` | `#3d6bff` → `#7aa2ff` (gradien tombol dan cahaya) |
| Aksen fitur | Transform `#ff9f0a`, Clipboard `#0a84ff`, Notes `#ffd60a`, Shelf `#bf5af2`, Music `#30d158` |
| Font judul | Instrument Serif (Google Fonts), fallback Georgia |
| Font teks | Inter (Google Fonts), fallback Segoe UI |
| Radius | Tombol 12, kartu 24, badge 6 |
| Lebar konten | 1160 px, gutter 20 px di mobile |

## Struktur halaman

1. **Nav** — logo bulat + "Kai", tautan Features · Get started · Privacy · FAQ · GitHub, tombol putih "Download".
2. **Hero** (Sentry + Claude) — badge `v4.0 · WINDOWS 10/11` dan `STATUS: ● OPEN SOURCE`; judul serif "Your desktop, / *one island* away." (baris pertama redup, kata kunci miring biru ala Luminai); kalimat singkat; tombol "Download for Windows" + "View on GitHub"; catatan kecil kebutuhan. Di kanan: island hitam yang berganti state (pil → jam → musik → notifikasi) di atas bidang isometrik bergaris dan cahaya biru.
3. **Built with** — baris redup: Python · PySide6 · SQLite · Windows SMTC · Core Audio.
4. **Fitur** — lima kartu kaca gelap, masing-masing titik aksen, judul, satu kalimat, dan screenshot asli Kai.
5. **Angka** (Luminai) — 0 cloud upload · 5 tools · 1 click to open.
6. **Get started** (Claude) — kiri judul serif; kartu "Desktop" dengan baris Windows x64 / Source code / Requirements dan tombol di kanan; kartu "Setup in 3 steps".
7. **Privacy** — local-first: data di `%LOCALAPPDATA%\Kai`, tanpa telemetri, lirik dan Spotify opsional.
8. **FAQ** — `<details>` native.
9. **Footer** — dibuat oleh RicoMitra, tautan GitHub, catatan lisensi.

## Gerak

Island hero: transisi lebar/tinggi/radius `cubic-bezier(.34,1.4,.5,1)` (sedikit memantul) 600 ms, isi fade 250 ms, ganti state tiap 3,2 s. Elemen masuk saat scroll: fade + naik 16 px. `prefers-reduced-motion` mematikan semua animasi dan island diam di state jam.

## Download

Tombol utama mengarah ke ZIP source dari GitHub (`https://github.com/RicoMitra/Kai/archive/refs/heads/main.zip`), gratis tanpa hosting file. Bila nanti ada GitHub Release, cukup ganti konstanta `DOWNLOAD_URL` di `index.html`.

## Deploy (Vercel Hobby, gratis)

Import repo `RicoMitra/Kai` di Vercel → **Root Directory: `site`** → Framework: Other → tanpa build command → Deploy. Tidak perlu environment variable.
