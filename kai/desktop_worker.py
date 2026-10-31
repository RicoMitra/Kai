"""Optional on-demand media/audio process. Closing it releases native libraries."""
import multiprocessing as mp
import threading

from events import emit


def _serve(pipe, stopped):
    import events
    from native import MediaService, AudioService, transport
    lock = threading.Lock()
    def forward(event):
        try:
            with lock:
                pipe.send((event.kind, event.text, event.data))
        except (BrokenPipeError, EOFError, OSError):
            stopped.set()
    events.subscribe(forward)
    media, audio = MediaService(), AudioService()
    try:
        media.start(); audio.start()
        while not stopped.is_set():
            if not pipe.poll(0.2):
                continue
            command, value = pipe.recv()
            try:
                if command == 'volume': audio.set_volume(value)
                elif command == 'mute': audio.toggle_mute()
                elif command == 'transport':
                    if not transport(value): emit('error', 'The player does not support seeking or rejected the position' if value.startswith('seek:') else 'No media session accepted the command')
            except Exception as exc:
                emit('error', str(exc))
    except (EOFError, OSError):
        pass
    finally:
        events.unsubscribe(forward)
        media.stop(); audio.stop()
        pipe.close()


class MediaProxy:
    def __init__(self, owner):
        self.owner, self.snapshot = owner, {}

    def command(self, value):
        self.owner.send('transport', value)

    def set_active(self, active):
        if active: self.owner.start()
        else: self.owner.stop(wait=False)


class AudioProxy:
    def __init__(self, owner):
        self.owner, self.snapshot = owner, {}

    def set_volume(self, value): self.owner.send('volume', value)
    def toggle_mute(self): self.owner.send('mute', None)


class DesktopServices:
    def __init__(self):
        self.media, self.audio = MediaProxy(self), AudioProxy(self)
        self.process = self.pipe = self.stopped = self.thread = None
        self.retired = []

    def start(self):
        if self.process is not None:
            return
        context = mp.get_context('spawn')
        receive, send = context.Pipe()
        stopped = context.Event()
        process = context.Process(target=_serve, args=(send, stopped), daemon=True)
        process.start()
        send.close()
        self.process, self.pipe, self.stopped = process, receive, stopped
        def read():
            try:
                while not stopped.is_set():
                    if not receive.poll(0.2): continue
                    kind, text, data = receive.recv()
                    if stopped.is_set(): break
                    if kind == 'media': self.media.snapshot = data or {}
                    elif kind in ('audio_state', 'volume'): self.audio.snapshot = data or {}
                    if not stopped.is_set(): emit(kind, text, data)
            except (EOFError, OSError):
                pass
        self.thread = threading.Thread(target=read, name='Kai desktop bridge', daemon=True)
        self.thread.start()

    def send(self, command, value):
        if self.pipe:
            try:
                self.pipe.send((command, value))
            except (BrokenPipeError, OSError):
                emit('error', 'Media service closed; reopen Music')

    def stop(self, wait=True):
        if self.process is None:
            if wait:
                for thread in self.retired: thread.join(timeout=3)
                self.retired = []
            return
        process, pipe, stopped, reader = self.process,self.pipe,self.stopped,self.thread
        self.process = self.pipe = self.stopped = self.thread = None
        stopped.set()
        def reap():
            process.join(timeout=1.5)
            if process.is_alive(): process.terminate(); process.join(timeout=2)
            reader.join(timeout=0.5)
            pipe.close(); process.close()
        if wait:
            reap()
            for thread in self.retired: thread.join(timeout=3)
            self.retired = []
        else:
            # Native worker is read-only apart from explicit transport/volume calls.
            # Reaping off the UI thread lets the hide spring run without a hitch.
            cleanup = threading.Thread(target=reap,name='Kai desktop cleanup',daemon=True)
            self.retired = [thread for thread in self.retired if thread.is_alive()]
            self.retired.append(cleanup); cleanup.start()
        self.media.snapshot = {}; self.audio.snapshot = {}
        emit('media', '', {})
        emit('audio_state', '', {})
