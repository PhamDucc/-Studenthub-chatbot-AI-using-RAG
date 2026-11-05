"""Optional Gemini generation using the REST API and Python standard library."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import GEMINI_MODEL
from ..models import ConversationTurn, Hit


def generate_answer(question: str, hits: list[Hit], api_key: str, history: list[ConversationTurn] | None = None) -> str:
    context = "\n\n".join(
        f"[{i}] {hit.passage.title} | {hit.passage.heading} | {hit.passage.source}\n{hit.passage.text}"
        for i, hit in enumerate(hits, 1)
    )
    conversation = "\n".join(f"{turn.role}: {turn.content}" for turn in (history or []))
    prompt = (
        ("Hội thoại gần đây:\n" + conversation + "\n\n" if conversation else "")
        + "Câu hỏi hiện tại: " + question + "\n\nNguồn được truy xuất:\n" + context
        + "\n\nTrả lời bằng tiếng Việt, ngắn gọn và đúng theo nguồn. "
        "Dẫn số nguồn dạng [1], [2] ngay sau thông tin tương ứng. "
        "Nếu nguồn chưa đủ, nói rõ phần chưa biết. Không dùng kiến thức ngoài nguồn."
    )
    body = {
        "systemInstruction": {"parts": [{"text": "Bạn là trợ lý thông tin sinh viên UET. Chỉ dùng nguồn được cung cấp; không suy đoán."}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urlopen(request, timeout=25) as response:
            payload = json.load(response)
        parts = payload["candidates"][0]["content"]["parts"]
        answer = "\n".join(part.get("text", "") for part in parts).strip()
        if not answer:
            raise ValueError("Gemini returned an empty answer")
        return answer
    except (HTTPError, URLError, KeyError, IndexError, ValueError) as exc:
        raise RuntimeError(f"Không gọi được Gemini: {exc}") from exc
