"""Function-calling tools: personal student data, calculators, and action proposals.

Every tool is read-only. `propose_service_request` only *prepares* a request;
nothing is filed until the student confirms in the UI (POST /requests).
"""

from datetime import date, timedelta
import uuid

from ..config import DEMO_TODAY
from ..repositories import student as data
from ..repositories.requests import list_requests, validate_request

WEEKDAYS = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]


def today() -> date:
    return date.fromisoformat(DEMO_TODAY)


def today_label() -> str:
    d = today()
    return f"{WEEKDAYS[d.weekday()]}, {d:%d/%m/%Y}"


def _period_time(start: int, periods: int) -> str:
    begin = (7 + start - 1) * 60
    end = (7 + start + periods - 2) * 60 + 50
    return f"{begin // 60:02d}:{begin % 60:02d} – {end // 60:02d}:{end % 60:02d}"


def _day_index(value: str | None) -> list[int]:
    value = (value or "today").strip().lower()
    base = today().weekday()
    named = {"today": base, "hôm nay": base, "hom nay": base, "tomorrow": base + 1, "ngày mai": base + 1,
             "ngay mai": base + 1}
    if value in named:
        return [named[value] % 7]
    if value in ("week", "tuần", "tuan", "all"):
        return list(range(6))
    for index, label in enumerate(WEEKDAYS):
        if value in (label.lower(), str(index + 2), f"t{index + 2}", "cn" if index == 6 else label.lower()):
            return [index]
    return [base]


def get_student_profile() -> dict:
    s = data.STUDENT
    return {k: s[k] for k in ("name", "student_id", "faculty", "major", "class", "program", "advisor", "status", "semester")}


def get_academic_summary() -> dict:
    s = data.STUDENT
    return {
        "gpa_cumulative_scale_4": s["gpa"], "credits_earned": s["credits_earned"],
        "credits_required_to_graduate": s["credits_required"],
        "credits_remaining": s["credits_required"] - s["credits_earned"], "ranking": s["ranking"],
        "latest_completed_semester": data.ACADEMIC_RECORDS[-1],
        "conduct_score": s["conduct_score"], "semester_results": data.ACADEMIC_RECORDS,
        "current_courses": data.CURRENT_COURSES,
        "current_credits": sum(c["credits"] for c in data.CURRENT_COURSES),
    }


def get_timetable(day: str | None = "today") -> dict:
    indexes = _day_index(day)
    sessions = [
        {"day": WEEKDAYS[s["day"]], "time": _period_time(s["start"], s["periods"]), "course": f'{s["code"]} {s["name"]}',
         "type": s["type"], "room": s["room"], "lecturer": s["lecturer"]}
        for s in sorted(data.TIMETABLE, key=lambda s: (s["day"], s["start"])) if s["day"] in indexes
    ]
    label = ", ".join(WEEKDAYS[i] for i in indexes if i < 7) if len(indexes) < 6 else "cả tuần"
    return {"today": today_label(), "requested": label, "sessions": sessions,
            "note": None if sessions else "Không có tiết học."}


def get_tuition_status() -> dict:
    total = sum(c["amount"] for c in data.CHARGES)
    paid = sum(c["amount"] for c in data.CHARGES if c["paid"])
    unpaid = [c for c in data.CHARGES if not c["paid"]]
    deadline = date(2026, 10, 31)
    return {"charges": data.CHARGES, "total_vnd": total, "paid_vnd": paid, "outstanding_vnd": total - paid,
            "unpaid_items": unpaid, "payment_deadline": data.TUITION_DEADLINE,
            "days_until_deadline": (deadline - today()).days}


def get_service_requests() -> dict:
    return {"requests": list_requests(), "available_types": {k: v for k, v in data.REQUEST_TYPES.items()}}


def get_announcements() -> dict:
    return {"announcements": data.ANNOUNCEMENTS}


def calc_gpa_scenario(next_credits: int, target_gpa: float | None = None, expected_avg: float | None = None) -> dict:
    """GPA after `next_credits` more credits, or the average needed to reach `target_gpa`."""
    gpa, credits = data.STUDENT["gpa"], data.STUDENT["credits_earned"]
    if not isinstance(next_credits, (int, float)) or next_credits <= 0:
        return {"error": "next_credits phải > 0"}
    result: dict = {"current_gpa": gpa, "current_credits": credits, "next_credits": next_credits}
    if expected_avg is not None:
        result["projected_gpa"] = round((gpa * credits + expected_avg * next_credits) / (credits + next_credits), 3)
    if target_gpa is not None:
        needed = (target_gpa * (credits + next_credits) - gpa * credits) / next_credits
        result.update(target_gpa=target_gpa, required_average=round(needed, 3),
                      feasible=needed <= 4.0, already_above_target=needed <= 0)
    return result


