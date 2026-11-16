from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "StudentHub_Business_Proposal_10slides.pptx"

NAVY = RGBColor(10, 27, 52)
BLUE = RGBColor(34, 103, 255)
CYAN = RGBColor(20, 198, 207)
MINT = RGBColor(177, 247, 224)
WHITE = RGBColor(249, 251, 255)
INK = RGBColor(22, 32, 50)
MUTED = RGBColor(94, 108, 132)
PALE = RGBColor(235, 242, 255)
ORANGE = RGBColor(255, 164, 76)
RED = RGBColor(235, 86, 86)


def box(slide, x, y, w, h, fill, radius=True, line=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def text(slide, value, x, y, w, h, size=20, color=INK, bold=False,
         font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = value
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return tb


def rich(slide, runs, x, y, w, h, size=20, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear(); tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    for value, color, bold in runs:
        r = p.add_run(); r.text = value
        r.font.name = "Aptos Display"; r.font.size = Pt(size)
        r.font.bold = bold; r.font.color.rgb = color
    return tb


def title(slide, kicker, headline, sub=None, dark=False):
    base = WHITE if dark else INK
    text(slide, kicker.upper(), 0.7, 0.42, 4.5, 0.25, 10, CYAN if dark else BLUE, True)
    text(slide, headline, 0.7, 0.78, 11.9, 0.72, 27, base, True, "Aptos Display")
    if sub:
        text(slide, sub, 0.72, 1.55, 11.5, 0.55, 13, RGBColor(195, 207, 226) if dark else MUTED)


def footer(slide, n, dark=False):
    text(slide, f"STUDENT HUB  /  BUSINESS PROPOSAL", 0.7, 7.13, 4.2, 0.18, 8,
         RGBColor(154, 170, 195) if dark else MUTED, True)
    text(slide, f"{n:02d}", 12.05, 7.08, 0.55, 0.22, 9,
         RGBColor(154, 170, 195) if dark else MUTED, True, align=PP_ALIGN.RIGHT)


def pill(slide, label, x, y, w, fill=PALE, color=BLUE):
    box(slide, x, y, w, 0.38, fill)
    text(slide, label, x, y+0.02, w, 0.25, 10, color, True, align=PP_ALIGN.CENTER)


def add_notes(slide, note):
    slide.notes_slide.notes_text_frame.text = note


def make_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 1 — Cover
    s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    box(s, 8.7, -0.2, 4.9, 7.9, BLUE, radius=False)
    for i, (lab, yy, col) in enumerate([
        ("Hỏi chính sách", 1.25, WHITE), ("Nộp đơn", 2.23, MINT),
        ("Theo dõi học phí", 3.21, WHITE), ("Xem lịch học", 4.19, MINT)]):
        box(s, 9.25, yy, 3.1, 0.68, col)
        text(s, lab, 9.42, yy+0.20, 2.65, 0.25, 13, NAVY, True)
    pill(s, "HACKATHON PROPOSAL · 10 SLIDES", 0.72, 0.62, 3.15, RGBColor(25, 54, 89), MINT)
    text(s, "STUDENT HUB", 0.72, 1.45, 7.3, 0.95, 42, WHITE, True, "Aptos Display")
    text(s, "Một cửa số cho mọi\nhành trình sinh viên", 0.72, 2.48, 7.35, 1.38, 30, WHITE, True, "Aptos Display")
    text(s, "Tra cứu đúng · Làm thủ tục nhanh · Hỗ trợ 24/7", 0.75, 4.18, 7.3, 0.4, 17, MINT, True)
    text(s, "Từ cổng thông tin phân mảnh thành một trải nghiệm dịch vụ thống nhất — được dẫn đường bởi chatbot có nguồn.", 0.75, 4.78, 7.15, 0.85, 15, RGBColor(198, 212, 234))
    text(s, "12 phút", 0.75, 6.38, 1.2, 0.28, 11, WHITE, True)
    text(s, "Business pitch", 2.05, 6.38, 1.7, 0.28, 11, RGBColor(176, 193, 218))
    add_notes(s, "0:00–0:50 — Mở bằng một câu hỏi: Vì sao sinh viên vẫn phải hỏi bạn bè để làm một thủ tục đã có quy định? Student Hub biến mọi hành trình thành một điểm đến duy nhất.")

    # 2 — Problem
    s = prs.slides.add_slide(blank)
    title(s, "01 · Pain point", "Sinh viên không thiếu thông tin. Họ thiếu một lối đi rõ ràng.", "Thông tin tồn tại, nhưng bị phân mảnh theo phòng ban, file, biểu mẫu và kênh liên hệ.")
    pains = [
        ("01", "Tìm lâu", "Phải dò nhiều trang, tài liệu và nhóm chat để tìm đúng quy định."),
        ("02", "Dễ sai", "Biểu mẫu, điều kiện và hạn xử lý dễ bị hiểu thiếu hoặc dùng nhầm phiên bản."),
        ("03", "Phải chờ", "Câu hỏi lặp lại dồn về cán bộ; hỗ trợ bị giới hạn bởi giờ làm việc."),
    ]
    for i, (num, hd, body) in enumerate(pains):
        x = 0.72 + i*4.18
        box(s, x, 2.35, 3.78, 2.58, WHITE, line=RGBColor(218, 227, 242))
        text(s, num, x+0.22, 2.58, 0.55, 0.35, 13, BLUE, True)
        text(s, hd, x+0.22, 3.08, 3.15, 0.38, 21, INK, True)
        text(s, body, x+0.22, 3.62, 3.18, 0.92, 13, MUTED)
    box(s, 0.72, 5.35, 12.0, 1.05, NAVY)
    rich(s, [("Hệ quả: ", MINT, True), ("trải nghiệm kém cho sinh viên + chi phí phục vụ tăng cho nhà trường.", WHITE, True)], 1.05, 5.68, 11.3, 0.38, 18)
    footer(s, 2)
    add_notes(s, "0:50–2:00 — Nhấn mạnh đây là pain point hai phía. Sinh viên mất thời gian và dễ sai; cán bộ mất năng lực xử lý cho các câu hỏi lặp lại.")

    # 3 — Service gap
    s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    title(s, "02 · Service gap", "Mỗi tác vụ là một điểm chạm. Hiện tại chúng chưa thành một dịch vụ.", dark=True)
    items = [("LỊCH HỌC", "Biết hôm nay học gì"), ("HỌC PHÍ", "Biết phải đóng bao nhiêu"),
             ("ĐƠN TỪ", "Biết cần mẫu nào"), ("RÈN LUYỆN", "Biết còn thiếu tiêu chí gì"),
             ("QUY CHẾ", "Biết điều kiện áp dụng")]
    for i, (a,b) in enumerate(items):
        x = 0.7 + i*2.49
        box(s, x, 2.4, 2.17, 1.55, RGBColor(22, 48, 79))
        text(s, a, x+0.16, 2.67, 1.84, 0.25, 10, CYAN, True, align=PP_ALIGN.CENTER)
        text(s, b, x+0.16, 3.10, 1.84, 0.48, 12, WHITE, True, align=PP_ALIGN.CENTER)
    # arrows and promise
    for x in [1.7, 4.19, 6.68, 9.17, 11.66]:
        text(s, "↓", x, 4.12, 0.25, 0.35, 18, MINT, True, align=PP_ALIGN.CENTER)
    box(s, 2.0, 4.72, 9.35, 1.12, BLUE)
    text(s, "MỘT CỬA SỐ · MỘT NGÔN NGỮ · MỘT HÀNH TRÌNH", 2.2, 5.07, 8.95, 0.35, 19, WHITE, True, align=PP_ALIGN.CENTER)
    text(s, "Cơ hội không phải thêm một kênh hỏi đáp — mà là hợp nhất trải nghiệm phục vụ.", 2.2, 6.22, 8.95, 0.4, 15, RGBColor(192, 208, 230), align=PP_ALIGN.CENTER)
    footer(s, 3, True)
    add_notes(s, "2:00–3:00 — Chuyển từ vấn đề sang cơ hội: năm nhu cầu không nên là năm hành trình rời rạc. Giá trị lớn nhất là service orchestration, chatbot là giao diện đơn giản nhất.")

    # 4 — Solution
    s = prs.slides.add_slide(blank)
    title(s, "03 · Giải pháp", "Student Hub = Portal hợp nhất + Trợ lý AI có nguồn", "Một giao diện cho dữ liệu cá nhân, dịch vụ hành chính và tri thức nhà trường.")
    cols = [
        ("01", "HIỂU", "Hỏi bằng ngôn ngữ tự nhiên", "“Điểm D có được học cải thiện?”", BLUE),
        ("02", "TÌM", "Truy xuất đúng quy định", "Từ kho tài liệu đã kiểm soát", CYAN),
        ("03", "LÀM", "Dẫn đến hành động tiếp theo", "Mở đơn · xem phí · theo dõi trạng thái", ORANGE),
    ]
    for i,(n,h,b,ex,c) in enumerate(cols):
        x=0.72+i*4.15
        box(s,x,2.35,3.72,3.28,WHITE,line=RGBColor(213,224,242))
        box(s,x+0.22,2.62,0.62,0.62,c)
        text(s,n,x+0.22,2.79,0.62,0.25,12,WHITE,True,align=PP_ALIGN.CENTER)
        text(s,h,x+1.03,2.67,2.2,0.35,18,INK,True)
        text(s,b,x+0.22,3.52,3.15,0.62,15,INK,True)
        text(s,ex,x+0.22,4.47,3.12,0.52,12,MUTED)
    box(s,1.65,6.0,10.0,0.62,PALE)
    text(s,"Kết quả: từ “tìm thông tin” → “hoàn tất nhu cầu” trong cùng một trải nghiệm.",1.9,6.18,9.5,0.25,15,BLUE,True,align=PP_ALIGN.CENTER)
    footer(s,4)
    add_notes(s, "3:00–4:20 — Giải thích vòng lặp Hiểu–Tìm–Làm. Điểm khác chatbot phổ thông: câu trả lời dựa trên nguồn của trường và nối trực tiếp sang dịch vụ trong portal.")

    # 5 — Journey
    s = prs.slides.add_slide(blank)
    title(s, "04 · Service journey", "Một câu hỏi. Một câu trả lời. Một hành động hoàn tất.", "Ví dụ: sinh viên cần xin bảng điểm.")
    stages=[("1", "HỎI", "“Xin bảng điểm ở đâu?”"), ("2", "TRẢ LỜI", "Địa điểm · phí · SLA · nguồn"),
            ("3", "THỰC HIỆN", "Mở đúng biểu mẫu ngay"), ("4", "THEO DÕI", "Biết trạng thái & ngày trả")]
    for i,(n,h,b) in enumerate(stages):
        x=0.72+i*3.08
        box(s,x,2.5,2.58,2.2,WHITE,line=RGBColor(211,222,240))
        pill(s,n,x+0.18,2.72,0.48,BLUE,WHITE)
        text(s,h,x+0.18,3.24,2.0,0.3,14,BLUE,True)
        text(s,b,x+0.18,3.78,2.15,0.62,13,INK,True)
        if i<3: text(s,"→",x+2.63,3.36,0.38,0.35,20,CYAN,True,align=PP_ALIGN.CENTER)
    box(s,0.72,5.23,12.0,1.0,NAVY)
    text(s,"Giá trị dịch vụ",0.98,5.55,1.55,0.3,12,MINT,True)
    text(s,"Ít bước hơn",3.05,5.55,1.6,0.3,14,WHITE,True)
    text(s,"Ít sai sót hơn",5.25,5.55,1.8,0.3,14,WHITE,True)
    text(s,"Minh bạch hơn",7.7,5.55,1.8,0.3,14,WHITE,True)
    text(s,"Phục vụ 24/7",10.12,5.55,1.8,0.3,14,WHITE,True)
    footer(s,5)
    add_notes(s, "4:20–5:30 — Kể như một demo journey, không sa vào kỹ thuật. Nhấn vào việc chatbot không dừng ở câu trả lời mà giảm số bước để hoàn tất dịch vụ.")

    # 6 — Why works
    s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    title(s, "05 · Why it works", "Chatbot hiệu quả khi được “đóng khung” đúng bài toán", "Không cố biết mọi thứ. Chỉ trả lời trong miền tri thức được nhà trường kiểm soát.", dark=True)
    reasons=[("CÓ NGUỒN", "Truy xuất từ quy chế, học phí, học bổng, thủ tục và liên hệ chính thức."),
             ("ĐÚNG NGỮ CẢNH", "Hiểu câu hỏi tiếng Việt và ưu tiên đoạn văn liên quan nhất."),
             ("LUÔN SẴN SÀNG", "Phản hồi tức thì; vẫn có chế độ trích xuất cục bộ khi không dùng LLM."),
             ("DỄ MỞ RỘNG", "Thêm tài liệu mới mà không phải viết lại toàn bộ luồng sản phẩm.")]
    for i,(h,b) in enumerate(reasons):
        x=0.72+(i%2)*6.15; y=2.35+(i//2)*1.78
        box(s,x,y,5.75,1.38,RGBColor(23,49,80))
        box(s,x+0.18,y+0.22,0.12,0.92,CYAN if i!=2 else ORANGE,radius=False)
        text(s,h,x+0.52,y+0.23,4.8,0.3,14,MINT,True)
        text(s,b,x+0.52,y+0.62,4.8,0.58,12,WHITE)
    text(s,"Nguyên tắc tin cậy: Không tìm thấy nguồn phù hợp → không bịa câu trả lời.",0.75,6.35,11.8,0.35,15,RGBColor(203,217,237),True,align=PP_ALIGN.CENTER)
    footer(s,6,True)
    add_notes(s, "5:30–6:50 — Đây là slide trả lời câu hỏi ‘tại sao chatbot này sẽ hiệu quả’. Nhấn mạnh miền hẹp, có nguồn, fallback và khả năng cập nhật tài liệu.")

    # 7 — Value
    s = prs.slides.add_slide(blank)
    title(s, "06 · Business value", "Tối ưu đồng thời trải nghiệm sinh viên và năng lực vận hành", "Một khoản đầu tư tạo giá trị cho cả hai phía của dịch vụ.")
    box(s,0.72,2.25,5.72,3.75,PALE)
    box(s,6.87,2.25,5.72,3.75,RGBColor(231,250,247))
    text(s,"CHO SINH VIÊN",1.05,2.58,4.8,0.35,14,BLUE,True)
    text(s,"Nhanh hơn",1.05,3.18,2.2,0.4,22,INK,True)
    text(s,"Tự phục vụ bất kỳ lúc nào",1.05,3.62,4.8,0.3,13,MUTED)
    text(s,"Chắc chắn hơn",1.05,4.27,2.5,0.4,22,INK,True)
    text(s,"Câu trả lời đi kèm nguồn và bước tiếp theo",1.05,4.72,4.9,0.48,13,MUTED)
    text(s,"CHO NHÀ TRƯỜNG",7.2,2.58,4.8,0.35,14,RGBColor(0,135,127),True)
    text(s,"Nhẹ tải hơn",7.2,3.18,2.4,0.4,22,INK,True)
    text(s,"Giảm câu hỏi lặp lại ở tuyến đầu",7.2,3.62,4.7,0.3,13,MUTED)
    text(s,"Đo lường được",7.2,4.27,2.5,0.4,22,INK,True)
    text(s,"Biết chủ đề nào đang gây vướng để cải tiến dịch vụ",7.2,4.72,4.85,0.48,13,MUTED)
    text(s,"North Star Metric",0.75,6.4,1.65,0.25,10,BLUE,True)
    text(s,"Tỷ lệ nhu cầu được giải quyết ngay trong phiên đầu tiên",2.55,6.32,8.9,0.38,17,INK,True)
    footer(s,7)
    add_notes(s, "6:50–8:00 — Không cam kết con số khi chưa pilot. Đưa ra North Star Metric: first-contact resolution. Đây là chỉ số nối thẳng trải nghiệm với hiệu quả vận hành.")

    # 8 — Validation metrics
    s = prs.slides.add_slide(blank)
    title(s, "07 · Pilot & KPI", "Chứng minh hiệu quả trong 4 tuần — bằng dữ liệu, không bằng cảm giác", "Pilot với một nhóm dịch vụ có tần suất cao và tài liệu đã chuẩn hóa.")
    weeks=[("TUẦN 1", "Chuẩn hóa nguồn", "Chọn 5 nhóm câu hỏi\n+đặt baseline"),
           ("TUẦN 2", "Pilot giới hạn", "Mời sinh viên dùng\n+ghi nhận truy vấn"),
           ("TUẦN 3", "Tối ưu", "Bổ sung nội dung\n+sửa intent chưa rõ"),
           ("TUẦN 4", "Đánh giá", "So sánh baseline\n+quyết định mở rộng")]
    for i,(w,h,b) in enumerate(weeks):
        x=0.72+i*3.06
        text(s,w,x,2.25,2.55,0.25,10,BLUE,True)
        box(s,x,2.66,2.58,1.62,WHITE,line=RGBColor(210,222,240))
        text(s,h,x+0.18,2.9,2.15,0.3,15,INK,True)
        text(s,b,x+0.18,3.4,2.15,0.55,12,MUTED)
    kpis=[("FCR", "Giải quyết ngay phiên đầu"), ("CSAT", "Hài lòng sau tương tác"),
          ("ESCALATION", "Tỷ lệ cần chuyển cán bộ"), ("ANSWER TIME", "Thời gian tới câu trả lời")]
    for i,(a,b) in enumerate(kpis):
        x=0.72+i*3.06
        box(s,x,4.82,2.58,1.05,NAVY)
        text(s,a,x+0.15,5.06,2.28,0.25,13,MINT,True,align=PP_ALIGN.CENTER)
        text(s,b,x+0.12,5.43,2.34,0.24,10,WHITE,align=PP_ALIGN.CENTER)
    text(s,"Mục tiêu pilot sẽ được chốt sau khi đo baseline — tránh “vanity metrics”.",0.75,6.35,11.8,0.35,14,MUTED,True,align=PP_ALIGN.CENTER)
    footer(s,8)
    add_notes(s, "8:00–9:20 — Trình bày kế hoạch kiểm chứng. KPI không phải số lượt chat; phải là tỷ lệ giải quyết, mức hài lòng, chuyển tuyến và tốc độ.")

    # 9 — Scale / moat
    s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
    title(s, "08 · Scale", "Bắt đầu nhỏ, mở rộng theo giá trị dịch vụ", "Kiến trúc module giúp nâng cấp retrieval hoặc tích hợp hệ thống mà không đổi trải nghiệm người dùng.", dark=True)
    phases=[("NOW", "MVP", "Portal + chatbot\n7 nhóm tài liệu"),
            ("NEXT", "TÍCH HỢP", "SSO · trạng thái đơn\nnotification"),
            ("SCALE", "SERVICE INTELLIGENCE", "Dashboard nhu cầu\nđề xuất chủ động")]
    for i,(tag,h,b) in enumerate(phases):
        x=0.85+i*4.16
        box(s,x,2.5,3.55,2.55,RGBColor(22,48,79))
        pill(s,tag,x+0.25,2.76,1.0,BLUE if i==0 else RGBColor(39,71,105),WHITE)
        text(s,h,x+0.25,3.42,3.0,0.35,17,MINT,True)
        text(s,b,x+0.25,4.02,3.0,0.62,13,WHITE)
        if i<2:text(s,"→",x+3.62,3.48,0.4,0.35,21,CYAN,True,align=PP_ALIGN.CENTER)
    box(s,1.4,5.55,10.55,0.72,BLUE)
    text(s,"Lợi thế tích lũy: kho tri thức sạch + dữ liệu nhu cầu thực + hành trình dịch vụ đã tối ưu",1.67,5.79,10.0,0.3,14,WHITE,True,align=PP_ALIGN.CENTER)
    footer(s,9,True)
    add_notes(s, "9:20–10:35 — Roadmap có kỷ luật: MVP chứng minh nhu cầu, sau đó tích hợp SSO/trạng thái đơn, cuối cùng dùng dữ liệu nhu cầu để cải tiến chủ động.")

    # 10 — Ask
    s = prs.slides.add_slide(blank)
    title(s, "09 · Closing", "Biến mỗi câu hỏi thành một dịch vụ được hoàn tất", "Student Hub giúp sinh viên tự phục vụ tốt hơn, đồng thời trả lại thời gian cho cán bộ xử lý những việc cần con người.")
    box(s,0.72,2.42,7.35,2.72,NAVY)
    text(s,"ĐỀ XUẤT SAU HACKATHON",1.08,2.78,3.4,0.3,12,MINT,True)
    text(s,"Cho phép pilot 4 tuần",1.08,3.42,5.95,0.42,25,WHITE,True)
    text(s,"01 đơn vị đồng hành · 05 nhóm dịch vụ · dữ liệu đã duyệt",1.08,4.15,6.3,0.5,14,RGBColor(200,214,234))
    box(s,8.42,2.42,4.17,2.72,BLUE)
    text(s,"SUCCESS =",8.78,2.83,2.3,0.3,13,MINT,True)
    text(s,"Nhu cầu được\ngiải quyết ngay",8.78,3.39,3.15,0.92,24,WHITE,True)
    text(s,"đo bằng FCR + CSAT",8.78,4.51,3.0,0.3,12,WHITE)
    rich(s,[("STUDENT HUB",BLUE,True),("  —  Hỏi đúng. Làm nhanh. An tâm hơn.",INK,True)],0.75,5.85,11.85,0.55,20,PP_ALIGN.CENTER)
    text(s,"Q&A",5.65,6.55,2.0,0.3,13,MUTED,True,align=PP_ALIGN.CENTER)
    footer(s,10)
    add_notes(s, "10:35–12:00 — Kết bằng ask cụ thể: quyền pilot, một đơn vị đồng hành và dữ liệu được duyệt. Nhắc lại định vị: chatbot chỉ là giao diện; sản phẩm thật là trải nghiệm dịch vụ sinh viên thống nhất.")

    prs.save(OUT)
    print(OUT)


if __name__ == "__main__":
    make_deck()
