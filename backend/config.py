"""Paths and small runtime settings for the local demo."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "chatbot" / "data"

API_HOST = os.getenv("PYTHON_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("PYTHON_API_PORT", "8000"))
MAX_BODY_BYTES = 16_384
MAX_QUESTION_LENGTH = 2_000
MAX_HISTORY_TURNS = 6
MAX_HISTORY_CONTENT = 1_000

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TOP_K = 8
