"""Coordinate retrieval, optional generation, and offline fallback."""

from collections.abc import Iterator
import os
import re

from . import cache, tools
from .conversation import resolve_question
from .answer_checks import completeness_issues
from .intent import Intent, classify, needs_student_tools
from .lang import detect
from .rewrite import needs_rewrite, rewrite_query
from .gemini import FollowUpFilter, api_error, build_prompt, generate_answer, request_budget, stream_turn, valid_citations
from ..config import MAX_TOOL_ROUNDS, CHAT_TIMEOUT_SECONDS
from ..models import ChatResult, ConversationTurn, Hit
from .retrieval import best_sentence, extract_answer, search


NO_MATCH_TEXT = {
    "vi": "Mình chưa tìm thấy thông tin phù hợp trong các tài liệu hiện có. "
          "Bạn có thể hỏi cụ thể hơn hoặc gửi câu hỏi cho nhân viên hỗ trợ.",
    "en": "I couldn't find matching information in the available documents. "
          "Try rephrasing your question, or send it to a support staff member.",
}
NO_MATCH = NO_MATCH_TEXT["vi"]

FOLLOW_UPS = {
    "vi": [
        "Điều kiện nhận học bổng khuyến khích học tập là gì?",
        "Khi nào sinh viên bị cảnh báo học vụ?",
        "Thủ tục xin giấy xác nhận sinh viên gồm những bước nào?",
    ],
    "en": [
        "What are the requirements for the academic scholarship?",
        "When does a student get an academic warning?",
        "What are the steps to request a student certificate?",
    ],
}
DEFAULT_FOLLOW_UPS = FOLLOW_UPS["vi"]

FAILURE_TEXT = {
    'vi': {
        'timeout': 'Dịch vụ AI phản hồi quá chậm nên câu trả lời chưa hoàn tất. Bạn thử gửi lại sau ít giây nhé.',
        'rate_limit': 'Dịch vụ AI đang giới hạn lượt gọi hoặc quota. Bạn vui lòng đợi rồi thử lại.',
        'auth': 'Dịch vụ AI chưa được cấp quyền truy cập. Cần kiểm tra API key và quyền của dự án.',
        'model': 'Cấu hình model AI chưa hợp lệ hoặc model không hỗ trợ yêu cầu này. Cần kiểm tra cấu hình backend.',
        'unavailable': 'Chưa kết nối được dịch vụ AI để trả lời câu hỏi này. Bạn thử lại sau ít giây nhé.',
    },
    'en': {
        'timeout': 'The AI service took too long to respond. Please try again in a few seconds.',
        'rate_limit': 'The AI service has reached a rate or quota limit. Please wait before trying again.',
        'auth': 'The AI service is not authorized. Check the API key and project permissions.',
        'model': 'The AI model configuration is invalid or does not support this request. Check the backend configuration.',
        'unavailable': 'The AI service is unavailable right now. Please try again in a few seconds.',
    },
}

ATTACHMENT_FAILED = {
    "vi": "Mình chưa đọc được tệp đính kèm lúc này (dịch vụ AI đang bận). Bạn thử gửi lại sau ít phút, hoặc gõ nội dung cần hỏi nhé.",
    "en": "I couldn't read the attachment just now (the AI service is busy). Please try again in a few minutes, or type your question.",
}

ATTACHMENT_OFFLINE = {
    "vi": "Mình cần kết nối Gemini để đọc ảnh/PDF. Hiện chế độ này chưa khả dụng — bạn hãy gõ nội dung cần hỏi nhé.",
    "en": "I need a Gemini connection to read images/PDFs, which isn't available right now. Please type your question.",
}


_search_query = rewrite_query


