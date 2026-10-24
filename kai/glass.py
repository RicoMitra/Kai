"""Windows compositor host backdrop. No desktop capture, browser, or third-party DLL.

ABI facts: Microsoft windows-rs 0.58 Windows.UI.Composition and
ICompositorDesktopInterop. Kept here to avoid loading the full WinRT projection.
"""
import ctypes as c
from ctypes import wintypes as w
import uuid


class GUID(c.Structure):
    _fields_ = [('data',c.c_ubyte*16)]


def guid(value):
    return GUID((c.c_ubyte*16).from_buffer_copy(uuid.UUID(value).bytes_le))


def checked(value):
    if value < 0: raise OSError(f'Compositor HRESULT 0x{value & 0xffffffff:08x}')


def call(pointer, index, types, *args):
    table = c.cast(pointer,c.POINTER(c.POINTER(c.c_void_p))).contents
    method = c.WINFUNCTYPE(c.c_long,c.c_void_p,*types)(table[index])
    return method(pointer,*args)


class GaussianEffect:
    """D2D GaussianBlur description for the Windows composition effect factory."""
    def __init__(self, owner, source, properties):
        self.callbacks=[]; self.storage=[]; self.interfaces={}; self.count=1
        def callback(result,types,function):
            value=c.WINFUNCTYPE(result,c.c_void_p,*types)(function)
            self.callbacks.append(value); return value
        def query(_,identity,out):
            pointer=self.interfaces.get(bytes(c.string_at(identity,16)))
            out[0]=pointer
            if pointer: self.count+=1; return 0
            return -2147467262
        def add(_): self.count+=1; return self.count
        def release(_): self.count=max(1,self.count-1); return self.count
        base=[callback(c.c_long,[c.POINTER(GUID),c.POINTER(c.c_void_p)],query),
              callback(c.c_ulong,[],add),callback(c.c_ulong,[],release)]
        def ids(_,count,out): count[0]=0;out[0]=None;return 0
        def name(_,out): return owner.runtime.WindowsCreateString('GaussianBlur',12,out)
        def trust(_,out): out[0]=0;return 0
        inspectable=base+[callback(c.c_long,[c.POINTER(c.c_ulong),c.POINTER(c.c_void_p)],ids),callback(c.c_long,[c.POINTER(c.c_void_p)],name),callback(c.c_long,[c.POINTER(c.c_int)],trust)]
        graphics=inspectable+[callback(c.c_long,[c.POINTER(c.c_void_p)],name),callback(c.c_long,[c.c_void_p],lambda *_:0)]
        def effect_id(_,out):out[0]=guid('1feb6d69-2fe6-4ac9-8c58-1d7f93e7a6a5');return 0
        def count_property(_,out):out[0]=3;return 0
        def get_property(_,index,out):
            if index>=3:return -2147024809
            call(properties[index],1,[]);out[0]=properties[index].value;return 0
        def get_source(_,index,out):
            if index:return -2147024809
            call(source,1,[]);out[0]=source.value;return 0
        def count_source(_,out):out[0]=1;return 0
        interop=base+[callback(c.c_long,[c.POINTER(GUID)],effect_id),
            callback(c.c_long,[w.LPCWSTR,c.POINTER(c.c_uint),c.POINTER(c.c_uint)],lambda *_:-2147467263),
            callback(c.c_long,[c.POINTER(c.c_uint)],count_property),
            callback(c.c_long,[c.c_uint,c.POINTER(c.c_void_p)],get_property),
            callback(c.c_long,[c.c_uint,c.POINTER(c.c_void_p)],get_source),
            callback(c.c_long,[c.POINTER(c.c_uint)],count_source)]
        def make(methods):
            table=(c.c_void_p*len(methods))(*[c.cast(method,c.c_void_p).value for method in methods])
            class Interface(c.Structure):_fields_=[('table',c.POINTER(c.c_void_p))]
            instance=Interface(table);self.storage.extend([table,instance]);return c.addressof(instance)
        self.pointer=c.c_void_p(make(graphics)); native=make(interop)
        for identity in ('00000000-0000-0000-c000-000000000046','af86e2e0-b12d-4c6a-9c5a-d7aa65101e90','cb51c0ce-8fe6-4636-b202-861faa07d8f3','2d8f9ddc-4339-4eb9-9216-f9deb75658a2'):
            self.interfaces[bytes(guid(identity).data)]=self.pointer.value
        self.interfaces[bytes(guid('2fc57384-a068-44d7-a331-30982fcf7177').data)]=native


