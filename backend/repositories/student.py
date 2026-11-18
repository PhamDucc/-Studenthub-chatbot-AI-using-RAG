"""Demo student data for the assistant's tools.

Mirrors web/lib/data.ts and the finance page. Replace the module-level
constants with calls to the real student-information API when it exists.
"""

STUDENT = {
    "name": "Nguyễn Minh Anh", "student_id": "22021234", "faculty": "Khoa Công nghệ Thông tin",
    "major": "Khoa học Máy tính", "class": "K67-CA-CLC2", "program": "Chất lượng cao",
    "advisor": "TS. Trần Văn Hùng", "status": "Đang học", "semester": "Học kỳ I, năm học 2026–2027",
    "gpa": 3.52, "credits_earned": 98, "credits_required": 150, "ranking": "Giỏi",
    "conduct_score": {"class_monitor": 84, "advisor": 82, "final": 82, "rating": "Tốt"},
}

ACADEMIC_RECORDS = [
    {"semester": "HK I 2022–2023", "gpa": 3.21, "credits": 18},
    {"semester": "HK II 2022–2023", "gpa": 3.38, "credits": 20},
    {"semester": "HK I 2023–2024", "gpa": 3.55, "credits": 19},
    {"semester": "HK II 2023–2024", "gpa": 3.62, "credits": 21},
    {"semester": "HK I 2025–2026", "gpa": 3.68, "credits": 20},
]

CURRENT_COURSES = [
    {"code": "INT3401", "name": "Trí tuệ nhân tạo", "credits": 3},
    {"code": "INT3306", "name": "Phát triển ứng dụng Web", "credits": 3},
    {"code": "INT3110", "name": "Phân tích và thiết kế hướng đối tượng", "credits": 3},
    {"code": "INT3209", "name": "Khai phá dữ liệu", "credits": 3},
    {"code": "INT3117", "name": "Kiểm thử và đảm bảo chất lượng phần mềm", "credits": 3},
    {"code": "PHI1002", "name": "Chủ nghĩa xã hội khoa học", "credits": 2},
]

# day: 0 = Thứ 2 ... 5 = Thứ 7; period 1 starts 07:00, each period is 50 minutes.
TIMETABLE = [
    {"code": "INT3401", "name": "Trí tuệ nhân tạo", "room": "301-G2", "lecturer": "PGS.TS. Lê Thanh Hà", "day": 0, "start": 1, "periods": 3, "type": "Lý thuyết"},
    {"code": "INT3306", "name": "Phát triển ứng dụng Web", "room": "208-E3", "lecturer": "TS. Hoàng Xuân Tùng", "day": 0, "start": 7, "periods": 2, "type": "Lý thuyết"},
    {"code": "INT3110", "name": "Phân tích và thiết kế hướng đối tượng", "room": "102-G2", "lecturer": "TS. Đặng Đức Hạnh", "day": 1, "start": 2, "periods": 3, "type": "Lý thuyết"},
    {"code": "INT3306", "name": "Phát triển ứng dụng Web", "room": "PM 207-G2", "lecturer": "ThS. Nguyễn Văn Nam", "day": 1, "start": 8, "periods": 3, "type": "Thực hành"},
    {"code": "INT3209", "name": "Khai phá dữ liệu", "room": "309-GĐ3", "lecturer": "TS. Trần Mai Vũ", "day": 2, "start": 1, "periods": 2, "type": "Lý thuyết"},
    {"code": "INT3401", "name": "Trí tuệ nhân tạo", "room": "PM 313-G2", "lecturer": "ThS. Phạm Thu Trang", "day": 2, "start": 7, "periods": 2, "type": "Thực hành"},
    {"code": "INT3117", "name": "Kiểm thử và đảm bảo chất lượng phần mềm", "room": "205-E3", "lecturer": "PGS.TS. Phạm Ngọc Hùng", "day": 3, "start": 3, "periods": 3, "type": "Lý thuyết"},
    {"code": "PHI1002", "name": "Chủ nghĩa xã hội khoa học", "room": "Hội trường G2", "lecturer": "TS. Vũ Thị Lan", "day": 4, "start": 1, "periods": 2, "type": "Lý thuyết"},
    {"code": "INT3209", "name": "Khai phá dữ liệu", "room": "PM 208-G2", "lecturer": "ThS. Lê Hoàng Quân", "day": 4, "start": 8, "periods": 2, "type": "Thực hành"},
    {"code": "INT3110", "name": "Phân tích và thiết kế hướng đối tượng", "room": "102-G2", "lecturer": "TS. Đặng Đức Hạnh", "day": 5, "start": 2, "periods": 2, "type": "Lý thuyết"},
]

CHARGES = [
    {"semester": "Học kỳ I · 2026–2027", "name": "Học phí học kỳ I", "amount": 22_000_000, "paid": False},
    {"semester": "Học kỳ I · 2026–2027", "name": "Phí bảo hiểm y tế", "amount": 683_100, "paid": True},
    {"semester": "Học kỳ II · 2025–2026", "name": "Học phí học kỳ II", "amount": 22_000_000, "paid": True},
]
TUITION_DEADLINE = "31/10/2026"

REQUEST_HISTORY = [
    {"id": "DV-2026-0412", "type": "Giấy xác nhận sinh viên", "submitted_at": "14/10/2026", "status": "Hoàn thành", "copies": 2},
    {"id": "DV-2026-0388", "type": "Bảng điểm (bản sao có dấu)", "submitted_at": "02/10/2026", "status": "Đã duyệt", "copies": 1},
    {"id": "DV-2026-0217", "type": "Đơn phúc khảo bài thi", "submitted_at": "18/07/2026", "status": "Từ chối", "copies": 1},
]

REQUEST_TYPES = {
    "xac-nhan-sv": {"label": "Giấy xác nhận sinh viên", "fee": "Miễn phí", "days": "2 ngày làm việc"},
    "bang-diem": {"label": "Bảng điểm (bản sao có dấu)", "fee": "20.000đ / bản", "days": "3 ngày làm việc"},
    "hoan-thi": {"label": "Đơn xin hoãn thi", "fee": "Miễn phí", "days": "5 ngày làm việc"},
    "nghi-hoc": {"label": "Đơn xin nghỉ học tạm thời", "fee": "Miễn phí", "days": "7 ngày làm việc"},
    "phuc-khao": {"label": "Đơn phúc khảo bài thi", "fee": "30.000đ / môn", "days": "10 ngày làm việc"},
    "mien-giam": {"label": "Đơn miễn giảm học phí", "fee": "Miễn phí", "days": "10 ngày làm việc"},
}

ANNOUNCEMENTS = [
    {"category": "Đào tạo", "title": "Thông báo lịch đăng ký học phần học kỳ II năm học 2026–2027", "date": "20/10/2026", "important": True},
    {"category": "Tài chính", "title": "Hạn cuối nộp học phí học kỳ I: 31/10/2026", "date": "18/10/2026", "important": True},
    {"category": "Khảo thí", "title": "Lịch thi giữa kỳ các học phần khối ngành Công nghệ Thông tin", "date": "15/10/2026", "important": False},
    {"category": "Công tác SV", "title": "Mở đơn xét học bổng khuyến khích học tập học kỳ II năm 2025–2026", "date": "12/10/2026", "important": False},
    {"category": "Sự kiện", "title": "UET Tech Day 2026 – Ngày hội công nghệ và việc làm", "date": "10/10/2026", "important": False},
]
