"""Handoff tickets: questions the assistant could not answer, escalated to staff."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

from ..config import TICKETS_DB

FIRST_NUMBER = 1


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            question TEXT NOT NULL,
            summary TEXT NOT NULL,
            student TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Mới',
            channel TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        )"""
    )
    return conn


def _row(row: sqlite3.Row) -> dict:
    item = dict(row)
    item["code"] = f"HT-2026-{FIRST_NUMBER - 1 + item['id']:04d}"
    item["student"] = json.loads(item["student"])
    return item


def create_ticket(client_id: str, department: str, question: str, summary: str, student: dict,
                  path: Path | None = None) -> tuple[dict, bool]:
    """Returns (ticket, created). Repeating a client_id returns the original with created=False."""
    with _connect(path or TICKETS_DB) as conn:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO tickets (client_id, department, question, summary, student, created_at) VALUES (?,?,?,?,?,?)",
            (client_id, department, question, summary, json.dumps(student, ensure_ascii=False),
             datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
        return _row(conn.execute("SELECT * FROM tickets WHERE client_id = ?", (client_id,)).fetchone()), cursor.rowcount == 1


def set_channel(ticket_id: int, channel: str, path: Path | None = None) -> None:
    with _connect(path or TICKETS_DB) as conn:
        conn.execute("UPDATE tickets SET channel = ? WHERE id = ?", (channel, ticket_id))


def list_tickets(limit: int = 50, path: Path | None = None) -> list[dict]:
    with _connect(path or TICKETS_DB) as conn:
        return [_row(r) for r in conn.execute("SELECT * FROM tickets ORDER BY id DESC LIMIT ?", (limit,))]
