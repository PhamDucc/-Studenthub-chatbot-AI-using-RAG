"""Turn a follow-up ("thế còn D+ thì sao?") into a standalone search query."""

from functools import lru_cache
import json
import logging
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import GEMINI_MODEL
from ..models import ConversationTurn
from .retrieval import normalize, tokens
from .budget import remaining_timeout
from .lang import detect

_REFERENCE = re.compile(r"\b(the|con|vay|do|nay|ay|no|kia|tren|nua|them|tiep|ngoai ra|truong hop do|cai do|nhu vay)\b")


def context_detail(question: str) -> bool:
    text = normalize(question)
    if re.match(r'^(a khoan|khoan|minh nham|toi nham|nham|sua lai|thuc ra|neu|gia su|if)\b', text):
        return True
    question_words = re.search(r'bao nhieu|may tin|may ky|the nao|la gi|duoc khong|khong\?|chua\?|\?', text)
    return not question_words and bool(re.search(r'\b(?:gpa|cpa|drl|qh\d{4}|hoc xong|he chuan)\b|'
                                                r'^(?:minh|toi|em|t|to) hoc\b', text))


def needs_rewrite(question: str, history: list[ConversationTurn]) -> bool:
    if not history or not any(turn.role == "user" for turn in history):
        return False
    reference = (re.search(r'\b(it|that|this|those|them|there|then)\b', normalize(question))
                 if detect(question) == 'en' else _REFERENCE.search(normalize(question)))
    return len(tokens(question)) < 5 or bool(reference) or context_detail(question)


def concatenated(question: str, history: list[ConversationTurn]) -> str:
    """Prepend the previous user question. Only sensible for very short questions: on a full question the
    extra words dilute retrieval (hit@1 0.75 -> 0.38 on the follow-up eval)."""
    if context_detail(question):
        recent = [turn.content for turn in history if turn.role == 'user'][-3:]
        return ' '.join([*recent, question])
    if len(tokens(question)) >= 5:
        return question
    previous = next((turn.content for turn in reversed(history) if turn.role == "user"), None)
    return f"{previous} {question}" if previous else question


@lru_cache(maxsize=256)
def _ask(context: str, question: str, api_key: str) -> str:
    prompt = (
        "Viết lại câu hỏi cuối của sinh viên thành MỘT câu hỏi đầy đủ, tự đứng độc lập (thay đại từ, bổ sung chủ đề "
        "từ hội thoại), giữ nguyên ý, không trả lời câu hỏi.\n\n"
        f"Hội thoại:\n{context}\n\nCâu hỏi cuối: {question}\n\nChỉ trả về JSON {{\"query\": \"...\"}}."
    )
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json", "maxOutputTokens": 200}}
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    with urlopen(request, timeout=remaining_timeout(5)) as response:
        payload = json.load(response)
    text = "".join(p.get("text", "") for p in payload["candidates"][0]["content"]["parts"])
    query = json.loads(text)["query"].strip()
    if not 3 <= len(query) <= 400:
        raise ValueError("unusable rewrite")
    return query


def rewrite_query(question: str, history: list[ConversationTurn]) -> str:
    """Standalone query for retrieval; never raises (falls back to concatenation)."""
    if not needs_rewrite(question, history):
        return question
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key and os.getenv("RAG_REWRITE", "1") != "0":
        context = "\n".join(f"{t.role}: {t.content[:300]}" for t in history[-4:])
        try:
            return _ask(context, question, api_key)
        except (HTTPError, URLError, TimeoutError, OSError, KeyError, IndexError, ValueError) as exc:
            logging.warning("Query rewrite failed, concatenating instead: %s", exc)
    return concatenated(question, history)
