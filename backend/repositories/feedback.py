"""Store thumbs up/down feedback on assistant answers in SQLite."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from ..config import FEEDBACK_DB

REASONS = {"inaccurate", "outdated", "incomplete", "irrelevant", "other"}


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT NOT NULL UNIQUE,
            rating TEXT NOT NULL CHECK (rating IN ('up', 'down')),
            reason TEXT,
            comment TEXT,
            question TEXT,
            answer TEXT,
            sources TEXT,
            mode TEXT,
            created_at TEXT NOT NULL
        )"""
    )
    return conn


def save_feedback(entry: dict, path: Path | None = None) -> None:
    """Insert or replace feedback for a message (a user may change their rating)."""
    with _connect(path or FEEDBACK_DB) as conn:
        conn.execute(
            """INSERT INTO feedback (message_id, rating, reason, comment, question, answer, sources, mode, created_at)
               VALUES (:message_id, :rating, :reason, :comment, :question, :answer, :sources, :mode, :created_at)
               ON CONFLICT(message_id) DO UPDATE SET rating=excluded.rating, reason=excluded.reason,
               comment=excluded.comment, created_at=excluded.created_at""",
            {**entry, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")},
        )


def feedback_stats(path: Path | None = None) -> dict:
    with _connect(path or FEEDBACK_DB) as conn:
        up, down = conn.execute(
            "SELECT COALESCE(SUM(rating='up'),0), COALESCE(SUM(rating='down'),0) FROM feedback"
        ).fetchone()
        reasons = dict(conn.execute(
            "SELECT reason, COUNT(*) FROM feedback WHERE rating='down' AND reason IS NOT NULL GROUP BY reason"
        ).fetchall())
    return {"up": up, "down": down, "reasons": reasons}
