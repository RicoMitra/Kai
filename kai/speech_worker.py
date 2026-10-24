"""Whisper's memory belongs to one short-lived child, never the resident UI."""
import multiprocessing as mp
import os
import threading
import time


def recognize(audio, options):
    os.environ['OMP_NUM_THREADS'] = '4'
    import psutil
    required = 2 * 2**30 if options.get('model', 'auto') in ('auto', 'medium') else 1536 * 2**20
    if psutil.virtual_memory().available < required:
        raise RuntimeError('RAM tersedia terlalu sedikit untuk model suara. Tutup aplikasi lain lalu coba lagi; island tetap dapat dipakai.')
    from stt import Transcriber
    transcriber = Transcriber(options)
    try:
        text, lang = transcriber.transcribe(audio)
    except Exception:
        if transcriber.device != 'cuda':
            raise
        import gc
        del transcriber
        gc.collect()
        if psutil.virtual_memory().available < 1536 * 2**20:
            raise RuntimeError('GPU gagal dan RAM tidak cukup untuk fallback CPU') from None
        fallback = dict(options, device='cpu')
        transcriber = Transcriber(fallback)
        text, lang = transcriber.transcribe(audio)
    return {'text': text, 'lang': lang, 'size': transcriber.size, 'device': transcriber.device}


def _entry(connection, backend, audio, options):
    try:
        connection.send(('ok', backend(audio, options)))
    except Exception as exc:
        connection.send(('error', str(exc)))
    finally:
        connection.close()


class SpeechJob:
    def __init__(self, backend=recognize):
        self.backend = backend
        self.process = None
        self._busy = threading.Lock()
        self._guard = threading.Lock()

    @property
    def busy(self):
        return self._busy.locked()

    def run(self, audio, options=None, timeout=180):
        if not self._busy.acquire(blocking=False):
            raise RuntimeError('Kai sedang memproses ucapan sebelumnya')
        context = mp.get_context('spawn')
        receive, send = context.Pipe(duplex=False)
        process = context.Process(target=_entry, args=(send, self.backend, audio, options or {}), daemon=True)
        try:
            with self._guard:
                self.process = process
                process.start()
            send.close()
            if not receive.poll(timeout):
                raise TimeoutError('Pengenalan suara melewati batas waktu; model dihentikan')
            try:
                status, result = receive.recv()
            except EOFError:
                raise RuntimeError('Proses pengenal suara berhenti sebelum mengirim hasil') from None
            if status != 'ok':
                raise RuntimeError(result)
            return result
        finally:
            send.close()
            receive.close()
            with self._guard:
                if process.pid is not None:
                    process.join(timeout=1)
                    if process.is_alive():
                        process.terminate()
                        process.join(timeout=3)
                    process.close()
                self.process = None
            self._busy.release()

    def cancel(self):
        with self._guard:
            if self.process is not None and self.process.pid and self.process.is_alive():
                self.process.terminate()
