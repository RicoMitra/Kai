# Kode Kai

Panduan aktif: [README root](../README.md) dan [panduan pakai](../docs/14-panduan-pakai.md). Launcher menggunakan runtime di LOCALAPPDATA.

`main.py` atau `main.py --island` memulai desktop tanpa suara, dengan media/audio on demand secara default. `--media-on-demand` memaksanya; `--demo` pratinjau tanpa layanan asli. `--text` mempertahankan perintah teks dan `--dry` hanya parse.

`stt.py` dan `speech_worker.py` adalah kode suara nonaktif yang dipertahankan dari implementasi sebelumnya. Entry point/panel tidak menggunakannya dan requirements aktif tidak memasang paket model/audio. Jangan menyalakan kembali tanpa permintaan pengguna.
