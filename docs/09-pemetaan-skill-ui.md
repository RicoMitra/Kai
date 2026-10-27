# Pemilihan skill untuk Kai

Pengguna meminta gpt-taste, emil-design-eng, ponytail serta pemeriksaan skill lokal lainnya. Inventaris metadata ada di [10](10-inventaris-skill-lokal.md). Tidak semua skill perlu dijalankan; pilih berdasarkan keluaran milestone, baca instruksi lengkap sebelum menerapkan, dan patuhi kebutuhan Kai serta instruksi pengguna terbaru.

## Skill yang sudah dibaca dan diterapkan dalam perencanaan

| Skill | Peran di Kai | Penerapan konkret |
| --- | --- | --- |
| ponytail (`%USERPROFILE%/.agents/skills/ponytail/SKILL.md`) | Menjaga solusi minimum, mode full sesuai permintaan | Pakai kode/parser yang ada; stdlib SQLite; satu proses; tanpa abstraksi/IPC spekulatif |
| emil-design-eng (`%USERPROFILE%/.codex/skills/emil-design-eng/SKILL.md`) | Respons cepat dan motion beralasan | Feedback segera; animasi pendek/dapat dibalik; tidak menunda shortcut; reduced motion |
| apple-design (`%USERPROFILE%/.codex/skills/apple-design/SKILL.md`) | Kontinuitas bentuk, material, tipografi | Anchor atas tengah, nilai animasi dari keadaan layar saat ini, teks terbaca di kaca |
| gpt-taste (`%USERPROFILE%/.codex/skills/gpt-tasteskill/SKILL.md`) | Komposisi dan kontras | Hierarki ringkas, tombol terbaca, susunan panel terukur; hindari layout generik |
| brainstorming (`%USERPROFILE%/.codex/skills/brainstorming/SKILL.md`) | Memahami kebutuhan dan membandingkan arah desain | Pilihan arah A/B/C dan pertanyaan bertahap sebelum implementasi |
| projectstep (`%USERPROFILE%/.codex/skills/projectstep/SKILL.md`) | Konteks lintas sesi | AGENTS, sumber data, akses, keputusan, workflow dan bukti |
| verification-before-completion (`%USERPROFILE%/.codex/skills/verification-before-completion/SKILL.md`) | Klaim sesuai hasil nyata | 98/98 hanya untuk parser; UI/runtime tetap belum diuji |

`using-superpowers` dibaca sebagai panduan pemakaian skill. `end-with-script` dipertimbangkan untuk pemeliharaan artefak: Markdown adalah sumber native yang bisa diedit langsung; inventaris berulang disertai script. `find-skills` dibaca untuk discovery; pencarian marketplace/instalasi tidak diperlukan karena pengguna meminta skill yang sudah lokal.

## Penyesuaian konflik ke aplikasi desktop

| Aturan pada skill | Adaptasi Kai | Alasan |
| --- | --- | --- |
| gpt-taste: hero/AIDA, typography marketing, random layout, GSAP ScrollTrigger | Tidak diterapkan pada island; mungkin relevan bila kelak membuat halaman portofolio | Kai adalah overlay desktop tanpa hero, footer, atau scroll pemasaran |
| gpt-taste: semua UI harus penuh motion | Motion hanya untuk perubahan yang membantu orientasi/status | Island dipakai berulang dan harus hemat resource |
| gpt-taste: font web tertentu dan larangan font lain | Gunakan font sistem Windows yang tersedia | Konsistensi native, tanpa unduhan font wajib |
| Emil: jangan animasikan aksi keyboard | Shortcut/indikator langsung; morph wadah tidak menghalangi aksi | Memenuhi feedback PTT sekaligus perilaku island dari sumber |
| Apple/Emil: CSS, transform, spring library web | Gunakan fasilitas Qt dan ukur frame time; jangan menganggap rendering Qt sama dengan browser | Stack PySide6 tetap baseline |
| Ponytail: sedikit berkas dan fitur | Pertahankan seluruh kebutuhan; implementasi bertahap dan sedikit modul | Pengguna meminta beberapa MD dan keseluruhan ide tetap terakomodasi |

Jangan memalsukan eksekusi RNG atau hasil benchmark demi checklist skill. Instruksi spesifik web tidak mengubah produk menjadi website. Untuk review UI memakai Emil, laporan perubahan memakai tabel Before/After/Why sesuai skill.

## Kandidat relevan dari inventaris, dibaca saat dibutuhkan

| Skill | Saat digunakan | Batas pemakaian |
| --- | --- | --- |
| anti-ai-slop-engineering | Review arsitektur/implementasi | Cegah abstraksi spekulatif dan fallback palsu |
| ui-ux-pro-max | Audit kontras, hierarchy, target kontrol | Ambil prinsip aksesibilitas; jangan memaksa stack web |
| impeccable | Audit keterbacaan/state/error/aksesibilitas | Pilih satu audit terarah, tidak tumpuk semua proses desain |
| review-animations / improve-animations | Setelah animasi Qt benar-benar ada | Evaluasi retarget, timing, frame time dan beban |
| systematic-debugging | Saat bug nyata mulai diperbaiki | Reproduksi dan akar sebab sebelum perubahan |
| test-driven-development | Logika state/penjadwal/parser baru | Tes perilaku yang bermakna sesuai instruksi yang berlaku |
| ponytail-review | Setelah perubahan cukup besar | Cari yang dapat dihapus; jangan mengurangi kebutuhan pengguna |
| imagegen / brandkit | Jika karakter/avatar atau identitas visual diminta | Bukan prasyarat demo teks/ikon |
| screenshot / computer-use | Verifikasi UI Windows bila tool tersedia | Gunakan kemampuan yang tersedia; jangan klaim observasi UI tanpa bukti |
| hyperframes / pr-to-video / ffmpeg | Saat demo video portofolio diminta | Tidak memasukkan pipeline video ke runtime Kai |

Skill design lain (taste frontend, frontend-god-mode, high-end-visual-design, hallmark, minimalist, brutalist, mobile/web imagegen) tersedia tetapi tidak dipakai serentak. Sebagian fokus website atau gaya yang berbeda dari liquid glass; pilih jika tugas spesifik membutuhkannya. Skill wiki, akademik, WordPress, spreadsheet dan slide tidak diperlukan untuk membangun inti Kai.

## Urutan kerja skill yang sederhana

Pahami kebutuhan → gunakan ponytail untuk menentukan perubahan minimum → rancang state/material dengan Apple/Emil dan prinsip gpt-taste yang relevan → implementasikan milestone → debug jika ada kegagalan → verifikasi → perbarui dokumentasi. Tidak menambah agen paralel atau tool baru semata karena skill tersedia.

## Latest applied skills

23 October: apple-design applied to anchored/reversible spring motion and native system typography; UI/UX Pro Max explicitly requested and its --design-system search executed. Adopt grouping, keyboard/focus/pressed states, contrast and reduced motion. Reject generated landing-page/AIDA, bright blue palette, remote fonts and web stack for this approved black Qt overlay. Desktop pointer targets remain compact rather than imposing phone-sized controls everywhere. See 18 and appearance-verification.json for implementation evidence.
