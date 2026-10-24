"""Gracefully restart only this project's Kai window, preserving notes and settings."""
import ctypes as c
from ctypes import wintypes as w
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kai'))
from storage import data_dir


def main():
    entry=str(ROOT/'kai/start.pyw').casefold();allowed={}
    for process in psutil.process_iter(['pid','name','cmdline']):
        try:
            if process.info['name'].lower()=='pythonw.exe' and any(arg.casefold()==entry for arg in (process.info['cmdline'] or [])):allowed[process.pid]=process
        except (psutil.AccessDenied,psutil.NoSuchProcess):pass
    user=c.WinDLL('user32',use_last_error=True)
    user.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,c.c_int]
    user.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)]
    user.PostThreadMessageW.argtypes=[w.DWORD,w.UINT,w.WPARAM,w.LPARAM]
    callback=c.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM);threads=[];targets=[]
    @callback
    def inspect(handle,unused):
        title=c.create_unicode_buffer(128);user.GetWindowTextW(handle,title,128)
        if title.value=='Kai Island':
            pid=w.DWORD();thread=user.GetWindowThreadProcessId(handle,c.byref(pid))
            if pid.value in allowed:threads.append(thread);targets.append(allowed[pid.value])
        return True
    user.EnumWindows.argtypes=[callback,w.LPARAM];user.EnumWindows(inspect,0)
    for thread in threads:
        if not user.PostThreadMessageW(thread,0x12,0,0):raise c.WinError(c.get_last_error())
    _,alive=psutil.wait_procs(targets,timeout=8)
    if alive:raise RuntimeError('Kai belum selesai menutup; peluncuran baru dibatalkan agar data tetap aman')
    launched=time.time();subprocess.run([str(ROOT/'Kai.exe'),'--check'],check=True)
    subprocess.Popen([str(ROOT/'Kai.exe')],cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
    log=data_dir()/'logs/session.json'
    for _ in range(50):
        if log.exists() and log.stat().st_mtime>=launched-1:
            state=json.loads(log.read_text(encoding='utf-8'))
            if psutil.pid_exists(state['pid']):print(json.dumps(state,indent=2));return
        time.sleep(.1)
    raise RuntimeError('Versi baru belum mencatat sesi; periksa logs/startup.log')


if __name__=='__main__':main()
