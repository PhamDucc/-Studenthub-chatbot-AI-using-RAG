"""Clearly fictional portal data for the standalone Python demo."""

STUDENT = {
    "name": "Nguyễn Minh Anh",
    "id": "22021234",
    "email": "22021234@vnu.edu.vn",
    "faculty": "Khoa Công nghệ Thông tin",
    "major": "Khoa học Máy tính",
    "class": "K67-CA-CLC2",
    "semester": "Học kỳ I · 2026–2027",
    "gpa": 3.52,
    "credits": 98,
    "total_credits": 150,
}

CLASSES = [
    ("Thứ 2", "07:00–09:50", "INT3401", "Trí tuệ nhân tạo", "301-G2"),
    ("Thứ 2", "13:00–14:50", "INT3306", "Phát triển ứng dụng Web", "208-E3"),
    ("Thứ 3", "08:00–10:50", "INT3110", "Phân tích và thiết kế hướng đối tượng", "102-G2"),
    ("Thứ 3", "14:00–16:50", "INT3306", "Phát triển ứng dụng Web (TH)", "PM 207-G2"),
    ("Thứ 4", "07:00–08:50", "INT3209", "Khai phá dữ liệu", "309-GĐ3"),
    ("Thứ 4", "13:00–14:50", "INT3401", "Trí tuệ nhân tạo (TH)", "PM 313-G2"),
    ("Thứ 5", "09:00–11:50", "INT3117", "Kiểm thử và đảm bảo chất lượng", "205-E3"),
    ("Thứ 6", "07:00–08:50", "PHI1002", "Chủ nghĩa xã hội khoa học", "Hội trường G2"),
    ("Thứ 6", "14:00–15:50", "INT3209", "Khai phá dữ liệu (TH)", "PM 208-G2"),
    ("Thứ 7", "08:00–09:50", "INT3110", "Phân tích và thiết kế hướng đối tượng", "102-G2"),
]

ANNOUNCEMENTS = [
    ("Đào tạo", "Thông báo lịch đăng ký học phần học kỳ II năm học 2026–2027", "20/10/2026"),
    ("Tài chính", "Hạn cuối nộp học phí học kỳ I: 31/10/2026", "18/10/2026"),
    ("Khảo thí", "Lịch thi giữa kỳ các học phần khối ngành Công nghệ Thông tin", "15/10/2026"),
    ("Công tác SV", "Mở đơn xét học bổng khuyến khích học tập", "12/10/2026"),
]

CHARGES = [
    {"id": "HP-01", "name": "Học phí học kỳ I", "amount": 22_000_000, "paid": False},
    {"id": "BHYT-01", "name": "Bảo hiểm y tế", "amount": 683_100, "paid": True},
    {"id": "HP-02", "name": "Học phí học kỳ II năm trước", "amount": 22_000_000, "paid": True},
]

REQUEST_TYPES = {
    "Giấy xác nhận sinh viên": "Miễn phí · dự kiến 2 ngày làm việc",
    "Bảng điểm": "Phí mẫu · dự kiến 3 ngày làm việc",
    "Đơn xin hoãn thi": "Miễn phí · dự kiến 5 ngày làm việc",
    "Đơn phúc khảo": "Phí mẫu · dự kiến 10 ngày làm việc",
    "Đơn miễn giảm học phí": "Miễn phí · dự kiến 10 ngày làm việc",
}

TRAINING_CRITERIA = {
    "Ý thức học tập": [("Tham gia đầy đủ hoạt động học tập", 15), ("Hoàn thành nhiệm vụ học tập", 10)],
    "Chấp hành nội quy": [("Chấp hành quy định của trường", 15), ("Tham gia sinh hoạt lớp", 10)],
    "Hoạt động và đóng góp": [("Tham gia hoạt động cộng đồng", 15), ("Tham gia câu lạc bộ", 10)],
    "Quan hệ cộng đồng": [("Hỗ trợ bạn học", 10), ("Giữ gìn môi trường học tập", 10)],
    "Thành tích": [("Có thành tích được ghi nhận", 5)],
}

FAQS = [
    ("Học phí", "Một ngày được tạo mã QR thanh toán tối đa mấy lần?", "Theo tài liệu hiện có, tối đa 5 lần mỗi ngày."),
    ("Thủ tục", "Xin bảng điểm nhận ở đâu?", "Nhận tại Phòng Công tác Sinh viên, Phòng 107 Nhà G2, theo lịch trả kết quả."),
    ("Đào tạo", "Điểm D có thể học cải thiện không?", "Có thể đăng ký học cải thiện theo quy chế; hãy đọc điều kiện và cách tính điểm trong tài liệu gốc."),
    ("Học bổng", "Học bổng xét theo GPA hay điểm rèn luyện?", "Mức xét theo mức thấp hơn giữa kết quả học tập và rèn luyện, cùng các điều kiện liên quan."),
]
