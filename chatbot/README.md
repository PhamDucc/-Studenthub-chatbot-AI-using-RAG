# STUDENT HUB UET - CHATBOT AI RAG MODULE

Thư mục này chứa toàn bộ tài nguyên dữ liệu tri thức, bộ kịch bản kiểm thử (benchmark) và mã nguồn của hệ thống Chatbot AI RAG (Retrieval-Augmented Generation) phục vụ sinh viên Trường Đại học Công nghệ (UET) - ĐHQGHN.

---

## 1. CẤU TRÚC THƯ MỤC MODULE

```text
chatbot/
├── data/                                             # Kho dữ liệu tri thức sạch (Markdown files)
│   ├── Quy_che_dao_tao.md                            # Quy chế đào tạo bậc đại học (QĐ 3626)
│   ├── Quy_dinh_ve_hoc_phi.md                        # Học phí, quét mã QR, miễn giảm & trợ cấp xã hội
│   ├── Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md # 19 thủ tục hành chính trực tuyến
│   ├── Hoc_bong_va_diem_ren_luyen.md                 # Học bổng KKHT (QĐ 1931), ngoài ngân sách & ĐRL
│   ├── Khen_thuong_ky_luat.md                        # Khen thưởng thi đua, xóa kỷ luật & khung 13 vi phạm
│   └── Thong_tin_lien_he_voi_nha_truong.md           # Danh bạ phòng ban, hotline & bảng tra cứu một cửa
├── tests/
│   └── benchmark_qa.md                               # Bộ 20 test cases kiểm thử độ chính xác (Ground Truth)
└── README.md                                         # Tài liệu mô tả dữ liệu và hướng dẫn kỹ thuật RAG
```

---

## 2. BẢNG TỔNG HỢP NGUỒN DỮ LIỆU TRI THỨC (KNOWLEDGE BASE)

Toàn bộ dữ liệu đã được số hóa và chuẩn hóa sang định dạng Markdown (`.md`), phân chia ranh giới nội dung rõ ràng nhằm triệt tiêu hiện tượng chồng chéo thông tin (Data Redundancy) khi embedding:

| STT | Tên file | Văn bản căn cứ pháp lý / Nguồn dữ liệu | Miền tri thức chính |
| :---: | :--- | :--- | :--- |
| **1** | `Quy_che_dao_tao.md` | **Quyết định số 3626/QĐ-ĐHQGHN** ngày 21/10/2022 của Giám đốc ĐHQGHN | Cách tính GPA thang 4, điều kiện cảnh báo học vụ, buộc thôi học, quy định học lại/cải thiện D & D+, khối lượng tín chỉ đăng ký, chuẩn đầu ra và điều kiện tốt nghiệp. |
| **2** | `Quy_dinh_ve_hoc_phi.md` | Cổng StudentHub UET, Nghị định 20/2021/NĐ-CP & Nghị định 57/2017/NĐ-CP | Công thức tính tiền học phí, quy trình 3 bước quét mã QR thanh toán trên hệ thống, phân loại định mức học phí các hệ và danh mục miễn/giảm 100%, 70%, 50% cùng trợ cấp XH. |
| **3** | `Cac_thu_tuc_hanh_chinh_va_mau_bieu_cho_sinh_vien.md` | Cổng thông tin một cửa StudentHub UET & Sổ tay người học UET | Hướng dẫn 19 thủ tục dịch vụ công: cấp bảng điểm, giấy xác nhận SV, vay vốn ngân hàng, xin hoãn thi, phúc khảo bài thi, bảo lưu, thôi học, cấp lại thẻ SV, làm vé xe buýt. |
| **4** | `Hoc_bong_va_diem_ren_luyen.md` | **Quyết định số 1931/QĐ-ĐHCN** ngày 07/08/2026 của Hiệu trưởng UET | Tiêu chí xét học bổng KKHT (Xuất sắc/Giỏi/Khá), nguyên tắc lấy mức thấp hơn, học bổng ngoài ngân sách, thang 100 ĐRL, điểm cơ sở 70 và khống chế ĐRL khi bị kỷ luật. |
| **5** | `Khen_thuong_ky_luat.md` | **Quyết định số 32/QĐ-ĐHQGHN** ngày 05/01/2017 của Giám đốc ĐHQGHN | Tiêu chuẩn danh hiệu Sinh viên Giỏi / Xuất sắc cuối năm; thời hạn xóa án kỷ luật (3 tháng với khiển trách, 6 tháng với cảnh cáo); bảng khung kỷ luật 13 nhóm vi phạm (thi hộ, chứng chỉ giả...). |
| **6** | `Thong_tin_lien_he_voi_nha_truong.md` | Trang thông tin chính thức Trường ĐH Công nghệ (UET) | Địa chỉ, số điện thoại, email Phòng CTSV (P.107-G2, P.210-G2), Phòng Đào tạo (P.213-G2) và bảng tra cứu nhanh đầu mối liên hệ theo từng nhu cầu phát sinh. |

