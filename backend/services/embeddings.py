"""Dense retrieval with Gemini embeddings (REST, stdlib only).

Passage vectors are computed once per knowledge-base version and cached on disk.
Every failure degrades to "no dense results" so callers fall back to BM25.
"""

from functools import lru_cache
import hashlib
import json
import logging
import math
import os
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import EMBED_CACHE, EMBED_DIMS, EMBED_MODEL
from ..models import Passage

_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:{method}"
_BATCH = 50
_RETRY_AFTER = 60.0  # seconds to wait before retrying after a failure

_lock = threading.Lock()
_index: tuple[str, list[list[float]]] | None = None  # (fingerprint, vectors)
_failed_at = 0.0


def enabled() -> bool:
    return os.getenv("RAG_DENSE", "1") != "0" and bool(os.getenv("GEMINI_API_KEY", "").strip())


def _post(method: str, body: dict, timeout: float = 30, retries: int = 0) -> dict:
    """POST to the embeddings API; 429s are retried with backoff (only when `retries` > 0)."""
    for attempt in range(retries + 1):
        request = Request(
            _BASE.format(model=EMBED_MODEL, method=method), data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"].strip()},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code != 429 or attempt == retries:
                raise
            time.sleep(min(20 * (attempt + 1), 65))
    raise AssertionError("unreachable")


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / norm for x in vector]


def embed_passages(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for start in range(0, len(texts), _BATCH):
        requests = [
            {"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": text}]},
             "taskType": "RETRIEVAL_DOCUMENT", "outputDimensionality": EMBED_DIMS}
            for text in texts[start:start + _BATCH]
        ]
        result = _post("batchEmbedContents", {"requests": requests}, timeout=60, retries=6)
        vectors.extend(_normalize(item["values"]) for item in result["embeddings"])
    return vectors


@lru_cache(maxsize=512)
def _embed_query(question: str) -> tuple[float, ...]:
    body = {"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": question}]},
            "taskType": "RETRIEVAL_QUERY", "outputDimensionality": EMBED_DIMS}
    retries = int(os.getenv("EMBED_QUERY_RETRIES", "0"))
    return tuple(_normalize(_post("embedContent", body, retries=retries)["embedding"]["values"]))


def _passage_text(passage: Passage) -> str:
    return f"{passage.title} | {passage.heading}\n{passage.text}"


def _fingerprint(passages: list[Passage]) -> str:
    digest = hashlib.sha256(f"{EMBED_MODEL}:{EMBED_DIMS}".encode())
    for passage in passages:
        digest.update(_passage_text(passage).encode("utf-8"))
    return digest.hexdigest()


def _vectors(passages: list[Passage], build: bool = False) -> list[list[float]] | None:
    """Vectors from memory or the disk cache; only `build=True` may call the API (None if unavailable)."""
    global _index, _failed_at
    fingerprint = _fingerprint(passages)
    with _lock:
        if _index and _index[0] == fingerprint:
            return _index[1]
        try:
            cached = json.loads(EMBED_CACHE.read_text(encoding="utf-8"))
            if cached.get("fingerprint") == fingerprint:
                _index = (fingerprint, cached["vectors"])
                return _index[1]
        except (OSError, ValueError, KeyError):
            pass
        if not build or (_failed_at and time.monotonic() - _failed_at < _RETRY_AFTER):
            return None
        try:
            vectors = embed_passages([_passage_text(p) for p in passages])
        except (HTTPError, URLError, TimeoutError, OSError, KeyError, ValueError) as exc:
            logging.warning("Embedding passages failed, using BM25 only: %s", exc)
            _failed_at = time.monotonic()
            return None
        _index = (fingerprint, vectors)
        try:
            EMBED_CACHE.write_text(json.dumps({"fingerprint": fingerprint, "vectors": vectors}), encoding="utf-8")
        except OSError:
            logging.warning("Could not write the embedding cache")
        return vectors


def dense_rank(question: str, passages: list[Passage], limit: int = 20) -> list[tuple[int, float]]:
    """[(passage index, cosine)] best first, or [] when dense retrieval is unavailable."""
    global _failed_at
    if not enabled():
        return []
    vectors = _vectors(passages)
    if vectors is None:
        return []
    try:
        query = _embed_query(question)
    except (HTTPError, URLError, TimeoutError, OSError, KeyError, ValueError) as exc:
        logging.warning("Embedding query failed, using BM25 only: %s", exc)
        _failed_at = time.monotonic()
        return []
    scored = [(i, sum(a * b for a, b in zip(query, vector))) for i, vector in enumerate(vectors)]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:limit]


def ensure_index(passages: list[Passage]) -> bool:
    """Build (or load) the passage vectors now, blocking. Returns True when dense retrieval is ready."""
    return enabled() and _vectors(passages, build=True) is not None


def start_warmup(passages: list[Passage]) -> None:
    """Build the index in the background so requests use BM25 until it is ready."""
    if enabled():
        threading.Thread(target=ensure_index, args=(passages,), name="embedding-warmup", daemon=True).start()
