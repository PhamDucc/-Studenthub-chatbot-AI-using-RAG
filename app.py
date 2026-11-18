"""Student Hub UET: standalone Python demo. Run with streamlit run app.py."""

from __future__ import annotations

from datetime import datetime
import html

import streamlit as st

from demo_data import (
    ANNOUNCEMENTS,
    CHARGES,
    CLASSES,
    FAQS,
    REQUEST_TYPES,
    STUDENT,
    TRAINING_CRITERIA,
)
from backend.services.chat import answer_question
from backend.config import DATA_DIR
from backend.repositories.documents import load_passages


st.set_page_config(page_title="Student Hub UET · Python demo", page_icon="🎓", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1250px;}
    [data-testid="stSidebar"] {background: #122b55;}
    [data-testid="stSidebar"] * {color: #f4f7ff;}
    [data-testid="stSidebar"] label {color: #e9efff !important;}
    .demo-banner {background:#eef4ff; border:1px solid #c7d8f5; border-radius:12px;
        padding:11px 14px; color:#244677; margin-bottom:1.4rem; font-size:.9rem;}
    .hero {background:linear-gradient(115deg,#163b77,#22549c); color:white; border-radius:16px;
        padding:28px 30px; margin-bottom:1.5rem;}
    .hero h2 {color:white; margin:0 0 5px;}
    .hero p {margin:0; opacity:.85;}
    .section-title {font-size:1.05rem; font-weight:700; margin:1rem 0 .55rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    st.session_state.setdefault("charges", [dict(item) for item in CHARGES])
    st.session_state.setdefault("requests", [])
    st.session_state.setdefault("training_draft", None)
    st.session_state.setdefault("training_submitted", None)
    st.session_state.setdefault("chat", [])


def money(value: int) -> str:
    return f"{value:,.0f}".replace(",", ".") + " đ"


def title(text: str, caption: str) -> None:
    st.title(text)
    st.caption(caption)


def dashboard() -> None:
    st.markdown(
        f'<div class="hero"><h2>Xin chào, {html.escape(STUDENT["name"])} 👋</h2>'
        f'<p>{html.escape(STUDENT["semester"])} · {html.escape(STUDENT["class"])}</p></div>',
        unsafe_allow_html=True,
    )
    debt = sum(item["amount"] for item in st.session_state.charges if not item["paid"])
    a, b, c, d = st.columns(4)
    a.metric("GPA tích lũy", f'{STUDENT["gpa"]:.2f}/4.00')
    b.metric("Tín chỉ tích lũy", f'{STUDENT["credits"]}/{STUDENT["total_credits"]}')
    c.metric("Môn học kỳ này", "6")
    d.metric("Khoản chưa thanh toán", money(debt))
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Lịch học mẫu")
        for day, time, code, name, room in CLASSES[:4]:
            st.markdown(f"**{day} · {time}** — {name} (`{code}`) · {room}")
    with right:
        st.subheader("Thông báo mẫu")
        for category, message, date in ANNOUNCEMENTS:
            st.markdown(f"**{category}** · {message}  ")
            st.caption(date)


def profile() -> None:
    title("Thông tin sinh viên", "Hồ sơ minh họa dùng chung trong bản demo")
    left, right = st.columns(2)
    fields = [
        ("Họ và tên", STUDENT["name"]), ("Mã sinh viên", STUDENT["id"]),
        ("Email", STUDENT["email"]), ("Khoa", STUDENT["faculty"]),
        ("Ngành", STUDENT["major"]), ("Lớp", STUDENT["class"]),
        ("Học kỳ", STUDENT["semester"]), ("Tình trạng", "Đang học (mẫu)"),
    ]
    for i, (label, value) in enumerate(fields):
        with (left if i % 2 == 0 else right):
            st.text_input(label, value=value, disabled=True)
    st.subheader("Tiến độ học tập")
    st.progress(STUDENT["credits"] / STUDENT["total_credits"])
    st.caption(f'{STUDENT["credits"]} / {STUDENT["total_credits"]} tín chỉ · GPA {STUDENT["gpa"]:.2f}')


def schedule() -> None:
    title("Lịch học", "Lịch minh họa của học kỳ I năm học 2026–2027")
    day = st.selectbox("Lọc theo ngày", ["Cả tuần", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"])
    rows = [
        {"Ngày": d, "Giờ": time, "Mã môn": code, "Học phần": name, "Phòng": room}
        for d, time, code, name, room in CLASSES if day == "Cả tuần" or d == day
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("Lịch này được lấy từ dữ liệu mẫu trong demo_data.py.")


def finance() -> None:
    title("Tài chính", "Các khoản phí và thanh toán đều là mô phỏng")
    charges = st.session_state.charges
    total = sum(item["amount"] for item in charges)
    paid = sum(item["amount"] for item in charges if item["paid"])
    a, b, c = st.columns(3)
    a.metric("Tổng khoản phí mẫu", money(total))
    b.metric("Đã thanh toán mẫu", money(paid))
    c.metric("Còn lại", money(total - paid))
    st.subheader("Các khoản phí")
    for item in charges:
        left, middle, right = st.columns([3, 2, 1])
        left.markdown(f'**{item["name"]}** · `{item["id"]}`')
        middle.write(money(item["amount"]))
        if item["paid"]:
            right.success("Đã trả", icon="✅")
        elif right.button("Giả lập đã trả", key=f'pay-{item["id"]}'):
            item["paid"] = True
            st.rerun()
    st.info("Nút thanh toán chỉ đổi trạng thái trong phiên demo; không tạo QR hay giao dịch ngân hàng.")


def training() -> None:
    title("Điểm rèn luyện", "Phiếu tự đánh giá mẫu, lưu trong phiên trình duyệt")
    st.caption("Các tiêu chí và điểm dưới đây chỉ dùng để trình diễn giao diện.")
    score = 0
    with st.form("training_form"):
        for group, items in TRAINING_CRITERIA.items():
            st.subheader(group)
            for label, points in items:
                key = f"criterion-{group}-{label}"
                if st.checkbox(f"{label} (+{points} điểm)", key=key):
                    score += points
        evidence = st.file_uploader("Minh chứng (tùy chọn)", type=["pdf", "jpg", "jpeg", "png"])
        a, b = st.columns(2)
        save = a.form_submit_button("Lưu nháp")
        submit = b.form_submit_button("Gửi đánh giá mẫu", type="primary")
    st.metric("Tổng điểm tự đánh giá", f"{min(score, 100)}/100")
    if save or submit:
        record = {"score": min(score, 100), "evidence": evidence.name if evidence else None}
        if save:
            st.session_state.training_draft = record
            st.success("Đã lưu nháp trong phiên demo.")
        else:
            st.session_state.training_submitted = record
            st.success("Đã ghi nhận phiếu đánh giá mẫu trong phiên demo.")
    if st.session_state.training_submitted:
        st.caption(f'Phiếu đã gửi: {st.session_state.training_submitted["score"]}/100 điểm')


def services() -> None:
    title("Đơn từ & dịch vụ", "Yêu cầu mẫu được lưu trong phiên demo")
    with st.form("request_form", clear_on_submit=True):
        kind = st.selectbox("Loại yêu cầu", list(REQUEST_TYPES))
        st.caption(REQUEST_TYPES[kind])
        a, b = st.columns(2)
        a.text_input("Họ và tên", STUDENT["name"], disabled=True)
        b.text_input("Mã sinh viên", STUDENT["id"], disabled=True)
        copies = st.number_input("Số bản", min_value=1, max_value=10, value=1)
        delivery = st.selectbox("Hình thức nhận", ["Nhận trực tiếp", "Bản mềm qua email", "Gửi qua bưu điện"])
        reason = st.text_area("Lý do / mục đích sử dụng")
        attachment = st.file_uploader("Minh chứng (tùy chọn)", type=["pdf", "jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Gửi yêu cầu mẫu", type="primary")
    if submitted:
        if len(reason.strip()) < 10:
            st.error("Vui lòng mô tả lý do ít nhất 10 ký tự.")
        elif attachment and attachment.size > 5 * 1024 * 1024:
            st.error("Tệp minh chứng cần nhỏ hơn 5 MB.")
        else:
            request_id = f"DEMO-{len(st.session_state.requests) + 1:04d}"
            st.session_state.requests.insert(0, {
                "Mã đơn": request_id, "Loại": kind, "Số bản": int(copies),
                "Hình thức nhận": delivery, "Trạng thái": "Đang xử lý (mẫu)",
                "Thời gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
            })
            st.success(f"Đã tạo yêu cầu mẫu {request_id}.")
    st.subheader("Lịch sử trong phiên")
    if st.session_state.requests:
        st.dataframe(st.session_state.requests, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có yêu cầu nào trong phiên này.")


def faq() -> None:
    title("Câu hỏi thường gặp", "Các câu trả lời ngắn; chatbot có thể tra cứu tài liệu đầy đủ")
    query = st.text_input("Tìm câu hỏi", placeholder="Học phí, phúc khảo, học bổng...").casefold().strip()
    categories = ["Tất cả", *sorted({row[0] for row in FAQS})]
    selected = st.selectbox("Chủ đề", categories)
    filtered = [row for row in FAQS if (selected == "Tất cả" or row[0] == selected)
                and (not query or query in (row[1] + " " + row[2]).casefold())]
    for category, question, response in filtered:
        with st.expander(f"{question} · {category}"):
            st.write(response)
    if not filtered:
        st.info("Không tìm thấy câu hỏi phù hợp.")


def chat() -> None:
    title("Trợ lý UET · RAG", "Tra cứu sáu tài liệu Markdown trong chatbot/data")
    count = len(load_passages(DATA_DIR))
    st.caption(f"{count} đoạn tài liệu đã được lập chỉ mục trong bộ nhớ khi tìm kiếm.")
    for turn in st.session_state.chat:
        with st.chat_message(turn["role"]):
            st.markdown(turn["text"])
            if turn.get("error"):
                st.warning(f'{turn["error"]} Đã hiển thị trích đoạn nguồn.')
            for index, hit in enumerate(turn.get("hits", []), 1):
                with st.expander(f'[{index}] {hit.passage.source} · {hit.passage.heading}'):
                    st.markdown(hit.passage.text)
    question = st.chat_input("Hỏi về học phí, quy chế, học bổng, thủ tục...")
    if question:
        st.session_state.chat.append({"role": "user", "text": question})
        with st.spinner("Đang tìm trong tài liệu..."):
            result = answer_question(question)
        st.session_state.chat.append({"role": "assistant", "text": result.answer, "hits": result.hits, "error": result.warning})
        st.rerun()
    if st.session_state.chat and st.button("Xóa hội thoại"):
        st.session_state.chat = []
        st.rerun()
    if not st.session_state.chat:
        st.info("Thử hỏi: “Một ngày được tạo mã QR học phí tối đa mấy lần?”")


init_state()
with st.sidebar:
    st.title("🎓 Student Hub UET")
    st.caption("PYTHON DEMO")
    page = st.radio(
        "Điều hướng",
        ["Tổng quan", "Thông tin sinh viên", "Lịch học", "Tài chính", "Điểm rèn luyện",
         "Đơn từ & dịch vụ", "Câu hỏi thường gặp", "Trợ lý UET · RAG"],
    )
    st.divider()
    st.caption(f'{STUDENT["name"]} · {STUDENT["id"]}')

st.markdown(
    '<div class="demo-banner">Bản demo: hồ sơ, lịch học, khoản phí và đơn từ là dữ liệu minh họa. '
    'Thông tin chatbot được tra từ các tệp Markdown trong repo.</div>',
    unsafe_allow_html=True,
)

pages = {
    "Tổng quan": dashboard,
    "Thông tin sinh viên": profile,
    "Lịch học": schedule,
    "Tài chính": finance,
    "Điểm rèn luyện": training,
    "Đơn từ & dịch vụ": services,
    "Câu hỏi thường gặp": faq,
    "Trợ lý UET · RAG": chat,
}
pages[page]()
