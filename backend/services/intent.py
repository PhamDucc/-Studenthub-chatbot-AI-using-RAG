"""Cheap rule-based routing so trivial or unsafe messages never reach retrieval or the LLM."""

from dataclasses import dataclass
import re
from typing import Literal

from .lang import detect, requested_language
from .retrieval import normalize
from ..models import ConversationTurn

Kind = Literal["smalltalk", "blocked", "personal", "regulation"]


@dataclass(frozen=True)
class Intent:
    kind: Kind
    reply: str | None = None


REPLIES = {
    "greeting": {
        "vi": "Chào bạn! Mình là trợ lý UET. Mình có thể tra cứu quy chế, học phí, học bổng, thủ tục sinh viên "
              "và xem lịch học, GPA, học phí còn nợ, đơn từ của bạn. Bạn muốn hỏi gì?",
        "en": "Hi! I'm the UET student assistant. I can look up regulations, tuition, scholarships and procedures, "
              "and check your timetable, GPA, outstanding tuition and requests. What would you like to know?",
    },
    "thanks": {"vi": "Không có gì nhé! Cần gì thêm bạn cứ hỏi mình.", "en": "You're welcome! Ask me anything else anytime."},
    "bye": {"vi": "Tạm biệt bạn! Chúc bạn học tốt.", "en": "Goodbye! Good luck with your studies."},
    "about": {
        "vi": "Mình là trợ lý AI của UET. Mình trả lời về quy chế đào tạo, học phí, học bổng, rèn luyện, kỷ luật, thủ tục "
              "hành chính dựa trên tài liệu chính thức (kèm nguồn), và tra cứu lịch học, kết quả học tập, học phí, đơn từ "
              "của riêng bạn. Mình cũng có thể soạn sẵn đơn để bạn xác nhận gửi, đọc ảnh/PDF bạn gửi, và chuyển câu hỏi "
              "khó cho nhân viên hỗ trợ.",
        "en": "I'm UET's AI assistant. I answer questions about regulations, tuition, scholarships, conduct, discipline and "
              "administrative procedures from official documents (with sources), and look up your own timetable, grades, "
              "tuition and requests. I can draft requests for you to confirm, read images/PDFs you send, and hand tough "
              "questions to staff.",
    },
    "blocked": {
        "vi": "Mình không thể làm theo yêu cầu đó. Mình chỉ hỗ trợ thông tin sinh viên UET — "
              "bạn thử hỏi về quy chế, học phí, học bổng hay lịch học của mình nhé.",
        "en": "I can't help with that request. I only support UET student information: try asking about regulations, "
              "tuition, scholarships or your timetable.",
    },
}

_SMALLTALK = [
    (re.compile(r"^(xin )?chao( ban| ad| admin| bot| bro| buddy)?( oi)?$|^(hello|hi|hey|alo|good (morning|afternoon|evening))( there| bot| bro| buddy| friend| mate)?$|^chao buoi (sang|chieu|toi)$"), "greeting"),
    (re.compile(r"^(cam on|camon|thanks|thank you|thank|thx)( ban| bro| buddy| friend| mate| nhieu| nhe| nha| a| rat nhieu| a lot| so much| very much)*$"), "thanks"),
    (re.compile(r"^(tam biet|bye|bye bye|goodbye|hen gap lai|see you)( ban| nhe| nha| later)*$"), "bye"),
    (re.compile(r"^(ban|bot|ad) (la ai|la gi|ten gi|ten la gi)\b.*|^ban (co the )?(lam|giup) (duoc )?(gi|nhung gi)\b.*|"
                r"^(gioi thieu|huong dan su dung)( ve)?( ban)?$|^(who are you|what are you|what can you do|what do you do)\b.*"), "about"),
]

_LANGUAGE_CONTROL_WORDS = set(
    "hay vui long lam on xin tra loi phan hoi giai thich noi viet bang tieng vi en anh english vietnamese "
    "chuyen sang su dung di nhe nha a nua voi giup ho cho toi minh em ban m may tao t do khong hieu vi la "
    "please answer respond reply write speak explain use switch to in using me i you my your do dont don "
    "not understand cant can could would t thanks thank instead only from now on duoc roi oke ok bro buddy "
    "co the tu gio bay thoi ma".split()
)


def language_only_request(question: str) -> bool:
    """A preference command alone can be acknowledged without RAG or Gemini."""
    if requested_language(question) is None:
        return False
    words = set(re.findall(r"[a-z]+", normalize(question)))
    return bool(words) and words <= _LANGUAGE_CONTROL_WORDS


