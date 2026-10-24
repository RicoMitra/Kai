"""Package source and GUI launcher, never user data or the Python runtime."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    files = [ROOT / name for name in ('README.md', 'handoff.md', 'AGENTS.md', 'Kai.cmd', 'Kai Hemat.cmd', 'Kai Preview.cmd', 'Setup Kai.cmd', 'THIRD_PARTY_NOTICES.md', 'kai-dynamic-island.md')]
    files += sorted((ROOT / 'kai').glob('*.py'))
    files += sorted((ROOT / 'kai').glob('*.pyw'))
    files += [ROOT / 'Kai.exe']
    files += sorted((ROOT / 'assets').glob('*.png'))
    files += sorted((ROOT / 'assets').glob('*.ico'))
    files += [ROOT / 'kai/requirements.txt', ROOT / 'kai/README.md']
    files += sorted((ROOT / 'docs').rglob('*.md'))
    files += sorted((ROOT / 'docs/references').glob('*.png'))
    files += sorted((ROOT / 'docs/references').glob('*.jpg'))
    files += sorted((ROOT / 'tools').glob('*.py'))
    files += sorted((ROOT / 'tools').glob('*.cs'))
    files += sorted((ROOT / 'artifacts/redesign').glob('*verification.json'))
    files += sorted((ROOT / 'artifacts/productivity').glob('*verification.json'))
    files += sorted((ROOT / 'artifacts/island').glob('*verification.json'))
    files += sorted((ROOT / 'artifacts/island').glob('memory-demand*.json'))
    files += [ROOT / 'artifacts/island/memory-core.json']
    files = sorted(set(files))
    manifest = {str(path.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    out = ROOT / 'dist/Kai-v3-productivity.zip'
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, 'Kai/' + path.relative_to(ROOT).as_posix())
        archive.writestr('Kai/MANIFEST.sha256.json', json.dumps(manifest, indent=2))
    with zipfile.ZipFile(out) as archive:
        assert archive.testzip() is None
        forbidden = ('__pycache__', '.venv/', '/runtime/', 'spotify-token', 'settings.json', '.sqlite3', '/models/')
        assert not any(word in name for name in archive.namelist() for word in forbidden)
        for name, digest in manifest.items():
            assert hashlib.sha256(archive.read('Kai/' + name)).hexdigest() == digest
    print(json.dumps({'file': str(out), 'files': len(files), 'bytes': out.stat().st_size,
                      'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'verified': True}, indent=2))


if __name__ == '__main__':
    main()