def derive_follow_ups(hits: list[Hit], limit: int = 3) -> list[str]:
    """Offline follow-ups: point to other sections that were retrieved."""
    seen = {hits[0].passage.heading} if hits else set()
    result: list[str] = []
    for hit in hits[1:]:
        heading = hit.passage.heading
        if heading in seen:
            continue
        seen.add(heading)
        result.append(f"Cho mình biết thêm về «{heading.split(' > ')[-1]}»")
        if len(result) == limit:
            break
    return result


def answer_question(question: str, history: list[ConversationTurn] | None = None) -> ChatResult:
    history = history or []
    intent = classify(question)
    lang = detect(question)
    if intent.reply:
        return ChatResult(intent.reply, [], mode="no_match", follow_ups=FOLLOW_UPS[lang])
    search_query = _search_query(question, history)

    hits = search(search_query)
    if not hits:
        return ChatResult(NO_MATCH_TEXT[lang], [], mode="no_match", follow_ups=FOLLOW_UPS[lang])

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        try:
            answer, follow_ups = generate_answer(question, hits, api_key, history)
            return ChatResult(answer, hits, mode="gemini",
                              follow_ups=follow_ups or derive_follow_ups(hits))
        except RuntimeError as exc:
            warning = str(exc)
    else:
        warning = None

    return ChatResult(extract_answer(search_query, hits), hits, warning,
                      mode="extractive", follow_ups=derive_follow_ups(hits))


def hit_to_dict(number: int, hit: Hit, question: str) -> dict:
    return {
        "number": number, "title": hit.passage.title, "heading": hit.passage.heading,
        "source": hit.passage.source, "score": round(hit.score, 4),
        "excerpt": hit.passage.text[:240].strip(),
        "text": hit.passage.text[:1500].strip(),
        "highlight": best_sentence(question, hit.passage),
    }


class Ungrounded(Exception):
    """The model answered, but not from the sources or tools (likely out of scope)."""


def _cited(answer: str, hit_count: int) -> list[int]:
    return sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer) if 1 <= int(n) <= hit_count})


def _fallback(search_query: str, hits: list[Hit], warning: str | None, replace: bool, lang: str = "vi") -> Iterator[dict]:
    """Offline answer from the retrieved passages (or NO_MATCH when there are none)."""
    if replace:
        yield {"type": "replace", "text": ""}
    if not hits:
        yield {"type": "delta", "text": NO_MATCH_TEXT[lang]}
        yield {"type": "done", "mode": "no_match", "warning": warning, "follow_ups": FOLLOW_UPS[lang],
               "tools": [], "cited": [], "needs_human": True, "lang": lang}
        return
    for line in extract_answer(search_query, hits).splitlines(keepends=True):
        yield {"type": "delta", "text": line}
    yield {"type": "done", "mode": "extractive", "warning": warning, "follow_ups": derive_follow_ups(hits),
           "tools": [], "cited": [], "needs_human": False, "lang": lang}


def stream_chat(question: str, history: list[ConversationTurn] | None = None,
                attachment: dict | None = None, response_language: str | None = None) -> Iterator[dict]:
    """Yield events: sources, delta*, tool*, action*, (replace)?, done."""
    resolved = resolve_question(question, history or [], response_language, has_attachment=bool(attachment))
    if resolved.reply:
        yield {"type": "sources", "sources": []}
        yield {"type": "delta", "text": resolved.reply}
        yield {"type": "done", "mode": "blocked" if classify(question).kind == "blocked" else "smalltalk",
               "warning": None, "tools": [], "cited": [], "needs_human": False,
               "lang": resolved.language, "response_language": resolved.preference, "follow_ups": []}
        return
    for event in _stream_question(resolved.question, resolved.history, attachment, resolved.language):
        if event["type"] == "done":
            event = {**event, "response_language": resolved.preference}
        yield event


