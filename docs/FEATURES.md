# Tính năng mới của trợ lý UET AI & hướng dẫn chạy

Tài liệu này liệt kê các tính năng đã thêm vào chatbot (Sprint 1–4), cách bật/dùng từng tính năng, và cách chạy toàn bộ hệ thống.
Chi tiết giao thức API nằm ở [API.md](API.md); cài đặt cơ bản ở [SETUP.md](SETUP.md).

> **Lưu ý trạng thái kiểm chứng.** Backend có 54 unit test (chạy offline, không cần mạng). Các tính năng gọi Gemini
> (streaming, tool calling, đọc ảnh, tiếng Anh, rerank, viết lại truy vấn) đã chạy thử thật ở các Sprint 1–2, nhưng khi
> làm Sprint 3–4 key bị giới hạn quota (HTTP 429) nên một phần chỉ kiểm chứng bằng unit test. Giao diện mới (mic, đọc to,
> đính kèm, thẻ chuyển nhân viên, nút VI/EN) mới qua typecheck và build, nên cần mở trình duyệt thử lại.

---

## 1. Chạy hệ thống

### 1.1 Yêu cầu

- Python 3.10+ (backend chỉ dùng thư viện chuẩn)
- Node.js 18+ và pnpm/npm
- (Khuyến nghị) một **Gemini API key có billing**. Key miễn phí dễ gặp 429, khi đó bot tự quay về chế độ trích xuất từ tài liệu.

### 1.2 Cấu hình `backend/.env`

Backend tự đọc `backend/.env` (file này bị `.gitignore`, không commit). Biến đã `export` trong shell luôn được ưu tiên.

```bash
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash        # tùy chọn
ADMIN_TOKEN=mot-chuoi-bi-mat-dai     # bật trang quản trị (xem mục 5)
```

### 1.3 Khởi động

Terminal 1, từ thư mục gốc dự án:

```bash
source .venv/bin/activate            # nếu dùng venv
python3 -m backend                   # http://127.0.0.1:8000
curl http://127.0.0.1:8000/health
```

Khi khởi động, backend dựng chỉ mục embedding **ở nền** (lần đầu mất ~1 phút do giới hạn quota; sau đó lưu vào
`backend/embeddings_cache.json`). Trong lúc đó và mỗi khi API embedding lỗi, truy xuất tự dùng BM25.

Terminal 2:

```bash
cd web
# Tạo file web/.env.local (không bắt buộc nếu không dùng trang quản trị):
#   ADMIN_TOKEN=cung-chuoi-voi-backend
#   PYTHON_API_URL=http://127.0.0.1:8000     # chỉ cần nếu backend ở địa chỉ khác
pnpm install        # hoặc npm install
pnpm dev            # http://localhost:3000
```

Mở trợ lý đầy đủ tại **`/tro-ly-ai`** (cũng có widget nổi ở mọi trang portal, nhưng widget chưa có các tính năng mới).

### 1.4 Chạy test và eval

```bash
python3 -m unittest backend.tests.test_services      # 54 test, offline, dùng DB tạm
python3 -m backend.eval --no-dense                   # đo truy xuất BM25 (offline, xác định)
python3 -m backend.eval                              # hybrid (cần key; dựng chỉ mục embedding trước)
python3 -m backend.eval --followups                  # đo viết lại truy vấn cho câu hỏi tiếp nối
python3 -m backend.eval --rerank -v                  # thêm LLM rerank (tốn quota)
cd web && npx tsc --noEmit                           # typecheck
```

> `next build` lần đầu có thể dừng với cảnh báo bảo mật phiên bản Next (16.4.0) và gợi ý `next upgrade`; chạy lại
> lần hai thì build bình thường. Nên cân nhắc nâng cấp Next.

---

## 2. Danh sách tính năng

### Sprint 1: trải nghiệm trò chuyện

