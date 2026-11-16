"""Cheap rule-based routing so trivial or unsafe messages never reach retrieval or the LLM."""

from dataclasses import dataclass
import re
from typing import Literal

from .lang import detect
from .retrieval import normalize

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
    (re.compile(r"^(xin )?chao( ban| ad| admin| bot)?( oi)?$|^(hello|hi|hey|alo|good (morning|afternoon|evening))( there| bot)?$|^chao buoi (sang|chieu|toi)$"), "greeting"),
    (re.compile(r"^(cam on|camon|thanks|thank you|thank|thx)( ban| nhieu| nhe| nha| a| rat nhieu| a lot| so much| very much)*$"), "thanks"),
    (re.compile(r"^(tam biet|bye|bye bye|goodbye|hen gap lai|see you)( ban| nhe| nha| later)*$"), "bye"),
    (re.compile(r"^(ban|bot|ad) (la ai|la gi|ten gi|ten la gi)\b.*|^ban (co the )?(lam|giup) (duoc )?(gi|nhung gi)\b.*|"
                r"^(gioi thieu|huong dan su dung)( ve)?( ban)?$|^(who are you|what are you|what can you do|what do you do)\b.*"), "about"),
]

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
    r"dieu \d+|can (bao nhieu|nhung gi)|toi da|toi thieu)\b"
)


def classify(question: str) -> Intent:
    lang = detect(question)
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
