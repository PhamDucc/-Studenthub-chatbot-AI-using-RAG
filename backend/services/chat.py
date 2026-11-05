"""Coordinate retrieval, optional generation, and offline fallback."""

import os

from .gemini import generate_answer
from ..models import ChatResult, ConversationTurn
from .retrieval import extract_answer, search, tokens


NO_MATCH = (
    "Mình chưa tìm thấy thông tin phù hợp trong sáu tài liệu hiện có. "
    "Bạn có thể hỏi cụ thể hơn hoặc liên hệ phòng phụ trách."
)


def answer_question(question: str, history: list[ConversationTurn] | None = None) -> ChatResult:
    history = history or []
    search_query = question
    if len(tokens(question)) < 5:
        previous_question = next((turn.content for turn in reversed(history) if turn.role == "user"), None)
        if previous_question:
            search_query = previous_question + " " + question

    hits = search(search_query)
    if not hits:
        return ChatResult(NO_MATCH, [], mode="no_match")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        try:
            return ChatResult(generate_answer(question, hits, api_key, history), hits, mode="gemini")
        except RuntimeError as exc:
            warning = str(exc)
    else:
        warning = None

    return ChatResult(extract_answer(search_query, hits), hits, warning, mode="extractive")