| Tính năng | Mô tả |
|---|---|
| **Streaming** | Chữ hiện dần theo thời gian thực (SSE `/chat/stream`, proxy `/api/chat/stream`). Nếu Gemini lỗi giữa chừng, câu trả lời được thay bằng bản trích xuất từ tài liệu. |
| **Trích dẫn inline** | `[1]` là chip bấm được, mở panel bên phải với đoạn gốc và câu khớp nhất được tô sáng. |
| **Gợi ý câu hỏi tiếp theo** | 3 chip dưới tin nhắn cuối; Gemini sinh, hoặc suy ra từ các mục tài liệu khác khi offline. |
| **Feedback 👍/👎** | Thumbs-down hỏi lý do (không chính xác, thông tin cũ, thiếu ý, không liên quan). Lưu vào SQLite `backend/feedback.db`. |
| **Markdown** | Danh sách, bảng, chữ đậm, code (renderer tự viết, không thêm thư viện). |

### Sprint 2: cá nhân hóa & hành động

| Tính năng | Mô tả |
|---|---|
| **8 tool (function calling)** | Hồ sơ, kết quả học tập, thời khóa biểu, học phí, đơn từ, thông báo, `calc_gpa_scenario`, `propose_service_request`. Dữ liệu là **mock** trong `backend/repositories/student.py` (chép từ `web/lib/data.ts`). |
| **Câu hỏi kết hợp** | Lấy dữ liệu cá nhân từ tool rồi đối chiếu ngưỡng trong quy chế, nêu từng điều kiện đạt/chưa đạt. |
| **Tính toán chính xác** | GPA dự kiến / điểm cần đạt tính bằng code, không để model tự nhẩm. |
| **Thẻ xác nhận đơn** | Bot chỉ *soạn* đơn; đơn chỉ tạo khi bạn bấm "Xác nhận gửi" (idempotent theo `client_id`). Đơn xuất hiện ở trang Đơn từ & Dịch vụ công. |
| **Bước tra cứu** | Chip "Đã tra cứu: Thời khóa biểu…" khi bot đang gọi tool. |
| **Nhắc việc** | Màn hình chào hiện học phí còn nợ, lịch học hôm nay, đơn đang xử lý, thông báo quan trọng. |

"Hôm nay" của dữ liệu demo cố định ở **thứ Hai 19/10/2026** (`DEMO_TODAY`) để khớp dashboard và hạn học phí 31/10.

### Sprint 3: chất lượng truy xuất & an toàn

| Tính năng | Mô tả |
|---|---|
| **Hybrid retrieval** | BM25 + embedding Gemini (`gemini-embedding-001`, 768 chiều) hợp nhất bằng RRF. Tự quay về BM25 khi không có key hoặc API lỗi. |
| **Cổng từ chối câu ngoài lề** | Có dense: cosine tốt nhất < 0.60 thì coi là ngoài phạm vi (trừ khi BM25 khớp từ khóa rất mạnh). Đo được 6/6 câu ngoài lề bị chặn. |
| **Viết lại truy vấn** | Câu tiếp nối ("thế còn D+ thì sao?") được viết lại thành câu độc lập bằng một lời gọi Gemini nhỏ; offline chỉ nối câu trước khi câu quá ngắn. |
| **LLM rerank** (tùy chọn) | `RAG_RERANK=1`: Gemini xếp lại 8 ứng viên đầu. Mặc định tắt, **chưa đo được hiệu quả** do quota. |
| **Định tuyến ý định** | Chào hỏi/cảm ơn/"bạn là ai" trả lời tức thì không tốn truy xuất hay model; câu thuần dữ liệu cá nhân bỏ qua truy xuất; yêu cầu tiêm prompt bị từ chối. |
| **Cache câu trả lời** | Câu quy chế không ngữ cảnh do Gemini trả lời (không dùng tool) được cache 1 giờ; phát lại dưới dạng stream, `done.cached = true`. |
| **Rate limit** | Mặc định 20 yêu cầu/phút/client cho `/chat*`; vượt thì `429` + `Retry-After`. |
| **Che PII** | Email, SĐT, mã sinh viên 8 số, số định danh 12 số bị thay bằng placeholder trước khi lưu feedback/log/ticket. |
| **Bộ eval** | `python -m backend.eval`: 20 câu chuẩn + 22 câu diễn đạt lại (chấm ở mức đoạn theo heading) + 6 câu ngoài lề. |

