# Architecture Overview

Student Hub UET is a demo university assistant that combines a student portal UI with a retrieval-based question answering backend. The project is designed for local demonstration, education, and rapid prototyping rather than production-scale deployment.

## High-level design

The system is intentionally split into two runtime layers:

- Frontend: a Next.js application in `web/` that renders the student portal and the floating AI assistant
- Backend: a Python service in `backend/` that indexes Markdown knowledge files and responds to chat questions

The frontend does not own business logic for retrieval; it simply forwards user questions to the Python API and displays the returned answer and source references.

```mermaid
flowchart LR
    A[Student / staff user] --> B[Next.js portal]
    B --> C[/api/chat route]
    C --> D[Python backend API]
    D --> E[Retrieval layer]
    E --> F[Markdown source docs]
    E --> G{Gemini API configured?}
    G -->|Yes| H[Gemini response]
    G -->|No| I[Extractive fallback]
    H --> J[JSON response with answer + sources]
    I --> J
    J --> B
    B --> A
```

## Frontend responsibilities

The web app in `web/` focuses on presentation and user experience:

- Dashboard UI for profile, timetable, finance, and service requests
- Portal pages for academic, financial, counseling, and FAQ content
- Floating AI assistant widget for natural-language queries
- API route that proxies requests to the Python backend

Key files:

- `web/app/api/chat/route.ts`
- `web/components/chat/chat-widget.tsx`
- `web/components/portal/app-shell.tsx`
- `web/lib/data.ts`

## Backend responsibilities

The backend is organized around a local retrieval pipeline:

1. Load Markdown files from the configured data directory
2. Split content into searchable passages
3. Normalize and tokenize questions
4. Score passages using TF-IDF-inspired lexical matching
5. Return the most relevant excerpts and optional answer synthesis

Key modules:

- `backend/server.py` — HTTP API and request validation
- `backend/services/retrieval.py` — indexing, matching, and answer extraction
- `backend/services/chat.py` — orchestration layer
- `backend/services/gemini.py` — optional LLM answer generation
- `backend/repositories/documents.py` — markdown ingestion

## Retrieval model

The retrieval system is intentionally lightweight and offline-friendly:

- It parses Markdown files and converts sections into chunked passages
- It calculates token-based relevance using normalized Vietnamese text
- It prefers answer excerpts from the most relevant passages when Gemini is unavailable

This keeps the demo easy to run without external vector databases or heavy dependencies.

## Data flow

A chat request follows this path:

1. User asks a question from the Next.js UI
2. The route file calls the Python API at `http://127.0.0.1:8000/chat`
3. `backend/server.py` validates and parses the JSON payload
4. `backend/services/chat.py` decides whether to use Gemini or the local extraction path
5. `backend/services/retrieval.py` selects the best source passages
6. The answer and citations are returned to the frontend

## Runtime configuration

The project supports both local run mode and optional AI enhancement:

- `PYTHON_API_HOST` and `PYTHON_API_PORT` control the Python server bind address
- `PYTHON_API_URL` tells the Next.js app where the backend lives
- `GEMINI_API_KEY` enables Gemini-powered answer generation
- `GEMINI_MODEL` selects the model version, defaulting to `gemini-2.5-flash`

## Design trade-offs

This project prioritizes clarity over enterprise complexity:

- Standard library Python for the backend API layer
- Lexical retrieval rather than a production vector database
- Demo data and sample student records instead of real institutional systems
- Clear modular boundaries so the retrieval layer can be swapped later

This makes the codebase easy to understand and extend for coursework, internal demos, or prototype deployments.
