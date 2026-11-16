"""Tiny Vietnamese/English detector so replies follow the student's language."""

import re

from .retrieval import normalize

_VI_CHARS = re.compile(r"[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]", re.I)
_VI_WORDS = {"la", "cua", "khong", "bao", "nhieu", "minh", "em", "the", "nao", "dau", "gi", "co", "duoc", "can",
             "toi", "ban", "hoc", "phi", "xin", "cho", "va", "nhu", "khi", "sinh", "vien", "diem"}
_AMBIGUOUS = {"the", "can", "co", "xin", "a"}  # real words in both languages
_EN_WORDS = {"ignore", "previous", "instructions", "reveal", "prompt", "system", "the", "is", "are", "what", "how", "do", "does", "can", "i", "my", "to", "a", "an", "of", "for", "when",
             "where", "which", "who", "why", "need", "want", "tuition", "scholarship", "student", "please", "hello",
             "thanks", "thank", "you", "me", "have", "will", "should", "if", "and", "or", "in", "on", "about"}


def detect(text: str) -> str:
    """Return "vi" or "en" (Vietnamese is the default for anything ambiguous)."""
    if _VI_CHARS.search(text):
        return "vi"
    words = re.findall(r"[a-z]+", normalize(text))
    en = sum(w in _EN_WORDS for w in words)
    vi = sum(w in _VI_WORDS and w not in _AMBIGUOUS for w in words)
    return "en" if en > vi and en >= 1 else "vi"


NAME = {"vi": "tiếng Việt", "en": "English"}
