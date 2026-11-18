"""Tiny Vietnamese/English detector so replies follow the student's language."""

import re

from .retrieval import normalize
from ..models import ConversationTurn

_VI_CHARS = re.compile(r"[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]", re.I)
_VI_WORDS = {"la", "cua", "khong", "bao", "nhieu", "minh", "em", "the", "nao", "dau", "gi", "co", "duoc", "can",
             "toi", "ban", "hoc", "phi", "xin", "cho", "va", "nhu", "khi", "sinh", "vien", "diem"}
_AMBIGUOUS = {"the", "can", "co", "xin", "a"}  # real words in both languages
_EN_WORDS = {"ignore", "previous", "instructions", "reveal", "prompt", "system", "the", "is", "are", "what", "how", "do", "does", "can", "i", "my", "to", "a", "an", "of", "for", "when",
             "where", "which", "who", "why", "need", "want", "tuition", "scholarship", "student", "please", "hello",
             "thanks", "thank", "you", "me", "have", "will", "should", "if", "and", "or", "in", "on", "about", "hi", "hey"}

_LANGUAGE = r"(?:tieng\s+)?(?:viet(?:namese)?|vi|anh|english|en)"
_REPLY_REQUEST = re.compile(
    r"\b(?:tra loi|phan hoi|giai thich|noi|viet|dich|answer|respond|reply|write|speak|explain|use|translate|switch to|chuyen sang)"
    r"\s+(?:(?:cho (?:toi|minh|em)|to me)\s+)?"
    r"(?:(?:(?:my |the |your )?(?:previous |last |earlier )?(?:question|answer|response)|"
    r"(?:cau hoi|cau tra loi)(?: (?:ban nay|truoc|vua roi))?)\s+)?"
    r"(?:(?:bang|in|using|sang|to|into)\s+)?"
    rf"(?P<language>{_LANGUAGE})\b"
)
_BARE_REQUEST = re.compile(rf"^\s*(?P<language>{_LANGUAGE})(?:\s+(?:di|nhe|nha|please|thanks))*[.!?]*\s*$")
_ONE_SHOT = re.compile(r"\b(?:translate|dich (?:sang|cau|doan|noi dung|giup|ho)|"
                       r"(?:only|just) this (?:answer|response|question)|for this (?:answer|response|question)|"
                       r"chi (?:cau|lan|phan tra loi) nay)\b")


def _without_quotes(text: str) -> str:
    # A quoted instruction is source text, not a conversational preference.
    text = re.sub(r'"[^"\n]*"|“[^”\n]*”|«[^»\n]*»|`[^`\n]*`', " ", text)
    return re.sub(r"(?<!\w)'[^'\n]+'(?!\w)|‘[^’\n]*’", " ", text)


def requested_language(text: str) -> str | None:
    """Return the last positive request to reply in Vietnamese or English."""
    text = normalize(_without_quotes(text))
    requests: list[str] = []
    matches = list(_REPLY_REQUEST.finditer(text))
    bare = _BARE_REQUEST.fullmatch(text)
    if not matches and bare:
        matches = [bare]
    for match in matches:
        before = text[:match.start()]
        # Don't interpret "don't reply in English" as an English preference.
        if re.search(r"\b(?:dung|khong|do not|dont|don't|not)\s+(?:bao gio\s+)?$", before):
            continue
        clause = re.split(r"[.!?;:,\n]", before)[-1]
        policy = re.search(r"\b(?:quy che|quy dinh|tai lieu|ngon ngu dao tao|bai thi|de thi|students? must|course requires)\b", clause)
        if policy and not re.search(r"\b(?:hay|vui long|lam on|please|can you|could you)\s*$", before):
            continue
        after = text[match.end():]
        # "m trả lời bằng tiếng en tao không hiểu" describes a bad previous
        # reply. It must not override an earlier "trả lời bằng tiếng Việt".
        descriptive = re.search(r"\b(?:m|may|ban|bot|you)\s+(?:(?:dang|da|cu|are|keep)\s+)?$", before)
        complaint = re.match(r"\s*[,;:]?\s*(?:(?:tao|t|toi|minh|em|i)\s+)?(?:khong hieu|(?:do not|dont|don't) understand)\b", after)
        language = match["language"].removeprefix("tieng ").strip()
        language = "vi" if language in ("viet", "vietnamese", "vi") else "en"
        if descriptive and complaint:
            misunderstood = re.match(rf"\s+(?P<language>{_LANGUAGE})\b", after[complaint.end():])
            other = misunderstood["language"].removeprefix("tieng ").strip() if misunderstood else None
            other = ("vi" if other in ("viet", "vietnamese", "vi") else "en") if other else None
            if other is None or other == language:
                continue
        requests.append(language)
    return requests[-1] if requests else None


def conversation_language(question: str, history: list[ConversationTurn] | None = None,
                          previous: str | None = None) -> str | None:
    """Persistent preference; translations and one-answer requests don't change it."""
    for text in [question, *(turn.content for turn in reversed(history or []) if turn.role == "user")]:
        if not _ONE_SHOT.search(normalize(_without_quotes(text))):
            if language := requested_language(text):
                return language
    return previous if previous in ("vi", "en") else None


def resolve_language(question: str, history: list[ConversationTurn] | None = None,
                     fallback_language: str | None = None) -> str:
    """Current explicit preference, then latest user preference, then detection."""
    current = requested_language(question)
    if current:
        return current
    return conversation_language("", history, fallback_language) or detect(question)


def detect(text: str) -> str:
    """Return "vi" or "en" (Vietnamese is the default for anything ambiguous)."""
    if _VI_CHARS.search(text):
        return "vi"
    words = re.findall(r"[a-z]+", normalize(text))
    en = sum(w in _EN_WORDS for w in words)
    vi = sum(w in _VI_WORDS and w not in _AMBIGUOUS for w in words)
    return "en" if en > vi and en >= 1 else "vi"


NAME = {"vi": "tiếng Việt", "en": "English"}
