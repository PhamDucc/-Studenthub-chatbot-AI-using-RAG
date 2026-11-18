# Student Hub UET

Student Hub UET is a demo university student portal and AI assistant built for an academic support experience. The project combines a modern Next.js student portal with a Python retrieval-based chatbot that answers questions from Markdown knowledge documents.

The application is designed for demonstration, internal prototyping, and educational use. It includes demo student data, service forms, timetable and finance screens, and a chat assistant powered by retrieval over a local knowledge base.

## Chạy hằng ngày trên Windows (PowerShell)

Mở **hai terminal** trong VS Code và giữ cả hai chạy khi sử dụng. Các lệnh dưới đây dùng thư mục dự án trên máy hiện tại; nếu chuyển máy, thay đường dẫn cho phù hợp.

### 1. Terminal backend

```powershell
Set-Location 'D:\-Studenthub-chatbot-AI-using-RAG'
& .\.venv\Scripts\python.exe -m backend
```

Backend chạy tại `http://127.0.0.1:8000`. Gọi trực tiếp Python trong môi trường ảo nên không cần activate hay thay đổi Execution Policy.

### 2. Terminal frontend

```powershell
Set-Location 'D:\-Studenthub-chatbot-AI-using-RAG\web'
npm.cmd run dev
```

Dùng `npm.cmd` để tránh lỗi PowerShell chặn thực thi `npm.ps1`. Mở địa chỉ Next.js in trong terminal (mặc định `http://localhost:3000`).

Lệnh `dev` dùng Webpack để tránh vòng lặp biên dịch/tải lại đã gặp khi chạy Turbopack trên máy Windows này. Khi chạy hằng ngày, dùng `npm.cmd run dev` như trên.

- Portal: `http://localhost:3000`
- Trợ lý đầy đủ: `http://localhost:3000/tro-ly-ai` — streaming, nguồn trích dẫn, mic, ảnh/PDF và gửi đơn. Widget nổi chưa có đủ các tính năng này.

**Không cần cài lại thư viện hoặc ingest lại mỗi ngày.** Backend tự nạp tài liệu và dùng lại cache embedding nếu nội dung không đổi.

### 3. Kiểm tra và dừng

Trong một terminal khác, kiểm tra backend:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health'
```

Nhấn **Ctrl+C ở từng terminal backend và frontend** để dừng. Lần sau chạy lại hai nhóm lệnh trên.

### Cấu hình lần đầu hoặc khi chuyển máy

Nếu chưa có môi trường Python, chạy từ thư mục gốc:

```powershell
py -m venv .venv
```

Backend hiện dùng thư viện chuẩn Python, không cần cài dependency ngoài để chạy `-m backend`. Cài frontend lần đầu, hoặc sau khi cập nhật dependency:

```powershell
Set-Location 'D:\-Studenthub-chatbot-AI-using-RAG\web'
npm.cmd install
```

Tạo file [backend/.env](backend/.env) nếu cần Gemini, với nội dung:

```dotenv
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-3.1-flash-lite
```

Backend tự đọc file này khi khởi động; biến môi trường đã đặt trong terminal được ưu tiên. Cấu hình ở `chatbot/.env` của pipeline cũ không được backend mới tự đọc. Không đưa API key lên GitHub.

Frontend mặc định kết nối `http://127.0.0.1:8000`. Chỉ khi đổi địa chỉ backend, đặt `PYTHON_API_URL` trong [web/.env.local](web/.env.local), rồi khởi động lại frontend:

```dotenv
PYTHON_API_URL=http://127.0.0.1:8000
```

### Khi thêm hoặc sửa tài liệu

1. Lưu tài liệu Markdown UTF-8 vào [chatbot/data/](chatbot/data/).
2. Dừng và chạy lại backend để khởi động việc dựng embedding cho nội dung mới. Tìm kiếm từ khóa BM25 vẫn hoạt động trong lúc chờ.
3. Backend lưu vector vào `backend/embeddings_cache.json` và dùng lại trong những lần chạy sau. File này được Git bỏ qua; máy khác cần dựng cache riêng.

Để chủ động dựng chỉ mục và đợi kết quả, dừng backend rồi chạy từ thư mục gốc:

```powershell
& .\.venv\Scripts\python.exe -u -c "from backend.repositories.documents import load_passages; from backend.services.embeddings import ensure_index; print('Dense index ready:', ensure_index(load_passages()))"
```

`Dense index ready: True` nghĩa là chỉ mục vector đã sẵn sàng. Nếu là `False`, kiểm tra Gemini key, kết nối mạng và quota; bot vẫn có thể dùng BM25. Pipeline mặc định chỉ ghi cache sau khi hoàn tất toàn bộ, nên giữ tiến trình chạy đến khi có kết quả; nếu bị ngắt trước đó, lần sau có thể phải tạo lại. Không cần xóa cache cũ: backend tự kiểm tra nội dung để xác định khi nào cần dựng lại.

### Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Web báo không kết nối được backend | Kiểm tra terminal backend còn chạy và gọi `/health` bằng lệnh phía trên. |
| Cổng 8000 hoặc 3000 đang được dùng | Kiểm tra terminal chạy trước đó và dừng bằng Ctrl+C. Nếu Next.js chọn cổng khác, mở đúng địa chỉ được in ra. |
| Bot chỉ trích tài liệu, không đọc ảnh hoặc gọi tool | Kiểm tra `GEMINI_API_KEY` trong `backend/.env`, rồi khởi động lại backend; xem lỗi API/quota trong terminal. |
| Gemini trả `429` | API đang giới hạn quota/tốc độ. Giao diện hiện thời gian chờ nếu API cung cấp; nếu hết quota ngày, cần chờ quota hồi phục hoặc dùng model khác còn quyền truy cập/quota trong cùng dự án. |
| Chat báo phản hồi quá lâu | Đây là timeout, không tự động có nghĩa hết token. Backend có giới hạn tổng 80 giây; chỉ thử lại một lần trước khi phát nội dung/tool, proxy chờ tối đa 90 giây. |
| Không tìm thấy Python trong `.venv` hoặc thiếu frontend dependency | Làm các bước cấu hình lần đầu ở trên. |

Hướng dẫn tính năng và giới hạn bản demo: [docs/FEATURES.md](docs/FEATURES.md). Hồ sơ sinh viên hiện là dữ liệu mẫu, chưa có đăng nhập theo từng người.

## Why this project exists

The project models a real digital student hub in a simplified form:

- Students can view profile, schedule, finance, training status, and service requests
- Staff or students can ask policy and procedure questions in natural language
- The backend retrieves relevant source passages from a local knowledge corpus
- Optional Gemini integration allows answer synthesis from those passages
- The UI remains separated from the core retrieval logic for easier maintenance

## System overview

This repository has three main execution layers:

- `app.py` — the original Streamlit-based standalone demo
- `backend/` — the Python API and retrieval engine
- `web/` — the main Next.js portal and chatbot UI

## Features

- Student dashboard and navigation shell
- Academic timetable and class listings
- Finance and fee tracking mock data
- Training score and service request flows
- FAQ content for typical student procedures
- AI assistant for academic and administrative questions
- Retrieval from Markdown documents
- Optional answer generation via Gemini
- Local API interface for frontend integration

## Tech stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS
- Backend: Python 3.10+, standard library HTTP server
- Retrieval: lightweight lexical search and excerpt ranking
- Optional generation: Google Gemini REST API
- Demo data: Markdown files and sample JSON-like data structures

## Repository structure

```text
Studenthub-chatbot/
├── app.py                     # standalone Streamlit demo
├── demo_data.py              # sample student and portal data
├── requirements.txt          # Python dependency baseline
├── README.md                 # project overview and setup
├── backend/
│   ├── __main__.py
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── server.py
│   ├── README.md
│   ├── repositories/
│   │   └── documents.py
│   └── services/
│       ├── chat.py
│       ├── gemini.py
│       └── retrieval.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   └── API.md
├── web/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── README.md
└── chatbot/
    └── data/                 # expected knowledge-base folder for Markdown sources
```

## Quick start

### 1. Create and activate a Python environment

```bash
cd /path/to/Studenthub-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Prepare the knowledge base

The backend indexes Markdown files in `chatbot/data/`.

```bash
mkdir -p chatbot/data
```

Add your `.md` files there before starting the API. If the folder is empty, the backend will still start but will return a no-match response for chat questions.

### 3. Start the Python backend

```bash
python3 -m backend
```

This starts the local API on `http://127.0.0.1:8000`.

### 4. Start the frontend

Open a second terminal:

```bash
cd web
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

## Optional Gemini configuration

When `GEMINI_API_KEY` is present, the backend uses Gemini to synthesize the final answer based on retrieved passages. If the key is missing, the system falls back to local extractive responses built from the matched source lines.

```bash
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-3.1-flash-lite"
python3 -m backend
```

The frontend connects to the backend through the `PYTHON_API_URL` environment variable:

```bash
export PYTHON_API_URL="http://127.0.0.1:8000"
```

## Environment variables

### Python backend

- `PYTHON_API_HOST` — default: `127.0.0.1`
- `PYTHON_API_PORT` — default: `8000`
- `GEMINI_API_KEY` — optional API key for answer generation
- `GEMINI_MODEL` — optional model name; default `gemini-3.1-flash-lite`

### Next.js frontend

- `PYTHON_API_URL` — backend base URL for `/chat` requests

## API behavior

The backend exposes a compact REST contract:

- `GET /health` — health and data summary
- `GET /sources` — source metadata
- `POST /chat` — question-answer endpoint

For a full request and response reference, see [docs/API.md](docs/API.md).

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design and data flow
- [docs/SETUP.md](docs/SETUP.md) — local install and run instructions
- [docs/API.md](docs/API.md) — backend endpoint contract
- [backend/README.md](backend/README.md) — backend module-level overview
- [web/README.md](web/README.md) — frontend usage notes

## Notes

This is a demo project intended to showcase a student support portal with retrieval-based assistance. It includes sample records and sample knowledge content instead of production-grade institutional systems. For a production deployment, the recommended next steps include authentication, database persistence, access controls, caching, monitoring, and deployment automation.
