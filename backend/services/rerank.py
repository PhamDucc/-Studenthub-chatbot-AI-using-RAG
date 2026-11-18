"""Optional LLM reranking of retrieval candidates (one Gemini call, falls back to the input order)."""

import json
import logging
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import GEMINI_MODEL
from ..models import Hit
from .budget import remaining_timeout

SNIPPET_CHARS = 420


def enabled() -> bool:
    return os.getenv("RAG_RERANK", "0") == "1" and bool(os.getenv("GEMINI_API_KEY", "").strip())


def parse_order(text: str, count: int) -> list[int]:
    """Valid, de-duplicated 0-based candidate indexes from the model's JSON (empty if unusable)."""
    try:
        raw = json.loads(text)["order"]
    except (ValueError, KeyError, TypeError):
        raw = [int(n) for n in re.findall(r"\d+", text)]
    order: list[int] = []
    for item in raw:
        if isinstance(item, int) and 1 <= item <= count and item - 1 not in order:
            order.append(item - 1)
    return order


def rerank(question: str, hits: list[Hit]) -> list[Hit]:
    """Reorder `hits` by relevance to the question; candidates the model omits keep their order after."""
    if len(hits) < 2:
        return hits
    listing = "\n\n".join(
        f"[{i}] {hit.passage.heading}\n{hit.passage.text[:SNIPPET_CHARS]}" for i, hit in enumerate(hits, 1)
    )
    prompt = (
        "Xếp hạng các đoạn tài liệu theo mức độ trả lời trực tiếp câu hỏi của sinh viên "
        "(đoạn chứa câu trả lời cụ thể lên đầu, đoạn chỉ nhắc qua chủ đề xuống cuối).\n\n"
        f"Câu hỏi: {question}\n\nCác đoạn:\n{listing}\n\n"
        'Chỉ trả về JSON dạng {"order": [số thứ tự các đoạn, tốt nhất trước]}.'
    )
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"].strip()},
    )
    retries = int(os.getenv("RERANK_RETRIES", "0"))
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=remaining_timeout(8)) as response:
                payload = json.load(response)
            text = "".join(p.get("text", "") for p in payload["candidates"][0]["content"]["parts"])
            order = parse_order(text, len(hits))
            break
        except HTTPError as exc:
            if exc.code == 429 and attempt < retries:
                time.sleep(15 * (attempt + 1))
                continue
            logging.warning("Rerank failed, keeping fused order: %s", exc)
            return hits
        except (URLError, TimeoutError, OSError, KeyError, IndexError, ValueError) as exc:
            logging.warning("Rerank failed, keeping fused order: %s", exc)
            return hits
    if not order:
        return hits
    rest = [i for i in range(len(hits)) if i not in order]
    return [hits[i] for i in order + rest]
