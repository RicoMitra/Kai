"""Native hotkey and user-initiated paste. No keyboard hook or background worker."""
import ctypes as c
from ctypes import wintypes as w
import os
import sys
from PySide6.QtCore import QAbstractNativeEventFilter


class HotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self,callback):super().__init__();self.callback=callback
    def nativeEventFilter(self,event_type,message):
        if sys.platform=='win32':
            msg=w.MSG.from_address(int(message))
            if msg.message==0x312 and msg.wParam==0x4B41:
                self.callback();return True,0
        return False,0


class DesktopShortcuts:
    def __init__(self,app,callback):
        self.app=app;self.target=None;self.available=False;self.filter=HotkeyFilter(callback)
        if sys.platform!='win32':return
        self.user=c.WinDLL('user32',use_last_error=True)
        self.user.GetForegroundWindow.restype=w.HWND
        self.user.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)]
        self.user.GetClassNameW.argtypes=[w.HWND,w.LPWSTR,c.c_int]
        self.user.SetForegroundWindow.argtypes=[w.HWND]
        self.user.IsWindow.argtypes=[w.HWND]
        self.available=bool(self.user.RegisterHotKey(None,0x4B41,0x4003,0x20))
        if self.available:app.installNativeEventFilter(self.filter)

    def remember(self):
        if sys.platform!='win32':return
        handle=self.user.GetForegroundWindow();pid=w.DWORD()
        self.user.GetWindowThreadProcessId(handle,c.byref(pid))
        name=c.create_unicode_buffer(128);self.user.GetClassNameW(handle,name,128)
        if pid.value!=os.getpid() and name.value not in ('Shell_TrayWnd','Shell_SecondaryTrayWnd','Progman','WorkerW'):
            self.target=handle

    def paste(self):
        if sys.platform!='win32' or not self.target or not self.user.IsWindow(self.target):return False
        if any(self.user.GetAsyncKeyState(key)&0x8000 for key in (0x10,0x11,0x12)):return False
        if not self.restore_focus():return False
        class Keyboard(c.Structure):
            _fields_=[('vk',w.WORD),('scan',w.WORD),('flags',w.DWORD),('time',w.DWORD),('extra',c.c_size_t)]
        class Mouse(c.Structure):
            _fields_=[('x',w.LONG),('y',w.LONG),('data',w.DWORD),('flags',w.DWORD),('time',w.DWORD),('extra',c.c_size_t)]
        class Data(c.Union):_fields_=[('keyboard',Keyboard),('mouse',Mouse)]
        class Input(c.Structure):_fields_=[('kind',w.DWORD),('data',Data)]
        events=(Input*4)()
        for event,(key,flags) in zip(events,((0x11,0),(0x56,0),(0x56,2),(0x11,2))):
            event.kind=1;event.data.keyboard=Keyboard(key,0,flags,0,0)
        self.user.SendInput.argtypes=[w.UINT,c.c_void_p,c.c_int]
        return self.user.SendInput(4,events,c.sizeof(Input))==4

    def restore_focus(self):
        if sys.platform!='win32' or not self.target or not self.user.IsWindow(self.target):return False
        self.user.SetForegroundWindow(self.target)
        return self.user.GetForegroundWindow()==self.target

    def stop(self):
        if self.available:
            self.user.UnregisterHotKey(None,0x4B41);self.app.removeNativeEventFilter(self.filter);self.available=False
