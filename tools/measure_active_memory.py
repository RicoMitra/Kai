"""Sample the entire GUI/worker tree during owned, single-file conversions."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import zipfile
import psutil
from measure_ui_memory import Counters

ROOT=Path(__file__).resolve().parents[1]


def main():
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage,QPainter,QFont,QPdfWriter,QTextDocument
    from PySide6.QtWidgets import QApplication
    app=QApplication([])
    psapi=ctypes.WinDLL('psapi',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    with tempfile.TemporaryDirectory(prefix='kai-active-memory-') as directory:
        root=Path(directory);png=root/'sample.png';pdf=root/'sample.pdf';md=root/'sample.md';state=root/'state.json'
        image=QImage(1600,900,QImage.Format_RGB32);image.fill(Qt.white);painter=QPainter(image);painter.setPen(Qt.black);painter.setFont(QFont('Arial',40));painter.drawText(50,130,'KAI LOCAL MEMORY TEST');painter.end();image.save(str(png));del image
        writer=QPdfWriter(str(pdf));doc=QTextDocument();doc.setPlainText('KAI LOCAL PDF\nA generated single-page fixture.');doc.print_(writer);del writer,doc
        md.write_text('A small note for local memory verification.',encoding='utf-8')
        scan=root/'scan.pdf';writer=QPdfWriter(str(scan));writer.setResolution(144);painter=QPainter(writer);painter.drawImage(0,0,QImage(str(png)));painter.end();del writer
        word=root/'sample.docx'
        with zipfile.ZipFile(word,'w') as archive:
            archive.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>KAI MEMORY TEST</w:t></w:r></w:p></w:body></w:document>')
        cases=[(str(png),'pdf'),(str(pdf),'md'),(str(pdf),'docx'),(str(word),'pdf'),(str(scan),'md')]
        scenario=f'''import sys,json,time
sys.path.insert(0,{str(ROOT/'kai')!r})
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QSystemTrayIcon
from island import run_island
app=QApplication([]);cases={cases!r};index=0;started=False;outcome=[]
def island():
    return next(w for w in app.topLevelWidgets() if type(w).__name__=='Island')
def select(label):
    window=island()
    for tray in window.findChildren(QSystemTrayIcon):
        for action in tray.contextMenu().actions():
            if action.text()==label:action.trigger();window._presence.pin_until=time.monotonic()+120;return
def next_job():
    global index,started
    window=island();panel=window._deck;page=panel._built['Transform']
    if started and (page.running or 'transform' in panel._tasks):return
    if started:
        outcome.append({{'input':Path(cases[index][0]).suffix,'output':cases[index][1],'success':bool(page.outputs),'message':page.info.text()}});page.clear();index+=1;started=False
    if index==len(cases):
        Path({str(state)!r}).write_text(json.dumps(outcome));timer.stop();window.close_island();QTimer.singleShot(1500,app.quit);return
    path,target=cases[index];page.set_files([path]);page.format.button(('pdf','md','docx').index(target)).setChecked(True);page.start();started=True
def begin():
    select('Transform');timer.start()
timer=QTimer();timer.setInterval(100);timer.timeout.connect(next_job)
QTimer.singleShot(1500,lambda:select('Music'));QTimer.singleShot(4000,begin)
QTimer.singleShot(110000,app.quit)
run_island(media_on_demand=True)
'''
        environment=os.environ.copy();environment['LOCALAPPDATA']=str(root/'data');environment['PYTHONUTF8']='1'
        child=subprocess.Popen([str(Path(sys.executable).with_name('pythonw.exe')),'-B','-c',scenario],cwd=ROOT/'kai',env=environment,creationflags=subprocess.CREATE_NO_WINDOW)
        process=psutil.Process(child.pid);peaks={'private_working_set_MiB':0,'working_set_MiB':0,'private_commit_MiB':0};samples=0;seen=set();maximum_processes=0
        try:
            deadline=time.monotonic()+115
            while child.poll() is None and time.monotonic()<deadline:
                totals=dict.fromkeys(peaks,0);tree=[process,*process.children(recursive=True)];maximum_processes=max(maximum_processes,len(tree))
                for item in tree:
                    handle=kernel.OpenProcess(0x0410,False,item.pid)
                    if not handle:continue
                    try:
                        counter=Counters();counter.cb=ctypes.sizeof(counter)
                        if psapi.GetProcessMemoryInfo(handle,ctypes.byref(counter),counter.cb):
                            totals['private_working_set_MiB']+=counter.PrivateWorkingSetSize/2**20;totals['working_set_MiB']+=counter.WorkingSetSize/2**20;totals['private_commit_MiB']+=counter.PrivateUsage/2**20;seen.add(item.pid)
                    finally:kernel.CloseHandle(handle)
                for key,value in totals.items():peaks[key]=max(peaks[key],value)
                samples+=1;time.sleep(.1)
            if child.poll() is None:raise RuntimeError('Active memory scenario timed out')
            outcomes=json.loads(state.read_text());assert len(outcomes)==len(cases) and all(item['success'] for item in outcomes),outcomes
        finally:
            if child.poll() is None:
                for descendant in process.children(recursive=True):descendant.terminate()
                child.terminate()
            child.wait(timeout=5)
        report={'sampled_tree_peaks_MiB':{key:round(value,2) for key,value in peaks.items()},'under_50_private_WS_in_this_sample':peaks['private_working_set_MiB']<=50,'under_50_private_commit_in_this_sample':peaks['private_commit_MiB']<=50,'samples':samples,'sample_interval_ms':100,'max_simultaneous_processes':maximum_processes,'processes_observed':len(seen),'cases':outcomes,'limits':'Generated 1600x900 PNG, one-page text PDF and scanned PDF/OCR; actual media worker opened read-only. GUI/redirector/all descendants included, harness excluded. Sampling may miss sub-100ms peaks; not a hard cap, arbitrary-input guarantee, soak or compositor cost. No working-set trimming.'}
        out=ROOT/'artifacts/island/memory-active-verification.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
