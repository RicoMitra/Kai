"""Penyiar kejadian sederhana. Nanti island cukup subscribe ke sini
(atau lewat WebSocket/named pipe) untuk menampilkan teks yang terdengar dan hasil perintah."""
from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    kind: str   # ready, listening, heard, intent, result, timer_done, error
    text: str
    data: Any = None


_listeners = []


def subscribe(fn):
    _listeners.append(fn)


def unsubscribe(fn):
    if fn in _listeners:
        _listeners.remove(fn)


def emit(kind, text, data=None):
    ev = Event(kind, text, data)
    for fn in list(_listeners):
        try:
            fn(ev)
        except Exception as e:  # satu pendengar rusak tidak boleh mematikan Kai
            print(f"[events] listener error: {e}")
