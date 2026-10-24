"""Inventaris metadata skill lokal; tidak menjalankan atau memasang skill."""
from pathlib import Path
from collections import Counter
import re

PROJECT = Path(__file__).resolve().parents[1]
HOME_DIR = Path.home()
ROOTS = [HOME_DIR / p for p in (
    '.codex/skills', '.agents/skills', '.codex/plugins/cache',
    '.claude/skills', '.gemini/skills', '.copilot/skills', '.config/opencode/skills',
)] + [PROJECT / '.agents/skills', PROJECT / '.codex/skills']


def metadata(path):
    body = path.read_text(encoding='utf-8-sig', errors='replace')
    front = body.split('---', 2)[1] if body.startswith('---') else ''
    name = re.search(r'^name:\s*(.+)$', front, re.M)
    desc = re.search(r'^description:\s*(.*)(?:\n|$)', front, re.M)
    name = name.group(1).strip().strip('\"\'') if name else path.parent.name
    description = desc.group(1).strip() if desc else ''
    if description in ('>', '|', '>-', '|-', '') and desc:
        following = front[desc.end():].splitlines()
        values = []
        for line in following:
            if line and not line[0].isspace():
                break
            values.append(line.strip())
        description = ' '.join(values).strip()
    return name, description.strip('\"\'')


def main():
    paths, errors = set(), []
    for root in ROOTS:
        if root.is_dir():
            try:
                paths.update(p.resolve() for p in root.rglob('SKILL.md') if p.is_file())
            except OSError as exc:
                errors.append(f'{root}: {exc}')
    rows = []
    for path in sorted(paths, key=lambda p: str(p).casefold()):
        try:
            name, description = metadata(path)
            rows.append((name, description, path))
        except OSError as exc:
            errors.append(f'{path}: {exc}')
    counts = Counter(name.casefold() for name, _, _ in rows)
    lines = ['# Inventaris skill lokal', '',
             'Inventaris metadata untuk pemilihan skill Kai. Membaca nama dan deskripsi, bukan audit penuh seluruh instruksi atau sertifikasi kualitas. Skill terpilih dibaca lengkap sebelum diterapkan.', '',
             f'Ditemukan **{len(rows)} berkas SKILL.md**, **{len(counts)} nama unik**; **{sum(n > 1 for n in counts.values())} nama** memiliki lebih dari satu lokasi/versi.', '',
             '## Cakupan pencarian', '']
    lines += [f'- `{root}` — ' + ('ada' if root.is_dir() else 'tidak ditemukan') for root in ROOTS]
    lines += ['', 'Pencarian terbatas pada direktori skill konvensional di atas; tidak memindai seluruh drive, seluruh akun Windows, atau isi repository lain. Nama sama tidak otomatis berarti isi identik. Tidak menghapus duplikat atau memasang/memperbarui skill.', '',
              'Ulangi dari root proyek: `python tools/inventory_skills.py`. Tanggal pemeriksaan awal: 22 Oktober 2026.', '',
              '## Semua entri', '', '| Skill | Deskripsi metadata | Lokasi |', '| --- | --- | --- |']
    for name, description, path in sorted(rows, key=lambda r: (r[0].casefold(), str(r[2]))):
        clean = lambda value: value.replace('|', '\\|').replace('\n', ' ')
        lines.append(f'| {clean(name)} | {clean(description)} | `{path.as_posix()}` |')
    lines += ['', '## Kesalahan baca', ''] + (errors or ['Tidak ada kesalahan baca yang dilaporkan.'])
    target = PROJECT / 'docs/10-inventaris-skill-lokal.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{len(rows)} files; {len(counts)} unique names; {len(errors)} read errors; output: docs/10-inventaris-skill-lokal.md')


if __name__ == '__main__':
    main()
