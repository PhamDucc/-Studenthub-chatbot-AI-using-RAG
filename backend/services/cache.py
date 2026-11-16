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


def _key(question: str) -> tuple:
    # Order- and filler-insensitive, and invalidated when the knowledge base changes.
    return (" ".join(sorted(set(tokens(question)))), data_signature())


def get(question: str) -> list[dict] | None:
    key = _key(question)
    with _lock:
        entry = _entries.get(key)
        if entry is None or time.monotonic() - entry[0] > TTL_SECONDS:
            _entries.pop(key, None)
            return None
        _entries.move_to_end(key)
        return entry[1]


def put(question: str, events: list[dict]) -> None:
    with _lock:
        _entries[_key(question)] = (time.monotonic(), events)
        _entries.move_to_end(_key(question))
        while len(_entries) > MAX_ENTRIES:
            _entries.popitem(last=False)


def clear() -> None:
    with _lock:
        _entries.clear()
