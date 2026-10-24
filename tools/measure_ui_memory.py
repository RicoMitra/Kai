"""Measure a fresh real Kai demo process through Windows PSAPI, without trimming RAM."""
import ctypes
import argparse
from ctypes import wintypes
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
import os
import tempfile
import psutil

ROOT = Path(__file__).resolve().parents[1]


class Counters(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in (
            'PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
            'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage',
            'PagefileUsage', 'PeakPagefileUsage', 'PrivateUsage', 'PrivateWorkingSetSize',
        )] + [('SharedCommitUsage', ctypes.c_uint64)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('demo', 'core', 'demand'), default='core')
    parser.add_argument('--panel-cycle', action='store_true', help='open/close Media before sampling demand idle recovery')
    args = parser.parse_args()
    if args.panel_cycle and args.mode != 'demand':
        parser.error('--panel-cycle requires --mode demand')
    if sys.platform != 'win32':
        raise SystemExit('Windows required')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    flags = {'demo': ['--demo'], 'core': [], 'demand': ['--media-on-demand']}[args.mode]
    gui_python = str(Path(sys.executable).with_name('pythonw.exe'))
    command = [gui_python, '-B', 'main.py', '--island', *flags]
    warmup = 3
    cycle_path = ROOT / 'artifacts/island/panel-cycle-verification.json'
    if args.panel_cycle:
        cycle_path.parent.mkdir(parents=True, exist_ok=True)
        cycle_path.unlink(missing_ok=True)
        scenario = f'''import sys
sys.path.insert(0, {str(ROOT / 'kai')!r})
import json, multiprocessing, time
from pathlib import Path
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import QTimer
from island import run_island
app = QApplication([])
state = {{'opened': False, 'closed': False, 'worker_seen': False, 'worker_reaped': False}}
def record_open():
    state['opened'] = any(type(widget).__name__ == 'ControlPanel' for widget in app.allWidgets())
    state['worker_seen'] = bool(multiprocessing.active_children())
def record_closed():
    state['worker_reaped'] = not multiprocessing.active_children()
    Path({str(cycle_path)!r}).write_text(json.dumps(state, indent=2), encoding='utf-8')
def select_page(page):
    for widget in app.topLevelWidgets():
        for tray in widget.findChildren(QSystemTrayIcon):
            for action in tray.contextMenu().actions():
                if action.text()=={{'Media':'Music','Atur':'Settings'}}.get(page,page):
                    action.trigger()
                    state.setdefault('pages_visited',[]).append(page)
                    if type(widget).__name__=='Island':widget._presence.pin_until=time.monotonic()+20
                    return

def close_panel():
    for widget in app.topLevelWidgets():
        if type(widget).__name__=='Island' and widget._deck_open:
            widget.collapse_deck();state['closed']=True
QTimer.singleShot(1500,lambda:select_page('Media'))
QTimer.singleShot(3000,record_open)
QTimer.singleShot(4000,lambda:select_page('Clipboard'))
QTimer.singleShot(5000,lambda:select_page('Notes'))
QTimer.singleShot(6000,lambda:select_page('Shelf'))
QTimer.singleShot(7000,lambda:select_page('Transform'))
QTimer.singleShot(10500,lambda:select_page('Atur'))
QTimer.singleShot(12000,close_panel)
QTimer.singleShot(14500,record_closed)
run_island(media_on_demand=True)
'''
        command = [gui_python, '-B', '-c', scenario]
        warmup = 16
    measurement_data = tempfile.TemporaryDirectory(prefix='kai-memory-')
    child_environment = os.environ.copy(); child_environment['LOCALAPPDATA'] = measurement_data.name
    child = subprocess.Popen(command,
                             cwd=ROOT / 'kai', env=child_environment, creationflags=subprocess.CREATE_NO_WINDOW)
    parent = psutil.Process(child.pid)
    measured_pids = set()
    try:
        time.sleep(warmup)
        if args.panel_cycle:
            cycle = json.loads(cycle_path.read_text(encoding='utf-8'))
            if not all(cycle.values()) or set(cycle.get('pages_visited',[]))!={'Media','Clipboard','Notes','Shelf','Transform','Atur'}:
                raise RuntimeError(f'Panel cycle not verified: {cycle}')
        samples = []
        process_details = {}
        for _ in range(10):
            if child.poll() is not None:
                raise RuntimeError('Kai exited during measurement')
            totals = dict.fromkeys(('working_set_MiB', 'private_working_set_MiB', 'private_commit_MiB'), 0)
            for process in [parent, *parent.children(recursive=True)]:
                handle = kernel.OpenProcess(0x0410, False, process.pid)
                if not handle:
                    raise ctypes.WinError(ctypes.get_last_error())
                try:
                    measured_pids.add(process.pid)
                    counters = Counters()
                    counters.cb = ctypes.sizeof(counters)
                    if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                        raise ctypes.WinError(ctypes.get_last_error())
                    totals['working_set_MiB'] += counters.WorkingSetSize / 2**20
                    totals['private_working_set_MiB'] += counters.PrivateWorkingSetSize / 2**20
                    totals['private_commit_MiB'] += counters.PrivateUsage / 2**20
                    process_details[process.pid]={'name':process.name(),'private_working_set_MiB':round(counters.PrivateWorkingSetSize/2**20,2)}
                finally:
                    kernel.CloseHandle(handle)
            samples.append(totals)
            time.sleep(1)
        report = {'mode': args.mode,
                  'warmup_seconds': warmup, 'panel_cycle': args.panel_cycle, 'samples': 10, 'interval_seconds': 1,
                  'metrics': {key: {
                      'min': round(min(s[key] for s in samples), 2),
                      'median': round(statistics.median(s[key] for s in samples), 2),
                      'max': round(max(s[key] for s in samples), 2),
                  } for key in samples[0]},
                  'raw_samples': samples,
                  'process_count': len(measured_pids),
                  'processes':list(process_details.values()),
                  'launch':'pythonw GUI, same runtime as Kai.exe; temporary local user data',
                  'limits': 'Sum of launcher and all descendants (working set may count shared pages twice). Short idle run; excludes DWM/system allocations, other apps and speech models. No memory trimming.'}
        label = args.mode + ('-after-panel' if args.panel_cycle else '')
        out = ROOT / ('artifacts/island/memory-ui.json' if args.mode == 'demo' else f'artifacts/island/memory-{label}.json')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in report.items() if k != 'raw_samples'}, indent=2))
    finally:
        descendants = parent.children(recursive=True)
        for process in reversed(descendants):
            try:
                process.terminate()
            except psutil.NoSuchProcess:
                pass
        child.terminate()  # Only this script's isolated demo process.
        child.wait(timeout=5)
        _, alive = psutil.wait_procs(descendants, timeout=5)
        for process in alive: process.kill()
        psutil.wait_procs(alive, timeout=3)
        measurement_data.cleanup()


if __name__ == '__main__':
    main()