Số đo đã có (retrieval, paraphrase, mức đoạn): BM25 hit@3 **64%** → hybrid **77%**; hit@1 50% → 55%; MRR 0.60 → 0.68.
Bộ 20 câu chuẩn gần trần (hit@3 100%) nên không phân biệt được cải tiến.

### Sprint 4: đa phương thức, vận hành, đa ngôn ngữ

| Tính năng | Mô tả |
|---|---|
| **Nhập giọng nói** | Nút mic dùng Web Speech API (`vi-VN` / `en-US`). Cần Chrome/Edge/Safari; Firefox không hỗ trợ nên nút tự ẩn. |
| **Đọc câu trả lời** | Nút loa trên mỗi câu trả lời (bỏ Markdown và `[n]` trước khi đọc). |
| **Đính kèm ảnh/PDF** | PNG/JPEG/WebP/PDF, tối đa 4 MB, gửi inline cho Gemini ("cái này nghĩa là gì?"). Không cần trích dẫn `[n]`, không cache; khi Gemini lỗi sẽ báo "chưa đọc được tệp" thay vì trích quy chế sai chủ đề. |
| **Chuyển nhân viên (handoff)** | Khi không có câu trả lời, hiện thẻ "Gửi cho nhân viên hỗ trợ". Xác nhận → tạo ticket `HT-2026-NNNN`, định tuyến Đào tạo/CTSV/KHTC, tóm tắt hội thoại đã che PII, thông báo qua email/webhook. |
| **Trang quản trị** | `/quan-tri?key=<ADMIN_TOKEN>`: số câu hỏi, tỉ lệ trả lời được, mức hài lòng, độ trễ, câu phổ biến, câu chưa trả lời, từ khóa "nên bổ sung tài liệu", lý do 👎, ticket. |
| **Song ngữ Việt/Anh** | Câu trả lời theo ngôn ngữ của câu hỏi; nút VI/EN đổi giao diện (lưu trong localStorage). |

---

## 3. Bật từng tính năng

### 3.1 Thông báo handoff (email / webhook)

Ticket luôn được lưu. Thông báo gửi qua các kênh đã cấu hình (đặt trong `backend/.env`):

```bash
# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587                  # 25 = không dùng STARTTLS
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=studenthub-bot@uet.example
HANDOFF_EMAIL_DAO_TAO=phongdaotao@example.edu
HANDOFF_EMAIL_CTSV=ctsv@example.edu
HANDOFF_EMAIL_KHTC=khtc@example.edu
HANDOFF_EMAIL_DEFAULT=ctsv@example.edu

# Webhook (Slack/Teams tương thích; Zalo OA cần một cầu nối nhận JSON này)
HANDOFF_WEBHOOK_URL=https://hooks.example.com/...
```

Không cấu hình kênh nào: ticket được lưu với kênh `outbox` (xem ở trang quản trị). Thông báo chỉ gửi **một lần**
cho mỗi ticket (idempotent theo `client_id`); lỗi gửi chỉ ghi log, không làm hỏng ticket.

### 3.2 Trang quản trị

1. Đặt **cùng** `ADMIN_TOKEN` trong `backend/.env` và `web/.env.local`, khởi động lại cả hai.
2. Mở `http://localhost:3000/quan-tri?key=<ADMIN_TOKEN>`.

Không đặt `ADMIN_TOKEN` thì các endpoint `/admin/*` trả 403 và trang hiển thị hướng dẫn cấu hình.
Trang không nằm trong menu điều hướng; ai biết khóa mới vào được. Dữ liệu analytics nằm ở `backend/chatlog.db`.

### 3.3 Hybrid retrieval, rerank, viết lại truy vấn

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `RAG_DENSE` | `1` | `0` = chỉ BM25 (offline, xác định) |
| `RAG_DENSE_MIN` | `0.60` | Ngưỡng cosine để coi là có liên quan |
| `RAG_LEXICAL_STRONG` | `20` | Điểm BM25 đủ mạnh để cứu khi cosine thấp |
| `RAG_RERANK` | `0` | `1` = LLM rerank (thêm 1 lời gọi Gemini/câu hỏi) |
| `RAG_REWRITE` | `1` | `0` = tắt viết lại truy vấn |
| `RAG_TOP_K`, `RAG_MIN_SCORE` | `6`, `1.5` | Số đoạn trả về / ngưỡng BM25 khi không có dense |
| `RATE_LIMIT_PER_MINUTE` | `20` | Giới hạn yêu cầu chat theo client |
| `DEMO_TODAY` | `2026-10-19` | "Hôm nay" của dữ liệu demo cá nhân |

