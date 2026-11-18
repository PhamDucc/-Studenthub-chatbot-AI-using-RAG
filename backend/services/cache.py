"""Small in-memory cache of finished answers to context-free regulation questions."""

from collections import OrderedDict
import threading
import time

from ..repositories.documents import data_signature
from .retrieval import tokens

MAX_ENTRIES = 200
TTL_SECONDS = 3600

_entries: "OrderedDict[tuple, tuple[float, list[dict]]]" = OrderedDict()
_lock = threading.Lock()


def _key(question: str, language: str | None = None) -> tuple:
    from .lang import detect
    # Order- and filler-insensitive, and invalidated when the knowledge base changes.
    return (" ".join(sorted(set(tokens(question)))), language or detect(question), data_signature())


def get(question: str, language: str | None = None) -> list[dict] | None:
    key = _key(question, language)
    with _lock:
        entry = _entries.get(key)
        if entry is None or time.monotonic() - entry[0] > TTL_SECONDS:
            _entries.pop(key, None)
            return None
        _entries.move_to_end(key)
        return entry[1]


def put(question: str, events: list[dict], language: str | None = None) -> None:
    key = _key(question, language)
    with _lock:
        _entries[key] = (time.monotonic(), events)
        _entries.move_to_end(key)
        while len(_entries) > MAX_ENTRIES:
            _entries.popitem(last=False)


def clear() -> None:
    with _lock:
        _entries.clear()
