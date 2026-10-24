"""Read-only check: native services live in a disposable process, never voice."""
import json
import multiprocessing
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'kai'))


def main():
    from desktop_worker import DesktopServices
    before = {process.pid for process in multiprocessing.active_children()}
    desktop = DesktopServices()
    try:
        desktop.start()
        deadline = time.monotonic() + 4
        while not desktop.audio.snapshot and time.monotonic() < deadline:
            time.sleep(0.1)
        report = {'audio_read_available': bool(desktop.audio.snapshot),
                  'native_modules_absent_in_parent': not any(name in sys.modules for name in ('native', 'winsdk', 'pycaw', 'comtypes')),
                  'voice_modules_absent_in_parent': not any(name in sys.modules for name in ('stt', 'faster_whisper', 'sounddevice', 'keyboard'))}
    finally:
        desktop.stop()
    report['worker_reaped'] = desktop.process is None and {process.pid for process in multiprocessing.active_children()} == before
    assert all(report.values()), report
    output = ROOT / 'artifacts/island/desktop-worker-verification.json'
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