---

## 3. KHUYẾN NGHỊ THÔNG SỐ KỸ THUẬT (RAG PIPELINE CONFIGURATION)

Dành cho lập trình viên thiết lập quy trình Vector Database (ChromaDB / FAISS / Qdrant):

### 3.1. Chiến lược cắt đoạn (Chunking Strategy)
* **Phương pháp chia tách ưu tiên:** Sử dụng `MarkdownHeaderTextSplitter` kết hợp với `RecursiveCharacterTextSplitter`.
  * Header Splitter chia nhỏ theo các cấp tiêu đề: `#` (Tên văn bản), `##` (Chương / Phần), `###` (Tên điều / Thủ tục cụ thể).
* **Kích thước đoạn (Chunk size):** `800` – `1200` characters (hoặc ~`200` – `300` tokens). Kích thước này đủ để chứa trọn vẹn 1 điều khoản quy chế hoặc 1 quy trình thủ tục mà không làm đứt gãy ngữ cảnh.
* **Độ gối đầu (Chunk overlap):** `100` – `150` characters để đảm bảo giữ nguyên liên kết ngữ nghĩa giữa hai chunk liền kề.

### 3.2. Cấu trúc Metadata đính kèm (Metadata Schema)
Mỗi document chunk được nạp vào Vector DB cần kèm metadata sau để phục vụ tính năng lọc trước khi truy vấn (pre-filtering):

```json
{
  "source": "chatbot/data/Quy_che_dao_tao.md",
  "doc_title": "Quy chế đào tạo đại học ĐHQGHN",
  "category": "academic_regulations", // academic_regulations | tuition_policy | procedures | scholarships | discipline | contact
  "legal_basis": "3626/QĐ-ĐHQGHN",
  "effective_year": "2022"
}
```

### 3.3. Cấu hình Truy xuất & Sinh câu trả lời (Retrieval & Generation)
* **Số lượng đoạn văn bản lấy ra (Top-K):** Đặt `k = 3` hoặc `k = 4`. Do dữ liệu đã được làm sạch và phân tách độc lập, Top-3 đã đủ bao quát câu trả lời mà không làm loãng prompt.
* **Mô hình AI:** Tích hợp Google Gemini (`gemini-2.5-flash` hoặc `gemini-1.5-pro` qua `google-genai` SDK).
* **Nhiệt độ (Temperature):** Thiết lập `temperature = 0.2` – `0.3` để mô hình trả lời mang tính khách quan, tuân thủ nguyên tắc thực tế (grounded facts) và tránh suy diễn hoặc bịa đặt điều khoản.

---

## 4. QUY TRÌNH KIỂM THỬ ĐỘ CHÍNH XÁC (EVALUATION / BENCHMARK)

Trước khi bàn giao hoặc đẩy lên production, hệ thống RAG cần chạy qua bộ kiểm thử tự động tại file `chatbot/tests/benchmark_qa.md`:
* Bộ kiểm thử gồm **20 Test Cases** đại diện cho các câu hỏi học vụ, tài chính và thủ tục hành chính thực tế.
* Tiêu chí đánh giá hệ thống:
  1. **Retrieval Hit Rate:** Top-K đoạn trích trả về phải chứa đúng nguồn file được chỉ định trong từng Test Case.
  2. **Answer Correctness:** Nội dung sinh ra bởi Gemini phải khớp chính xác với nội dung tại mục `Đáp án chuẩn (Ground Truth)`.
  3. **Keyword Matching:** Câu trả lời bắt buộc phải chứa các từ khóa quy chế đã định danh trong file benchmark.