"""Regenerate the GitHub README from its editable Markdown source."""
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    source=(ROOT/'docs/readme-source.md').read_text(encoding='utf-8')
    if not source.startswith('# Kai') or len(source)<5000:raise SystemExit('Incomplete README source')
    target=ROOT/'README.md'
    if args.check:
        if target.read_text(encoding='utf-8')!=source:raise SystemExit('README is out of date; run tools/build_readme.py')
    else:target.write_text(source,encoding='utf-8')
    print(f'README: {len(source.splitlines())} lines; '+('in sync' if args.check else 'generated'))


if __name__=='__main__':main()
