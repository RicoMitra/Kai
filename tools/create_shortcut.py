"""Create the desktop shortcut with Unicode shell APIs (including Japanese paths)."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import uuid


class GUID(c.Structure):
    _fields_=[('data',c.c_ubyte*16)]


def guid(value):
    return GUID((c.c_ubyte*16).from_buffer_copy(uuid.UUID(value).bytes_le))


def call(pointer,index,types,*args):
    table=c.cast(pointer,c.POINTER(c.POINTER(c.c_void_p))).contents
    result=c.WINFUNCTYPE(c.c_long,c.c_void_p,*types)(table[index])(pointer,*args)
    if result<0: raise OSError(f'Shell HRESULT {result:#x}')


def main():
    root=Path(__file__).resolve().parents[1]
    ole=c.OleDLL('ole32');ole.CoInitialize(None)
    link=c.c_void_p();persist=c.c_void_p()
    cls=guid('00021401-0000-0000-c000-000000000046')
    iid=guid('000214f9-0000-0000-c000-000000000046')
    ole.CoCreateInstance(c.byref(cls),None,1,c.byref(iid),c.byref(link))
    try:
        call(link,20,[w.LPCWSTR],str(root/'Kai.exe'))
        call(link,9,[w.LPCWSTR],str(root))
        call(link,17,[w.LPCWSTR,c.c_int],str(root/'assets/kai.ico'),0)
        call(link,7,[w.LPCWSTR],'Kai desktop island')
        iid=guid('0000010b-0000-0000-c000-000000000046')
        call(link,0,[c.POINTER(GUID),c.POINTER(c.c_void_p)],c.byref(iid),c.byref(persist))
        desktop=c.create_unicode_buffer(32768)
        c.WinDLL('shell32').SHGetFolderPathW(None,0x10,None,0,desktop)
        destination=Path(desktop.value)/'Kai.lnk'
        call(persist,6,[w.LPCWSTR,w.BOOL],str(destination),True)
        call(persist,5,[w.LPCWSTR,w.DWORD],str(destination),0)
        actual=c.create_unicode_buffer(32768)
        call(link,3,[w.LPWSTR,c.c_int,c.c_void_p,w.DWORD],actual,len(actual),None,0)
        assert Path(actual.value).samefile(root/'Kai.exe'),actual.value
        print('Shortcut verified:',destination)
    finally:
        if persist:call(persist,2,[])
        if link:call(link,2,[])
        ole.CoUninitialize()


if __name__=='__main__':main()