_INJECTION = re.compile(
    r"ignore (all |any |the )?(previous|prior|above)|disregard (the |all )?(previous|above|instructions)|"
    r"system prompt|developer message|reveal (your|the) (prompt|instructions)|jailbreak|\bdan mode\b|"
    r"bo qua (tat ca |moi )?(cac )?(huong dan|chi dan|quy tac|luat)|quen (het )?(cac )?(huong dan|quy tac)|"
    r"(tiet lo|in ra|cho (toi|minh) xem|hien thi) (system )?prompt|(huong dan|chi dan) (he thong|ban dau) cua ban|"
    r"(gia vo|dong vai|ban bay gio la|you are now|pretend (to be|you are)) "
)

_PERSONAL = re.compile(
    r"\b(lich hoc|thoi khoa bieu|tkb|hoc gi|hoc mon gi|con no|dang no|no hoc phi|da dong|han (nop|dong)|"
    r"gpa (cua )?(minh|em|toi)|diem (cua )?(minh|em|toi)|don (tu )?(cua )?(minh|em|toi)|trang thai don|don (da|dang) nop|"
    r"tin chi (cua )?(minh|em|toi)|minh (da )?(hoc|dat|tich luy)|ho so cua (minh|em|toi))\b"
)
_REGULATION = re.compile(
    r"\b(quy dinh|quy che|dieu kien|thu tuc|ho so|muc|cach|huong dan|bao lau|khi nao bi|ky luat|khen thuong|"
    r"dieu \d+|can (bao nhieu|nhung gi)|toi da|toi thieu|xu ly|che tai|hau qua)\b"
)

_TOOL_REQUEST = re.compile(
    r'\b(cua (minh|em|toi|t)|my (gpa|grades|credits|timetable|schedule|tuition|profile|requests)|'
    r'(minh|em|toi|t|i) (da |have |am )?(hoc|tich luy|no|dong|completed|paid|owe)|'
    r'(giup|ho) (minh|em|toi|t) (xin|nop|soan)|'
    r'(xin|nop|soan|request) (\d+ (ban |copies )?)?(bang diem|giay xac nhan|transcript)|'
    r'gpa.*(len|muc tieu|du kien|target)|(len|nang|du kien|target).*gpa|'
    r'(am i|do i|can i).*(eligible|qualify|owe|graduate)|'
    r'(minh|em|toi|t) (co )?(du dieu kien|duoc (xet |nhan )?hoc bong)|'
    r'lich hoc|thoi khoa bieu|tkb|hoc (gi|mon gi))\b'
)


def needs_student_tools(question: str, history: list[ConversationTurn]) -> bool:
    """Keep private data tools for personal/mixed questions, not generic policies."""
    text = normalize(question)
    # Generic policy questions must not become personal-tool-only requests just
    # because they mention debt, discipline or another student-domain term.
    personal_subject = re.search(r'\b(minh|toi|em|tao|my|i)\b|\bcua t\b', text)
    if not personal_subject and re.search(r'\b(quy dinh|quy che|xu ly|che tai|hau qua|dieu kien)\b', text):
        return False
    if _TOOL_REQUEST.search(text) or re.search(r'\b(con no|dang no|no hoc phi|trang thai don)\b', text):
        return True
    # Preserve context for short follow-ups without dragging personal tools into
    # an explicit new question about a regulation or a curriculum.
    followup = r'^(con\b|the (con|thi)\b|vay\b|truong hop do\b|what about\b|and\b)'
    if len(text.split()) <= 7 and re.search(followup, text):
        for turn in reversed(history):
            if turn.role != 'user':
                continue
            previous = normalize(turn.content)
            if _TOOL_REQUEST.search(previous):
                return True
            if len(previous.split()) > 7 or not re.search(followup, previous):
                break
    return False


def classify(question: str, language: str | None = None) -> Intent:
    lang = language if language in ("vi", "en") else detect(question)
    text = re.sub(r"[^\w\s]", " ", normalize(question))
    text = re.sub(r"\s+", " ", text).strip()
    if _INJECTION.search(text + " "):
        return Intent("blocked", REPLIES["blocked"][lang])
    if len(text.split()) <= 8:
        for pattern, key in _SMALLTALK:
            if pattern.match(text):
                return Intent("smalltalk", REPLIES[key][lang])
    if _PERSONAL.search(text) and not _REGULATION.search(text):
        return Intent("personal")
    return Intent("regulation")