def _stream_question(question: str, history: list[ConversationTurn],
                     attachment: dict | None, lang: str) -> Iterator[dict]:
    intent = classify(question, lang)
    if intent.reply and (intent.kind == "blocked" or not attachment):  # no retrieval or model call needed
        yield {"type": "sources", "sources": []}
        yield {"type": "delta", "text": intent.reply}
        yield {"type": "done", "mode": intent.kind, "warning": None, "tools": [], "cited": [], "needs_human": False,
               "lang": lang, "follow_ups": FOLLOW_UPS[lang] if intent.kind == "smalltalk" else []}
        return

    context_needed = needs_rewrite(question, history)
    cacheable = (not context_needed and intent.kind == 'regulation' and not attachment
                 and not needs_student_tools(question, history))
    if cacheable and (stored := cache.get(question, language=lang)) is not None:
        yield from _replay(stored)
        return

    stream = _stream_model(question, history, intent, attachment, lang)
    if not cacheable:
        yield from stream
        return
    recorded: list[dict] = []
    for event in stream:
        recorded.append(event)
        yield event
    done = recorded[-1] if recorded else {}
    if done.get("type") == "done" and done.get("mode") == "gemini" and not done.get("tools"):
        text = ''
        for event in recorded:
            if event['type'] == 'replace':
                text = event['text']
            elif event['type'] == 'delta':
                text += event['text']
        cache.put(question, [recorded[0], {"type": "delta", "text": text}, done], language=lang)


def _replay(events: list[dict]) -> Iterator[dict]:
    """Re-emit a cached answer in small chunks so the UI streams it like a fresh one."""
    for event in events:
        if event["type"] == "delta":
            text = event["text"]
            for start in range(0, len(text), 60):
                yield {"type": "delta", "text": text[start:start + 60]}
        elif event["type"] == "done":
            yield {**event, "cached": True}
        else:
            yield event


def _stream_model(question: str, history: list[ConversationTurn], intent: Intent,
                  attachment: dict | None = None, lang: str | None = None) -> Iterator[dict]:
    with request_budget(CHAT_TIMEOUT_SECONDS):
        yield from _run_model(question, history, intent, attachment, lang)


