"""Local speech: resident PTT is small; Whisper exists only in a child process."""
import threading
import time

import config
from events import emit


def pick_device():
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return 'cuda', 'float16'
    except Exception:
        pass
    return 'cpu', 'int8'


class Transcriber:
    def __init__(self, options=None):
        from faster_whisper import WhisperModel
        from storage import data_dir
        options = options or {}
        device, compute = pick_device()
        if options.get('device') == 'cpu':
            device, compute = 'cpu', 'int8'
        requested = options.get('model', config.MODEL_SIZE)
        size = ('medium' if device == 'cuda' else 'small') if requested == 'auto' else requested
        if size not in ('tiny', 'base', 'small', 'medium'):
            raise ValueError('Model suara tidak valid')
        try:
            self.model = WhisperModel(size, device=device, compute_type=compute,
                                      cpu_threads=4, num_workers=1, download_root=str(data_dir() / 'models'))
        except Exception:
            if device != 'cuda':
                raise
            device, compute = 'cpu', 'int8'
            size = 'small' if requested == 'auto' else requested
            self.model = WhisperModel(size, device=device, compute_type=compute,
                                      cpu_threads=4, num_workers=1, download_root=str(data_dir() / 'models'))
        self.device, self.size = device, size
        self.prompt = 'Kai. ' + ', '.join(options.get('hint_names', config.HINT_NAMES))

    def transcribe(self, audio):
        lang = None
        try:
            _, _, probabilities = self.model.detect_language(audio)
            probabilities = dict(probabilities)
            lang = 'id' if probabilities.get('id', 0) + probabilities.get('ms', 0) >= probabilities.get('en', 0) else 'en'
        except Exception:
            pass
        segments, info = self.model.transcribe(
            audio, language=lang, beam_size=1, vad_filter=True,
            initial_prompt=self.prompt, condition_on_previous_text=False)
        return ' '.join(s.text.strip() for s in segments).strip(), lang or info.language


class PushToTalk:
    def __init__(self, on_audio, can_record=lambda: True):
        self.on_audio = on_audio
        self.can_record = can_record
        self._down = set()
        self._recording = False
        self._held = False
        self._enabled = True
        self._frames = []
        self._stream = None
        self._limit_timer = None
        self._hook = None
        self._lock = threading.RLock()

    @staticmethod
    def _norm(name):
        name = (name or '').lower()
        return 'ctrl' if 'ctrl' in name else name

    def start(self):
        import keyboard
        self._enabled = True
        self._hook = keyboard.hook(self._on_key, suppress=False)
        return self

    def _on_key(self, event):
        if not self._enabled:
            return
        name = self._norm(event.name)
        self._down.add(name) if event.event_type == 'down' else self._down.discard(name)
        both = all(k in self._down for k in config.HOTKEY)
        if both and not self._held:
            self._held = True
            self._begin()
        elif not both:
            self._held = False
            self._end()

    def _begin(self):
        if not self.can_record():
            emit('error', 'Kai masih memproses perintah sebelumnya')
            return
        stream = None
        try:
            import sounddevice as sd
            from storage import settings
            self._frames = []
            def callback(indata, frames, clock, status):
                with self._lock:
                    if self._recording:
                        self._frames.append(indata.copy())
            stream = sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1, dtype='float32',
                                    device=settings().get('microphone'), callback=callback)
            with self._lock:
                if not self._enabled:
                    stream.close()
                    return
                self._stream, self._recording = stream, True
            stream.start()
            self._limit_timer = threading.Timer(config.MAX_RECORD_SECONDS, self._end)
            self._limit_timer.daemon = True
            self._limit_timer.start()
            emit('listening', 'Mendengarkan...')
        except Exception as exc:
            with self._lock:
                self._recording, self._stream = False, None
            if stream is not None:
                stream.close()
            emit('error', f'Mikrofon tidak dapat dibuka: {exc}')

    def _end(self, process=True):
        with self._lock:
            if not self._recording:
                return
            self._recording = False
            stream, frames = self._stream, self._frames
            self._stream, self._frames = None, []
        if self._limit_timer:
            self._limit_timer.cancel()
        if stream:
            try:
                try:
                    stream.stop()
                except Exception as exc:
                    emit('error', f'Rekaman berhenti: {exc}')
            finally:
                stream.close()
        if not process:
            return
        if not frames:
            emit('heard', '(tidak terdengar)')
            return
        import numpy as np
        audio = np.concatenate(frames).flatten()[:int(config.MAX_RECORD_SECONDS * config.SAMPLE_RATE)]
        if len(audio) < config.MIN_RECORD_SECONDS * config.SAMPLE_RATE:
            emit('heard', '(terlalu singkat)')
            return
        threading.Thread(target=self.on_audio, args=(audio,), name='Kai speech request', daemon=True).start()

    def stop(self):
        self._enabled = False
        if self._hook is not None:
            import keyboard
            keyboard.unhook(self._hook)
            self._hook = None
        self._end(process=False)
        self._down.clear()


class VoiceService:
    def __init__(self, on_text):
        from speech_worker import SpeechJob
        self.job = SpeechJob()
        self.on_text = on_text
        self.stopped = threading.Event()
        self.ptt = PushToTalk(self._on_audio, lambda: not self.job.busy)

    def start(self):
        self.ptt.start()
        emit('ready', 'Kai siap')
        return self

    def _on_audio(self, audio):
        from storage import settings
        if self.stopped.is_set():
            return
        try:
            emit('loading', 'Memuat model suara sesuai kebutuhan...')
            began = time.perf_counter()
            result = self.job.run(audio, settings(), timeout=300)
            if self.stopped.is_set():
                return
            emit('info', f"{result['size']} / {result['device']} / {time.perf_counter() - began:.1f} dtk; model dilepas")
            if not result['text']:
                emit('heard', '(tidak terdengar)')
                return
            emit('heard', result['text'])
            self.on_text(result['text'])
        except Exception as exc:
            if not self.stopped.is_set():
                emit('error', f'Pengenalan suara: {exc}')

    def stop(self):
        self.stopped.set()
        self.ptt.stop()
        self.job.cancel()