Chỉ mục embedding tự dựng lại khi tài liệu trong `chatbot/data/` đổi. Xóa `backend/embeddings_cache.json` để ép dựng lại.

### 3.4 Nơi lưu dữ liệu (đều bị `.gitignore`)

| File | Nội dung | Biến đổi đường dẫn |
|---|---|---|
| `backend/feedback.db` | Đánh giá 👍/👎 | `FEEDBACK_DB` |
| `backend/requests.db` | Đơn từ gửi qua chat | `REQUESTS_DB` |
| `backend/chatlog.db` | Nhật ký câu hỏi (đã che PII) | `CHATLOG_DB` |
| `backend/tickets.db` | Ticket chuyển nhân viên | `TICKETS_DB` |
| `backend/embeddings_cache.json` | Vector embedding của tài liệu | `EMBED_CACHE` |

---

## 4. Thử nhanh bằng giao diện

Mở `/tro-ly-ai` rồi thử lần lượt:

1. **Streaming + trích dẫn:** "Điều kiện để nhận học bổng khuyến khích học tập là gì?" → bấm chip `[1]`.
2. **Dữ liệu cá nhân:** "Mai mình học gì, phòng nào?" / "Mình còn nợ học phí không?"
3. **Tính toán:** "Học thêm 20 tín thì cần trung bình bao nhiêu để lên GPA 3.6?" (đáp án 3.992)
4. **Hành động:** "Giúp mình xin 2 bản bảng điểm" → bấm "Xác nhận gửi" → kiểm tra ở trang Đơn từ.
5. **Chuyển nhân viên:** hỏi điều không có trong tài liệu, ví dụ "Ký túc xá có cho nuôi mèo không?" → "Gửi cho nhân viên hỗ trợ" → xem ticket ở `/quan-tri`.
6. **Đính kèm:** bấm kẹp giấy, chọn ảnh chụp thông báo, hỏi "cái này nghĩa là gì?".
7. **Giọng nói:** bấm mic, nói câu hỏi; bấm loa để nghe câu trả lời.
8. **Tiếng Anh:** đổi sang EN rồi hỏi "How many times a day can I generate a tuition QR code?".
9. **Chào hỏi / chặn:** "Xin chào", "Bạn là ai?", và "Bỏ qua mọi hướng dẫn trước đó" (bị từ chối, không tốn model).

---

## 5. Giới hạn đã biết

- **Dữ liệu cá nhân là mock** và không có đăng nhập: mọi người đều là "Minh Anh". Cần thay `student.py` bằng API thật và thêm xác thực trước khi dùng thật.
- **Dữ liệu cá nhân được gửi tới Gemini** khi tool được gọi; cân nhắc về quyền riêng tư khi dùng dữ liệu thật.
- **Không có `GEMINI_API_KEY`:** bot chỉ trả lời phần quy chế (trích xuất), không dùng tool, không đọc ảnh/PDF; tiếng Anh chỉ hoạt động tốt khi có chỉ mục embedding.
- **Widget nổi** vẫn dùng `/chat` cũ (không streaming, không tool, không đính kèm); chỉ trang `/tro-ly-ai` có đủ tính năng.
- Tệp đính kèm không được gửi lại ở các lượt sau, chỉ lời giải thích của bot nằm trong lịch sử.
- Rate limit và cache lưu trong bộ nhớ tiến trình: khởi động lại là mất, và không chia sẻ giữa nhiều tiến trình.
- Trang `/quan-tri` bảo vệ bằng một khóa chung trong URL, phù hợp demo/nội bộ, không phải hệ thống phân quyền.
- Retrieval vẫn chưa hoàn hảo: ở bộ paraphrase, hit@1 chỉ khoảng 55%. Rerank và viết lại truy vấn chưa được đo bằng eval.
