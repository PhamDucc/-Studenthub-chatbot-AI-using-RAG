# Student Hub UET

Student Hub UET is a demo university student portal and AI assistant built for an academic support experience. The project combines a modern Next.js student portal with a Python retrieval-based chatbot that answers questions from Markdown knowledge documents.

The application is designed for demonstration, internal prototyping, and educational use. It includes demo student data, service forms, timetable and finance screens, and a chat assistant powered by retrieval over a local knowledge base.

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
export GEMINI_MODEL="gemini-2.5-flash"
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
- `GEMINI_MODEL` — optional model name; default `gemini-2.5-flash`

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