def _run_model(question: str, history: list[ConversationTurn], intent: Intent,
               attachment: dict | None = None, lang: str | None = None) -> Iterator[dict]:
    lang = lang or detect(question)
    allow_tools = needs_student_tools(question, history)
    personal_only = intent.kind == 'personal' and allow_tools
    search_query = question if personal_only else _search_query(question, history)
    hits = [] if personal_only else search(search_query)
    yield {"type": "sources", "sources": [hit_to_dict(i, hit, search_query) for i, hit in enumerate(hits, 1)]}

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        if attachment:
            yield {"type": "delta", "text": ATTACHMENT_OFFLINE[lang]}
            yield {"type": "done", "mode": "no_match", "warning": None, "tools": [], "cited": [],
                   "needs_human": False, "lang": lang, "follow_ups": []}
            return
        yield from _fallback(search_query, hits, None, replace=False, lang=lang)
        return

    relevant_history = history[-6:] if needs_rewrite(question, history) else []
    contents = [{"role": "model" if t.role == "assistant" else "user", "parts": [{"text": t.content}]}
                for t in relevant_history]
    # History is already sent as contents above; don't copy it into the prompt.
    parts = [{"text": build_prompt(question, hits, None, tools.today_label(), lang, bool(attachment))}]
    if attachment:
        parts.append({"inlineData": {"mimeType": attachment["mime"], "data": attachment["data"]}})
    contents.append({"role": "user", "parts": parts})
    answer, started, used, follow_ups = "", False, [], []
    try:
        for round_number in range(MAX_TOOL_ROUNDS + 1):
            splitter, calls, raw_parts = FollowUpFilter(), [], []
            # The last round has no tools, which forces a final text answer.
            declared = tools.declarations() if allow_tools and round_number < MAX_TOOL_ROUNDS else None
            for kind, value in stream_turn(contents, api_key, declared):
                if kind == "text":
                    text = splitter.feed(value)
                    if text:
                        started, answer = True, answer + text
                        yield {"type": "delta", "text": text}
                elif kind == "call":
                    calls.append(value)
                else:
                    raw_parts = value
            leftover, follow_ups = splitter.finish()
            if leftover:
                started, answer = True, answer + leftover
                yield {"type": "delta", "text": leftover}
            if not calls:
                break
            contents.append({"role": "model", "parts": raw_parts})
            responses = []
            for call in calls:
                name = call["name"]
                used.append(name)
                yield {"type": "tool", "name": name, "label": tools.label(name)}
                result = tools.execute(name, call["args"])
                proposal = result.get("proposal") if isinstance(result, dict) else None
                if proposal:
                    yield {"type": "action", "action": {"kind": "service_request", **proposal}}
                responses.append({"functionResponse": {"name": name, "response": {"result": result}}})
            contents.append({"role": "user", "parts": responses})
        answer = answer.strip()
        if not answer:
            raise RuntimeError("Gemini trả về câu trả lời rỗng")
        issues = completeness_issues(question, hits, answer) if not used and not attachment else []
        citation_problem = not valid_citations(answer, len(hits))
        if (not used and not attachment and hits
                and (issues or (citation_problem and any(hit.passage.heading.startswith('CTĐT ') for hit in hits)))):
            # Give a source-backed draft one correction for citation/completeness
            # defects. Validate the correction again; never patch facts silently.
            contents.extend([
                {'role': 'model', 'parts': [{'text': answer}]},
                {'role': 'user', 'parts': [{'text':
                    'Bản nháp cần sửa. ' + ' '.join(issues) +
                    ' Trả lời lại câu hỏi gốc CHỈ từ nguồn đã cấp. '
                    'Chỉ được dùng các số nguồn: ' + ', '.join(f'[{i}]' for i in range(1, len(hits) + 1)) + '. '
                    'Số Phần/Chương trong tài liệu không phải số trích dẫn. '
                    'Không lấy bản nháp làm bằng chứng; nếu nguồn thiếu ý nào, nói rõ ý đó.'}]},
            ])
            yield {'type': 'replace', 'text': ''}
            answer, started = '', False
            splitter = FollowUpFilter()
            for kind, value in stream_turn(contents, api_key, None):
                if kind == 'text':
                    text = splitter.feed(value)
                    if text:
                        started, answer = True, answer + text
                        yield {'type': 'delta', 'text': text}
            leftover, follow_ups = splitter.finish()
            if leftover:
                started, answer = True, answer + leftover
                yield {'type': 'delta', 'text': leftover}
            answer = answer.strip()
        cited = _cited(answer, len(hits))
        if not used and not attachment and completeness_issues(question, hits, answer):
            raise Ungrounded
        if not used and not attachment and (not hits or not valid_citations(answer, len(hits))):
            raise Ungrounded
    except Ungrounded:
        yield from _fallback(search_query, [], None, replace=started, lang=lang)
        return
    except RuntimeError as exc:
        failure = api_error(exc)
        message = FAILURE_TEXT[lang][failure.code]
        if attachment:
            message = ATTACHMENT_FAILED[lang] + ' ' + message
        if failure.retry_after is not None:
            message += (f' Thử lại sau khoảng {failure.retry_after} giây.' if lang == 'vi'
                        else f' Retry in about {failure.retry_after} seconds.')
        if started:
            yield {'type': 'replace', 'text': ''}
        yield {'type': 'delta', 'text': message}
        yield {'type': 'done', 'mode': 'unavailable', 'warning': message,
               'error': {'code': failure.code, 'message': message, 'retry_after': failure.retry_after},
               'tools': list(dict.fromkeys(used)), 'cited': [], 'needs_human': False, 'lang': lang, 'follow_ups': []}
        return
    yield {"type": "done", "mode": "gemini", "warning": None, "tools": list(dict.fromkeys(used)),
           "follow_ups": follow_ups or (derive_follow_ups(hits) if cited else []), "cited": cited,
           "needs_human": False, "lang": lang}
