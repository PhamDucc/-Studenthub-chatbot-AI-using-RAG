"""Paths and small runtime settings for the local demo."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "chatbot" / "data"


def _load_local_env(path: Path) -> None:
    """Load the demo env file without adding a runtime dependency."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key.replace("_", "").isalnum():
            os.environ.setdefault(key, value)


_load_local_env(PROJECT_ROOT / "backend" / ".env")

API_HOST = os.getenv("PYTHON_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("PYTHON_API_PORT", "8000"))
MAX_BODY_BYTES = 16_384
MAX_QUESTION_LENGTH = 2_000
MAX_HISTORY_TURNS = 6
MAX_HISTORY_CONTENT = 1_000

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
TOP_K = max(1, min(int(os.getenv("RAG_TOP_K", "6")), 12))
MIN_RETRIEVAL_SCORE = float(os.getenv("RAG_MIN_SCORE", "1.5"))

FEEDBACK_DB = Path(os.getenv("FEEDBACK_DB", str(PROJECT_ROOT / "backend" / "feedback.db")))
MAX_FEEDBACK_TEXT = 6_000
REQUESTS_DB = Path(os.getenv("REQUESTS_DB", str(PROJECT_ROOT / "backend" / "requests.db")))
# The demo portal data is frozen at this date (a Monday) so "today" matches the dashboard.
DEMO_TODAY = os.getenv("DEMO_TODAY", "2026-10-19")
MAX_TOOL_ROUNDS = 4
CHAT_TIMEOUT_SECONDS = 80.0
GEMINI_TIMEOUT_SECONDS = 25.0

# Hybrid retrieval: Gemini embeddings fused with BM25. Set RAG_DENSE=0 to force lexical-only.
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
EMBED_DIMS = 768
EMBED_CACHE = Path(os.getenv("EMBED_CACHE", str(PROJECT_ROOT / "backend" / "embeddings_cache.json")))
DENSE_MIN_SCORE = float(os.getenv("RAG_DENSE_MIN", "0.60"))
LEXICAL_STRONG_SCORE = float(os.getenv("RAG_LEXICAL_STRONG", "20"))  # exact keyword match that overrides a weak dense score
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))

# Admin analytics are disabled unless ADMIN_TOKEN is set (sent as the X-Admin-Token header).
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()
CHATLOG_DB = Path(os.getenv("CHATLOG_DB", str(PROJECT_ROOT / "backend" / "chatlog.db")))
TICKETS_DB = Path(os.getenv("TICKETS_DB", str(PROJECT_ROOT / "backend" / "tickets.db")))
MAX_ATTACHMENT_BYTES = 4 * 1024 * 1024
ATTACHMENT_MIME_TYPES = ("image/png", "image/jpeg", "image/webp", "application/pdf")
