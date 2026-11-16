"""Per-client rate limiting and PII redaction for stored text."""

from collections import defaultdict, deque
import re
import threading
import time

from ..config import RATE_LIMIT_PER_MINUTE


class RateLimiter:
    """Sliding-window limiter: at most `limit` requests per `window` seconds per key."""

    def __init__(self, limit: int, window: float = 60.0) -> None:
        self.limit, self.window = limit, window
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, now: float | None = None) -> float:
        """Return 0 when allowed, otherwise the seconds to wait before retrying."""
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return max(self.window - (now - hits[0]), 1.0)
            hits.append(now)
            if len(self._hits) > 5000:  # drop idle keys
                for stale in [k for k, v in self._hits.items() if not v or now - v[-1] >= self.window]:
                    del self._hits[stale]
            return 0.0


chat_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

_PII = [
    (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "[email]"),
    (re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.-]?\d){9}(?!\d)"), "[điện thoại]"),
    (re.compile(r"(?<!\d)\d{12}(?!\d)"), "[số định danh]"),
    (re.compile(r"(?<!\d)\d{8}(?!\d)"), "[mã sinh viên]"),
]


def redact(text: str | None) -> str | None:
    if not text:
        return text
    for pattern, placeholder in _PII:
        text = pattern.sub(placeholder, text)
    return text
