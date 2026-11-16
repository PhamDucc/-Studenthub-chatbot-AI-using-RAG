"""Escalate unanswered questions to staff: route to a department, summarise, notify.

Notification channels (all optional; a ticket is always stored):
  * SMTP email:  SMTP_HOST [SMTP_PORT=587] [SMTP_USER SMTP_PASSWORD] SMTP_FROM, plus recipients
                 HANDOFF_EMAIL_<DEPT> (DAO_TAO, CTSV, KHTC) or HANDOFF_EMAIL_DEFAULT
  * Webhook:     HANDOFF_WEBHOOK_URL receives {"text": ..., "ticket": {...}} (Slack/Teams-compatible,
                 or a bridge to Zalo OA)
"""

from email.message import EmailMessage
import json
import logging
import os
import smtplib
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..models import ConversationTurn
from ..repositories import student as student_data
from ..repositories.tickets import create_ticket, set_channel
from .retrieval import normalize
from .safety import redact

DEPARTMENTS = {
    "DAO_TAO": ("Phòng Đào tạo", ("hoc phan", "dang ky", "diem", "thi", "bang diem", "tot nghiep", "hoc vu", "quy che", "tin chi", "chuyen nganh", "thoi hoc", "bao luu")),
    "CTSV": ("Phòng Công tác Sinh viên", ("hoc bong", "ren luyen", "ky luat", "khen thuong", "ky tuc", "tro cap", "the sinh vien", "vay von", "xac nhan sinh vien")),
    "KHTC": ("Phòng Kế hoạch – Tài chính", ("hoc phi", "nop tien", "cong no", "hoan tien", "chuyen khoan", "mien giam")),
}
DEFAULT_DEPARTMENT = "CTSV"


def route_department(text: str) -> str:
    """Pick the department whose keywords appear most often (CTSV when nothing matches)."""
    normalized = normalize(text)
    scores = {key: sum(normalized.count(word) for word in words) for key, (_, words) in DEPARTMENTS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else DEFAULT_DEPARTMENT


def summarize(question: str, history: list[ConversationTurn], limit: int = 6) -> str:
    """Deterministic, PII-redacted transcript summary for staff."""
    lines = [f"Câu hỏi chưa được trả lời: {redact(question.strip())}"]
    recent = history[-limit:]
    if recent:
        lines.append("Hội thoại gần đây:")
        lines += [f"- {'SV' if t.role == 'user' else 'Bot'}: {redact(t.content.strip())[:240]}" for t in recent]
    return "\n".join(lines)


def _email(ticket: dict, text: str) -> str | None:
    host = os.getenv("SMTP_HOST", "").strip()
    to = os.getenv(f"HANDOFF_EMAIL_{ticket['department']}") or os.getenv("HANDOFF_EMAIL_DEFAULT")
    if not host or not to:
        return None
    message = EmailMessage()
    message["Subject"] = f"[{ticket['code']}] Câu hỏi sinh viên cần hỗ trợ"
    message["From"] = os.getenv("SMTP_FROM", "studenthub-bot@localhost")
    message["To"] = to
    message.set_content(text)
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as smtp:
        if os.getenv("SMTP_PORT", "587") != "25":
            smtp.starttls()
        if os.getenv("SMTP_USER"):
            smtp.login(os.environ["SMTP_USER"], os.getenv("SMTP_PASSWORD", ""))
        smtp.send_message(message)
    return "email"


def _webhook(ticket: dict, text: str) -> str | None:
    url = os.getenv("HANDOFF_WEBHOOK_URL", "").strip()
    if not url.startswith(("https://", "http://")):
        return None
    body = json.dumps({"text": text, "ticket": {k: ticket[k] for k in ("code", "department", "question", "status")}},
                      ensure_ascii=False).encode("utf-8")
    with urlopen(Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST"), timeout=10):
        pass
    return "webhook"


def notify(ticket: dict) -> list[str]:
    """Send through every configured channel; failures are logged, never raised."""
    text = (f"Ticket {ticket['code']} · {DEPARTMENTS[ticket['department']][0]}\n"
            f"Sinh viên: {ticket['student']['name']} ({ticket['student']['student_id']}) · {ticket['student']['email']}\n\n"
            f"{ticket['summary']}")
    sent = []
    for channel in (_email, _webhook):
        try:
            if result := channel(ticket, text):
                sent.append(result)
        except (OSError, smtplib.SMTPException, URLError, ValueError) as exc:
            logging.warning("Handoff notification via %s failed: %s", channel.__name__, exc)
    return sent


def open_ticket(client_id: str, question: str, history: list[ConversationTurn]) -> dict:
    """Create the ticket once per client_id, notify staff, and record the channel used."""
    department = route_department(question + " " + " ".join(t.content for t in history[-4:] if t.role == "user"))
    student = {"name": student_data.STUDENT["name"], "student_id": student_data.STUDENT["student_id"],
               "email": f"{student_data.STUDENT['student_id']}@vnu.edu.vn"}
    ticket, created = create_ticket(client_id, department, redact(question.strip()), summarize(question, history), student)
    if created:
        channels = notify(ticket)
        ticket["channel"] = "+".join(channels) or "outbox"
        set_channel(ticket["id"], ticket["channel"])
    ticket["department_name"] = DEPARTMENTS[ticket["department"]][0]
    return ticket
