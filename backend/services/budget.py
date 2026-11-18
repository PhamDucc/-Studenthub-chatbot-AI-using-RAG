"""One request deadline shared by retrieval, rewriting and generation."""

from contextlib import contextmanager
from contextvars import ContextVar
import time


_deadline: ContextVar[float | None] = ContextVar('chat_deadline', default=None)


@contextmanager
def request_budget(seconds: float):
    token = _deadline.set(time.monotonic() + seconds)
    try:
        yield
    finally:
        _deadline.reset(token)


def remaining_timeout(cap: float) -> float:
    deadline = _deadline.get()
    remaining = cap if deadline is None else min(cap, deadline - time.monotonic())
    if remaining <= 0:
        raise TimeoutError('Chat request deadline exceeded')
    return remaining