def propose_service_request(request_type: str, reason: str, copies: int = 1) -> dict:
    """Prepare (not file) a service request for the student to confirm."""
    try:
        request_type, reason, copies = validate_request(request_type, reason, copies)
    except ValueError as exc:
        return {"error": str(exc), "valid_types": list(data.REQUEST_TYPES)}
    info = data.REQUEST_TYPES[request_type]
    return {
        "status": "awaiting_student_confirmation",
        "message": "Đơn đã được soạn nhưng CHƯA gửi. Sinh viên phải bấm 'Xác nhận gửi' trên giao diện.",
        "proposal": {"client_id": uuid.uuid4().hex, "request_type": request_type, "label": info["label"],
                     "fee": info["fee"], "days": info["days"], "reason": reason, "copies": copies},
    }


TOOLS = {
    "get_student_profile": (get_student_profile, "Hồ sơ sinh viên", "Thông tin cá nhân: họ tên, MSSV, khoa, ngành, lớp, cố vấn học tập."),
    "get_academic_summary": (get_academic_summary, "Kết quả học tập", "GPA tích lũy (thang 4), tín chỉ, xếp loại, điểm rèn luyện, điểm từng học kỳ, các học phần đang học."),
    "get_timetable": (get_timetable, "Thời khóa biểu", "Lịch học. Tham số day: 'today', 'tomorrow', 'week', hoặc 'Thứ 2'..'Thứ 7'."),
    "get_tuition_status": (get_tuition_status, "Học phí", "Các khoản phí, đã nộp, còn nợ và hạn nộp học phí."),
    "get_service_requests": (get_service_requests, "Đơn từ đã nộp", "Danh sách đơn đã nộp kèm trạng thái và các loại đơn có thể nộp."),
    "get_announcements": (get_announcements, "Thông báo", "Các thông báo gần đây của nhà trường."),
    "calc_gpa_scenario": (calc_gpa_scenario, "Tính GPA", "Tính chính xác GPA dự kiến hoặc điểm trung bình cần đạt ở N tín chỉ tiếp theo."),
    "propose_service_request": (propose_service_request, "Soạn đơn", "Soạn sẵn đơn dịch vụ cho sinh viên xác nhận. KHÔNG tự gửi."),
}

_SCHEMAS = {
    "get_timetable": {"type": "OBJECT", "properties": {"day": {"type": "STRING"}}},
    "calc_gpa_scenario": {"type": "OBJECT", "properties": {
        "next_credits": {"type": "INTEGER", "description": "Số tín chỉ sẽ học tiếp"},
        "target_gpa": {"type": "NUMBER", "description": "GPA mục tiêu (thang 4)"},
        "expected_avg": {"type": "NUMBER", "description": "Điểm trung bình dự kiến ở các tín chỉ tiếp theo"}},
        "required": ["next_credits"]},
    "propose_service_request": {"type": "OBJECT", "properties": {
        "request_type": {"type": "STRING", "enum": list(data.REQUEST_TYPES)},
        "reason": {"type": "STRING", "description": "Lý do / mục đích, 10-500 ký tự"},
        "copies": {"type": "INTEGER", "description": "Số bản, 1-10"}},
        "required": ["request_type", "reason"]},
}


def declarations() -> list[dict]:
    return [{"name": name, "description": description, **({"parameters": _SCHEMAS[name]} if name in _SCHEMAS else {})}
            for name, (_, _, description) in TOOLS.items()]


def label(name: str) -> str:
    return TOOLS[name][1] if name in TOOLS else name


def execute(name: str, args: dict | None) -> dict:
    if name not in TOOLS:
        return {"error": f"Công cụ không tồn tại: {name}"}
    try:
        return TOOLS[name][0](**(args or {}))
    except TypeError as exc:
        return {"error": f"Tham số không hợp lệ: {exc}"}


def reminders() -> list[dict]:
    """Proactive nudges shown on the chat welcome screen."""
    items: list[dict] = []
    tuition = get_tuition_status()
    if tuition["outstanding_vnd"] > 0:
        items.append({"kind": "finance", "title": f'Còn nợ {tuition["outstanding_vnd"]:,} đ'.replace(",", "."),
                      "detail": f'Hạn nộp học phí {tuition["payment_deadline"]} (còn {tuition["days_until_deadline"]} ngày)',
                      "urgent": tuition["days_until_deadline"] <= 14,
                      "prompt": "Mình còn nợ học phí không? Nộp bằng cách nào?"})
    next_class = get_timetable("today")["sessions"]
    if next_class:
        first = next_class[0]
        items.append({"kind": "class", "title": f'Hôm nay có {len(next_class)} tiết học',
                      "detail": f'{first["time"].split(" – ")[0]} · {first["course"]} · {first["room"]}', "urgent": False,
                      "prompt": "Hôm nay mình học gì, ở phòng nào?"})
    pending = [r for r in list_requests() if r["status"] in ("Đang xử lý", "Đã duyệt")]
    if pending:
        items.append({"kind": "request", "title": f'{len(pending)} đơn đang được xử lý',
                      "detail": f'{pending[0]["type"]} · {pending[0]["status"]}', "urgent": False,
                      "prompt": "Các đơn từ của mình đang ở trạng thái nào?"})
    for note in data.ANNOUNCEMENTS:
        if note["important"] and "học phí" not in note["title"].lower():
            items.append({"kind": "notice", "title": note["category"], "detail": note["title"], "urgent": False,
                          "prompt": f'Cho mình biết chi tiết: {note["title"]}'})
    return items
