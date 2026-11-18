"""Service requests (đơn từ) filed through the assistant, stored in SQLite."""

from datetime import date
from pathlib import Path
import sqlite3

from ..config import DEMO_TODAY, REQUESTS_DB
from .student import REQUEST_HISTORY, REQUEST_TYPES

FIRST_NUMBER = 413  # continues after the seeded DV-2026-0412


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            reason TEXT NOT NULL,
            copies INTEGER NOT NULL,
            submitted_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Đang xử lý'
        )"""
    )
    return conn


def _row(row: sqlite3.Row) -> dict:
    return {"id": f"DV-2026-{FIRST_NUMBER - 1 + row['id']:04d}", "type": REQUEST_TYPES[row["type"]]["label"],
            "submitted_at": row["submitted_at"], "status": row["status"], "copies": row["copies"]}


def validate_request(request_type: object, reason: object, copies: object) -> tuple[str, str, int]:
    if request_type not in REQUEST_TYPES:
        raise ValueError("Loại đơn không hợp lệ.")
    if not isinstance(reason, str) or not 10 <= len(reason.strip()) <= 500:
        raise ValueError("Lý do / mục đích phải từ 10 đến 500 ký tự.")
    if isinstance(copies, bool) or not isinstance(copies, int) or not 1 <= copies <= 10:
        raise ValueError("Số bản phải từ 1 đến 10.")
    return request_type, reason.strip(), copies


def create_request(client_id: str, request_type: str, reason: str, copies: int, path: Path | None = None) -> dict:
    """Create a request; repeating the same client_id returns the original (idempotent)."""
    request_type, reason, copies = validate_request(request_type, reason, copies)
    submitted = date.fromisoformat(DEMO_TODAY).strftime("%d/%m/%Y")
    with _connect(path or REQUESTS_DB) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO requests (client_id, type, reason, copies, submitted_at) VALUES (?,?,?,?,?)",
            (client_id, request_type, reason, copies, submitted),
        )
        return _row(conn.execute("SELECT * FROM requests WHERE client_id = ?", (client_id,)).fetchone())


def list_requests(path: Path | None = None) -> list[dict]:
    """Newest first: requests filed through the assistant, then the seeded history."""
    with _connect(path or REQUESTS_DB) as conn:
        filed = [_row(row) for row in conn.execute("SELECT * FROM requests ORDER BY id DESC")]
    return filed + [dict(item) for item in REQUEST_HISTORY]
