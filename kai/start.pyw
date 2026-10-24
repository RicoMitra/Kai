"""GUI startup: show actionable failures without opening a console."""
import os
from pathlib import Path
import runpy
import sys
import traceback


if __name__ == '__main__':
    try:
        root = Path(__file__).resolve().parent
        sys.path.insert(0, str(root))
        runpy.run_path(str(root / 'main.py'), run_name='__main__')
    except Exception:
        folder = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'Kai' / 'logs'
        folder.mkdir(parents=True, exist_ok=True)
        log = folder / 'startup.log'
        log.write_text(traceback.format_exc(), encoding='utf-8')
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, 'Unable to open Kai. Error details were saved to:\n' + str(log), 'Kai', 0x10)
