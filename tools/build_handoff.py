"""Generate the handoff with complete Markdown coverage and a project-file inventory."""
import argparse
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/handoff-source.md'
OUTPUT=ROOT/'handoff.md'


def build():
    content=SOURCE.read_text(encoding='utf-8').rstrip()+'\n'
    files=sorted(path for path in ROOT.rglob('*') if path.is_file() and not any(part in ('__pycache__','.git','.venv','venv','runtime') for part in path.relative_to(ROOT).parts))
    markdown=[path for path in files if path.suffix.lower()=='.md' and path!=OUTPUT]
    missing=[path.relative_to(ROOT).as_posix() for path in markdown if path.relative_to(ROOT).as_posix() not in content]
    if missing:raise ValueError('MD belum dijelaskan: '+', '.join(missing))
    appendix=['','## Lampiran A. Inventaris seluruh MD dan heading','',
              f'{len(markdown)} MD sumber/pendukung + handoff.md keluaran. Daftar berikut dibaca dari berkas sebenarnya; heading arsip tetap dicantumkan.','']
    for path in markdown:
        relative=path.relative_to(ROOT).as_posix();text=path.read_text(encoding='utf-8-sig')
        appendix.extend([f'### [{relative}]({relative})',''])
        fenced=False
        for line in text.splitlines():
            if line.startswith('```'):fenced=not fenced
            if not fenced and re.match(r'^#{1,6} ',line):appendix.append('- '+line.lstrip('#').strip())
        appendix.append('')
    appendix.extend(['## Lampiran B. Letak setiap file proyek','',
                     'Inventaris source, aset, dokumen, arsip, paket dan bukti yang ada saat build; mengecualikan runtime, .git, venv dan pycache. Data pengguna berada di luar pohon ini.','', '```text'])
    appendix.extend(path.relative_to(ROOT).as_posix() for path in files if path!=OUTPUT)
    appendix.extend(['handoff.md','```',''])
    return content+'\n'.join(appendix)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    expected=build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8')!=expected:raise SystemExit('handoff.md belum sinkron; jalankan build_handoff.py')
    else:OUTPUT.write_text(expected,encoding='utf-8')
    assert len(expected)>1000 and 'docs/17-revisi-shelf-notes-dan-context.md' in expected
    print(f'{OUTPUT.name}: {len(expected.splitlines())} baris; cakupan MD lengkap; '+('sinkron' if args.check else 'dibuat'))


if __name__=='__main__':main()