class Backdrop:
    def __init__(self, owner, x, y, width, height, test_color=False):
        self.references=[]; self.hwnd=None; self.target=None
        self.registered=False; self.ro_initialized=False
        self.user=c.WinDLL('user32',use_last_error=True)
        self.gdi=c.WinDLL('gdi32'); self.dwm=c.WinDLL('dwmapi'); self.runtime=c.WinDLL('combase')
        self.user.CreateWindowExW.argtypes=[w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,c.c_int,c.c_int,c.c_int,c.c_int,w.HWND,w.HMENU,w.HINSTANCE,c.c_void_p]
        self.user.CreateWindowExW.restype=w.HWND
        self.user.SetWindowPos.argtypes=[w.HWND,w.HWND,c.c_int,c.c_int,c.c_int,c.c_int,w.UINT]
        self.user.DestroyWindow.argtypes=[w.HWND]
        self.user.EnableWindow.argtypes=[w.HWND,w.BOOL]
        self.user.SetLayeredWindowAttributes.argtypes=[w.HWND,w.DWORD,c.c_ubyte,w.DWORD]
        self.user.UnregisterClassW.argtypes=[w.LPCWSTR,w.HINSTANCE]
        self.user.DefWindowProcW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]; self.user.DefWindowProcW.restype=c.c_ssize_t
        self.user.ValidateRect.argtypes=[w.HWND,c.c_void_p]
        self.user.SetWindowRgn.argtypes=[w.HWND,w.HRGN,w.BOOL]
        self.gdi.CreateRoundRectRgn.argtypes=[c.c_int]*6; self.gdi.CreateRoundRectRgn.restype=w.HRGN
        self.dwm.DwmSetWindowAttribute.argtypes=[w.HWND,c.c_uint,c.c_void_p,c.c_uint]
        self.owner=owner; self.shape=None; self.shown=False
        try:
            self.ro_initialized=self.runtime.RoInitialize(0) in (0,1)
            class QueueOptions(c.Structure):
                _fields_=[('size',w.DWORD),('thread',c.c_int),('apartment',c.c_int)]
            controller=c.c_void_p()
            queue=c.WinDLL('CoreMessaging').CreateDispatcherQueueController
            queue.argtypes=[QueueOptions,c.POINTER(c.c_void_p)]; queue.restype=c.c_long
            result=queue(QueueOptions(c.sizeof(QueueOptions),2,0),c.byref(controller))
            self.queue_result=result
            if result>=0 and controller: self.references.append(controller)
            self.runtime.WindowsCreateString.argtypes=[w.LPCWSTR,c.c_uint,c.POINTER(c.c_void_p)]
            self.runtime.WindowsDeleteString.argtypes=[c.c_void_p]
            self.runtime.RoActivateInstance.argtypes=[c.c_void_p,c.POINTER(c.c_void_p)]
            string=c.c_void_p(); instance=c.c_void_p()
            name='Windows.UI.Composition.Compositor'
            checked(self.runtime.WindowsCreateString(name,len(name),c.byref(string)))
            try: checked(self.runtime.RoActivateInstance(string,c.byref(instance)))
            finally: self.runtime.WindowsDeleteString(string)
            self.references.append(instance)
            compositor=self.query(instance,'b403ca50-7f8c-4e83-985f-cc45060036d8')
            interop=self.query(instance,'29e691fa-4567-4dca-b319-d0f207eb6807')
            callback=c.WINFUNCTYPE(c.c_ssize_t,w.HWND,w.UINT,w.WPARAM,w.LPARAM)
            @callback
            def procedure(hwnd,message,wp,lp):
                if message==0x84: return -1
                if message==0x21: return 3
                if message==0x14: return 1
                if message==0x0f: self.user.ValidateRect(hwnd,None); return 0
                return self.user.DefWindowProcW(hwnd,message,wp,lp)
            self.procedure=procedure
            class WindowClass(c.Structure):
                _fields_=[('style',w.UINT),('procedure',callback),('class_extra',c.c_int),('window_extra',c.c_int),('instance',w.HINSTANCE),('icon',w.HICON),('cursor',w.HANDLE),('background',w.HBRUSH),('menu',w.LPCWSTR),('name',w.LPCWSTR)]
            self.class_name='KaiGlass'+str(id(self))
            self.user.RegisterClassW.argtypes=[c.POINTER(WindowClass)]
            window_class=WindowClass(0,procedure,0,0,None,None,None,None,None,self.class_name)
            if not self.user.RegisterClassW(c.byref(window_class)): raise c.WinError(c.get_last_error())
            self.registered=True
            self.hwnd=self.user.CreateWindowExW(0x082800a8,self.class_name,'',0x80000000,x,y,width,height,None,None,None,None)
            if not self.hwnd: raise c.WinError(c.get_last_error())
            self.user.EnableWindow(self.hwnd,False)
            self.user.SetLayeredWindowAttributes(self.hwnd,0,255,2)
            flag=c.c_int(1); self.dwm.DwmSetWindowAttribute(self.hwnd,17,c.byref(flag),4)
            class Accent(c.Structure): _fields_=[('state',c.c_int),('flags',c.c_int),('color',c.c_uint32),('animation',c.c_int)]
            class Attribute(c.Structure): _fields_=[('attribute',c.c_int),('data',c.c_void_p),('size',c.c_size_t)]
            accent=Accent(5,0,0,0); attribute=Attribute(19,c.addressof(accent),c.sizeof(accent))
            self.user.SetWindowCompositionAttribute.argtypes=[w.HWND,c.POINTER(Attribute)]
            self.user.SetWindowCompositionAttribute(self.hwnd,c.byref(attribute))
            target=self.output(interop,3,[w.HWND,w.BOOL],self.hwnd,True)
            self.target=self.query(target,'a1bea8ba-d726-4663-8129-6b5e7927ffa6')
            sprite=self.output(compositor,22,[])
            visual=self.query(sprite,'117e202d-a859-4c89-873b-c2aa566788e3')
            compositor2=self.query(instance,'735081dc-5e24-45da-a38f-e32cc349a9a0')
            backdrop=self.output(compositor2,8,[])
            brush=self.query(backdrop,'ab0d7608-30c0-40e9-b568-b60a6bd1fb46')
            if not test_color:
                factory=self.factory('Windows.UI.Composition.CompositionEffectSourceParameter','b3d9f276-aba3-4724-acf3-d0397464db1c')
                label=c.c_void_p();checked(self.runtime.WindowsCreateString('backdrop',8,c.byref(label)))
                try: parameter=self.output(factory,6,[c.c_void_p],label)
                finally:self.runtime.WindowsDeleteString(label)
                source=self.query(parameter,'2d8f9ddc-4339-4eb9-9216-f9deb75658a2')
                values=self.factory('Windows.Foundation.PropertyValue','629bdbc8-d932-4ff4-96b9-8d96c5c1e858')
                properties=[self.output(values,14,[c.c_float],22.0),self.output(values,11,[c.c_uint],1),self.output(values,11,[c.c_uint],1)]
                self.effect=GaussianEffect(self,source,properties)
                effect_factory=self.output(compositor,11,[c.c_void_p],self.effect.pointer)
                effect_brush=self.output(effect_factory,6,[])
                label=c.c_void_p();checked(self.runtime.WindowsCreateString('backdrop',8,c.byref(label)))
                try:checked(call(effect_brush,7,[c.c_void_p,c.c_void_p],label,brush))
                finally:self.runtime.WindowsDeleteString(label)
                brush=self.query(effect_brush,'ab0d7608-30c0-40e9-b568-b60a6bd1fb46')
            if test_color:
                class Color(c.Structure): _fields_=[('a',c.c_ubyte),('r',c.c_ubyte),('g',c.c_ubyte),('b',c.c_ubyte)]
                color=self.output(compositor,8,[Color],Color(255,240,20,100))
                brush=self.query(color,'ab0d7608-30c0-40e9-b568-b60a6bd1fb46')
            class Vector2(c.Structure): _fields_=[('x',c.c_float),('y',c.c_float)]
            checked(call(visual,36,[Vector2],Vector2(width,height)))
            checked(call(sprite,7,[c.c_void_p],brush))
            checked(call(self.target,7,[c.c_void_p],visual))
            self.user.SetWindowPos(self.hwnd,owner,x,y,width,height,0x0010)
        except Exception:
            self.close(); raise

    def query(self, instance, identity):
        result=c.c_void_p(); iid=guid(identity)
        checked(call(instance,0,[c.POINTER(GUID),c.POINTER(c.c_void_p)],c.byref(iid),c.byref(result)))
        self.references.append(result); return result

    def factory(self,name,identity):
        self.runtime.RoGetActivationFactory.argtypes=[c.c_void_p,c.POINTER(GUID),c.POINTER(c.c_void_p)]
        string=c.c_void_p();result=c.c_void_p();iid=guid(identity)
        checked(self.runtime.WindowsCreateString(name,len(name),c.byref(string)))
        try:checked(self.runtime.RoGetActivationFactory(string,c.byref(iid),c.byref(result)))
        finally:self.runtime.WindowsDeleteString(string)
        self.references.append(result);return result

    def output(self,instance,index,types,*args):
        result=c.c_void_p()
        checked(call(instance,index,types+[c.POINTER(c.c_void_p)],*args,c.byref(result)))
        self.references.append(result); return result

    def clip(self,x,y,width,height,radius):
        shape=(x,y,width,height,radius)
        if shape==self.shape: return
        self.shape=shape
        region=self.gdi.CreateRoundRectRgn(x,y,x+width+1,y+height+1,radius*2,radius*2)
        self.user.SetWindowRgn(self.hwnd,region,True)
        if not self.shown:
            self.user.SetWindowPos(self.hwnd,self.owner,0,0,0,0,0x0053)
            self.shown=True

    def close(self):
        if self.target: call(self.target,7,[c.c_void_p],None); self.target=None
        if self.hwnd: self.user.DestroyWindow(self.hwnd); self.hwnd=None
        if self.registered:
            self.user.UnregisterClassW(self.class_name,None);self.registered=False
        for reference in reversed(self.references): call(reference,2,[])
        self.references=[]
        if self.ro_initialized:self.runtime.RoUninitialize();self.ro_initialized=False
