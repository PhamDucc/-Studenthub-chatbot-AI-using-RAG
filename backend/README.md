# Backend Documentation

The Python backend powers the student assistant and exposes a local HTTP API for the Next.js frontend. It is intentionally lightweight and transparent so the retrieval flow can be understood quickly and extended safely.

## Purpose

The backend responsibilities are:

- read student knowledge content from Markdown files
- split text into searchable passages
- match user questions to relevant source fragments
- return answers or excerpts to the frontend
- optionally call Gemini for answer synthesis

## Module map

```text
backend/
├── __main__.py            # entry point: python3 -m backend
├── server.py              # API server and request validation
├── config.py              # runtime settings and environment variables
├── models.py              # dataclasses for passes, hits, and result objects
├── repositories/
│   └── documents.py       # Markdown ingestion and segmentation
└── services/
    ├── retrieval.py       # search and excerpt ranking
    ├── chat.py            # high-level answer orchestration
    └── gemini.py          # optional Gemini answer generation
```

## Request flow

```text
Frontend -> POST /chat -> server.py -> services/chat.py -> services/retrieval.py -> repositories/documents.py
                                                  \-> services/gemini.py (optional)
```

The full flow is:

1. The frontend sends a `question` and optional `history`
2. `server.py` validates the payload
3. `services/chat.py` normalizes the query and decides whether to use Gemini
4. `services/retrieval.py` ranks relevant passages from the knowledge corpus
5. The result is returned as structured JSON with answer, source references, and metadata

## Retrieval behavior

The retrieval layer is a lexical, TF-IDF style matching system designed for a small local knowledge base. It:

- normalizes Vietnamese text and removes diacritics where appropriate
- tokenizes both questions and content
- scores passages based on term relevance and heading overlap
- extracts the best source lines for answer fallback

This approach keeps the demo self-contained without requiring a vector database or external indexing service.

## Configuration

Core settings live in `backend/config.py`:

- `PROJECT_ROOT` and `DATA_DIR` define the knowledge base location
- `API_HOST` and `API_PORT` configure the server bind address
- `GEMINI_MODEL` sets the Gemini model version
- `TOP_K` controls how many retrieval hits are considered

Required environment variables:

- `GEMINI_API_KEY` (optional for Gemini mode)
- `PYTHON_API_HOST` and `PYTHON_API_PORT` (optional overrides)

## Running the backend

From the project root:

```bash
python3 -m backend
```

Verify the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

## Notes

The backend is intentionally designed as a demo service. If you later replace the lexical retriever with a vector database or an enterprise search engine, the main API contract can remain the same while only the retrieval layer changes.
