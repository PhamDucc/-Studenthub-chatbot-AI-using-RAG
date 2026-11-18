"""Resolve conversation controls before routing a knowledge question."""

from dataclasses import dataclass
import re

from ..models import ConversationTurn
from .intent import classify, language_only_request
from .lang import conversation_language, requested_language, resolve_language
from .retrieval import normalize


_REPEAT_WORDS = set((
    "va hay vui long lam on xin ban toi minh em m t tao cua ay do lai tra loi cau hoi "
    "phan hoi nhac lap laplai ban nay luc nay hoi truoc vua roi do di nhe nha giup ho "
    "cho cu the mot lan nua tieng viet anh en vi bang sang "
    "please can could would you answer reply respond repeat rephrase say tell that this "
    "it again my the previous last earlier question response in english vietnamese me and"
).split())
_REPEAT_REFERENCE = re.compile(
    r"\b(?:(?:cau hoi|cau tra loi).*(?:ban nay|luc nay|truoc|vua|hoi roi)|"
    r"(?:previous|last|earlier) (?:question|answer|response)|"
    r"repeat (?:that|this|it)|say (?:that|it) again)\b"
)


def repeat_request(question: str) -> bool:
    """Recognize a request to repeat, without swallowing a new subject."""
    text = normalize(question)
    words = set(re.findall(r"[a-z]+", text))
    return bool(_REPEAT_REFERENCE.search(text)) and words <= _REPEAT_WORDS


def _translation_request(question: str) -> bool:
    text = normalize(question)
    words = set(re.findall(r"[a-z]+", text))
    return (bool(re.match(r"^(?:(?:please|vui long|lam on|hay)\s+)*(?:dich|translate)\b", text))
            and requested_language(question) is not None
            and words <= _REPEAT_WORDS | {"dich", "translate", "into", "to"})


def _control_request(question: str) -> bool:
    return language_only_request(question) or repeat_request(question) or _translation_request(question)


def _substantive_question(question: str) -> str:
    # Preserve the actual question after an inline language instruction.
    parts = re.split(r"[:：]", question, maxsplit=1)
    if len(parts) == 2 and parts[1].strip() and language_only_request(parts[0]):
        return parts[1].strip()
    return question


def _question_history(history: list[ConversationTurn]) -> list[ConversationTurn]:
    """Remove control exchanges so they cannot become retrieval context."""
    result: list[ConversationTurn] = []
    keep_answer = False
    for turn in history:
        if turn.role == "user":
            keep_answer = (not _control_request(turn.content)
                           and classify(turn.content).reply is None)
            if keep_answer:
                result.append(ConversationTurn("user", _substantive_question(turn.content)))
        elif keep_answer:
            result.append(turn)
    return result


@dataclass(frozen=True)
class ResolvedQuestion:
    question: str
    history: list[ConversationTurn]
    language: str
    preference: str | None
    reply: str | None = None


def resolve_question(question: str, history: list[ConversationTurn],
                     response_language: str | None = None, *, has_attachment: bool = False) -> ResolvedQuestion:
    language = resolve_language(question, history, response_language)
    preference = conversation_language(question, history, response_language)
    meaningful = _question_history(history)
    original_intent = classify(question, language)
    if original_intent.kind == "blocked":
        return ResolvedQuestion(question, meaningful, language, preference, original_intent.reply)

    language_control = language_only_request(question)
    repeat = repeat_request(question)
    translation = _translation_request(question)
    if not has_attachment and (language_control or repeat or translation):
        previous_index = next((i for i in range(len(meaningful) - 1, -1, -1)
                               if meaningful[i].role == "user"), None)
        if previous_index is not None:
            # Answer the earlier question afresh; its old answer is not evidence.
            return ResolvedQuestion(meaningful[previous_index].content, meaningful[:previous_index],
                                    language, preference)
        if translation:
            reply = ("Bạn gửi lại nội dung cần dịch nhé."
                     if language == "vi" else "Please send the text you would like translated.")
        elif repeat:
            reply = ("Mình chưa thấy câu hỏi trước đó trong ngữ cảnh hiện có. Bạn gửi lại câu hỏi nhé."
                     if language == "vi" else
                     "I can't see the earlier question in the available conversation. Please send it again.")
        else:
            reply = ("Được nhé, mình sẽ trả lời bằng tiếng Việt. Bạn muốn hỏi gì?"
                     if language == "vi" else
                     "Sure, I'll reply in English. What would you like to ask?")
        return ResolvedQuestion(question, meaningful, language, preference, reply)
    return ResolvedQuestion(_substantive_question(question), meaningful, language, preference)
