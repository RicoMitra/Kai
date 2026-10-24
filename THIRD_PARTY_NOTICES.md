# Dependensi dan lisensi

## HTTP/TLS security pins — 24 October 2026

The active requirements now also pin requests 2.33.0 (Apache-2.0), urllib3 2.8.0 (MIT), idna 3.15 (BSD-3-Clause), and certifi 2026.10.19 (MPL-2.0), verified against their version-specific PyPI metadata. These replace older inherited HTTP/TLS dependencies in Kai's own virtual environment. The 26-package active Python closure was re-audited; see docs/19-github-and-privacy.md and artifacts/productivity/dependency-audit-verification.json. This is not a native-library or full legal compliance audit. Development scanners are not shipped as application dependencies.

Fast Transform memakai QtGui/QPdfWriter dan QtPdf dari instalasi PySide6 yang sama, ZIP/XML stdlib untuk DOCX, serta API OCR Windows melalui winsdk yang sudah ada. Tidak menambah PyMuPDF/python-docx/LibreOffice/Word COM sebagai dependensi. QtPdf membawa komponen PDFium/transitif sesuai distribusi Qt; jika kelak membundel biner, notice Qt/PDFium juga perlu disertakan. Tidak ada model OCR baru diunduh.

Paket suara (faster-whisper, ctranslate2, av, sounddevice dan numpy) kini nonaktif dan tidak ada dalam requirements desktop; barisnya dipertahankan untuk jejak inspeksi runtime sebelumnya. Versi berikut diperiksa dari metadata distribusi yang terpasang pada 22 Oktober 2026. Paket source Kai tidak menyertakan runtime Python, Qt, DLL, model, atau dependensi biner; Setup mengambil paket melalui pip. Lisensi Kai sendiri belum ditentukan pemilik. Referensi gambar adalah materi pengguna, bukan aset pihak ketiga yang diunduh untuk didistribusikan bebas.

| Paket | Versi diuji | Lisensi metadata |
| --- | --- | --- |
| PySide6 | 6.10.1 | LGPL-3.0-only / GPL-2.0-only / GPL-3.0-only |
| faster-whisper | 1.2.1 | MIT |
| ctranslate2 | 4.8.3 | MIT |
| av | 19.0.2 | BSD-3-Clause; pustaka codec memiliki notice tersendiri |
| sounddevice | 0.5.6 | MIT; PortAudio memiliki notice tersendiri |
| numpy | 1.26.4 | BSD dan notice pustaka bawaan dalam metadata distribusi |
| keyboard | 0.13.5 | MIT |
| rapidfuzz | 3.14.6 | MIT |
| spotipy | 2.25.1 | MIT |
| pycaw | 20260927 | MIT |
| comtypes | 1.4.17 | MIT |
| winsdk | 1.0.0b10 | MIT |
| psutil | 6.0.0 | BSD-3-Clause |
| icalendar | 7.3.0 | BSD-2-Clause |
| recurring-ical-events | 3.8.2 | LGPL-3.0-or-later |

Pakai distribusi Qt open source tanpa biaya lisensi komersial. Jika kelak membuat installer/bundel biner, sertakan notice/teks lisensi dependensi dan penuhi kewajiban distribusinya; source ZIP ini belum merupakan bundel tersebut. Metadata bukan audit hukum seluruh dependensi transitif.

Cuaca menampilkan atribusi Open-Meteo; lirik diambil dari LRCLIB hanya atas permintaan. Spotify memakai layanan resmi dan akun pengguna. Library UI web yang diminta dipakai sebagai referensi prinsip gerak/desain; tidak ada komponen React/GSAP atau kode berlisensi lain yang disalin ke runtime Qt.

## Launcher, material dan identitas

Kai.exe adalah launcher GUI buatan proyek, dikompilasi dengan compiler .NET Framework Windows; Python/Qt tetap runtime terpisah yang tidak dibundel. tools/KaiLauncher.cs adalah sumber yang bisa dibangun ulang. kai/glass.py memakai ABI Windows.UI.Composition/Direct2D Microsoft melalui ctypes; tidak membundel DLL pihak ketiga. Referensi ABI primer: microsoft/windows-rs 0.58.0 dan dokumentasi Microsoft. Tidak memakai kode Qt frameless GPL yang sempat diperiksa sebagai referensi. Logo PNG diberikan pengguna dan hanya dikonversi ke ukuran ikon; hak logo sumber tetap pemiliknya. Animmaster/Skiper/Unlumen dipakai sebagai referensi visual; tidak menyalin komponen berbayar.
