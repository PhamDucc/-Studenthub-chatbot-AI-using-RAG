"""Chat log and aggregate analytics (no raw personal data: questions are PII-redacted)."""

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sqlite3

from ..config import CHATLOG_DB
from ..services.retrieval import tokens
from .feedback import feedback_stats


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS chat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            question TEXT NOT NULL,
            lang TEXT,
            mode TEXT NOT NULL,
            tools TEXT NOT NULL DEFAULT '',
            sources TEXT NOT NULL DEFAULT '',
            cached INTEGER NOT NULL DEFAULT 0,
            needs_human INTEGER NOT NULL DEFAULT 0,
            has_attachment INTEGER NOT NULL DEFAULT 0,
            latency_ms INTEGER
        )"""
    )
    return conn


def log_chat(entry: dict, path: Path | None = None) -> None:
    with _connect(path or CHATLOG_DB) as conn:
        conn.execute(
            """INSERT INTO chat_log (ts, question, lang, mode, tools, sources, cached, needs_human, has_attachment, latency_ms)
               VALUES (:ts, :question, :lang, :mode, :tools, :sources, :cached, :needs_human, :has_attachment, :latency_ms)""",
            {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "lang": None, "tools": "", "sources": "",
             "cached": 0, "needs_human": 0, "has_attachment": 0, "latency_ms": None, **entry},
        )


def _topic_key(question: str) -> str:
    return " ".join(sorted(set(tokens(question)))) or question.lower()


def analytics(days: int = 30, path: Path | None = None, feedback_path: Path | None = None) -> dict:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    with _connect(path or CHATLOG_DB) as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM chat_log WHERE ts >= ? ORDER BY id", (since,))]
    questions = [r for r in rows if r["mode"] not in ("smalltalk", "blocked")]
    total = len(rows)
    unanswered = [r for r in questions if r["needs_human"]]
    groups: dict[str, list[dict]] = {}
    for r in questions:
        groups.setdefault(_topic_key(r["question"]), []).append(r)
    top = sorted(groups.values(), key=len, reverse=True)[:8]
    gaps: dict[str, list[dict]] = {}
    for r in unanswered:
        gaps.setdefault(_topic_key(r["question"]), []).append(r)
    word_counts: Counter[str] = Counter()
    for r in unanswered:
        word_counts.update(set(tokens(r["question"])))
    feedback = feedback_stats(feedback_path)
    rated = feedback["up"] + feedback["down"]
    per_day = Counter(r["ts"][:10] for r in rows)
    latencies = sorted(r["latency_ms"] for r in rows if r["latency_ms"])
    return {
        "days": days,
        "totals": {
            "messages": total, "questions": len(questions), "unanswered": len(unanswered),
            "answered_rate": round(1 - len(unanswered) / len(questions), 3) if questions else None,
            "cached": sum(r["cached"] for r in rows), "with_attachment": sum(r["has_attachment"] for r in rows),
            "english": sum(r["lang"] == "en" for r in rows), "blocked": sum(r["mode"] == "blocked" for r in rows),
            "p50_latency_ms": latencies[len(latencies) // 2] if latencies else None,
            "satisfaction": round(feedback["up"] / rated, 3) if rated else None, "rated": rated,
        },
        "modes": dict(Counter(r["mode"] for r in rows)),
        "tools": dict(Counter(t for r in rows for t in r["tools"].split(",") if t)),
        "top_questions": [{"question": g[-1]["question"], "count": len(g)} for g in top],
        "unanswered": sorted(
            ({"question": g[-1]["question"], "count": len(g), "last_seen": g[-1]["ts"]} for g in gaps.values()),
            key=lambda item: item["count"], reverse=True)[:15],
        "document_gaps": [{"topic": word, "questions": count} for word, count in word_counts.most_common(8) if count >= 1],
        "feedback_reasons": feedback["reasons"],
        "per_day": [{"date": d, "count": c} for d, c in sorted(per_day.items())],
    }
