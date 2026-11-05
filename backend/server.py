"""Local HTTP API for the Next.js demo in web/."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os

from .services.chat import answer_question
from .config import API_HOST, API_PORT, MAX_BODY_BYTES, MAX_HISTORY_CONTENT, MAX_HISTORY_TURNS, MAX_QUESTION_LENGTH
from .models import ConversationTurn
from .repositories.documents import load_passages


def parse_chat_payload(payload: object) -> tuple[str, list[ConversationTurn]]:
    if not isinstance(payload, dict):
        raise ValueError("Yêu cầu phải là một JSON object.")
    question = payload.get("question")
    if not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_LENGTH:
        raise ValueError("Câu hỏi phải có từ 1 đến 2000 ký tự.")

    raw_history = payload.get("history", [])
    if not isinstance(raw_history, list) or len(raw_history) > MAX_HISTORY_TURNS:
        raise ValueError(f"Lịch sử hội thoại tối đa {MAX_HISTORY_TURNS} lượt.")
    history: list[ConversationTurn] = []
    for turn in raw_history:
        if not isinstance(turn, dict):
            raise ValueError("Lịch sử hội thoại không hợp lệ.")
        role, content = turn.get("role"), turn.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            raise ValueError("Lịch sử hội thoại không hợp lệ.")
        if not content.strip() or len(content) > MAX_HISTORY_CONTENT:
            raise ValueError(f"Mỗi lượt hội thoại phải có từ 1 đến {MAX_HISTORY_CONTENT} ký tự.")
        history.append(ConversationTurn(role, content.strip()))
    return question.strip(), history


def source_summary() -> list[dict]:
    sources: dict[str, dict] = {}
    for passage in load_passages():
        item = sources.setdefault(passage.source, {
            "source": passage.source, "title": passage.title, "passages": 0,
        })
        item["passages"] += 1
    return list(sources.values())

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            sources = source_summary()
            self.send_json(200, {
                "status": "ok" if sources else "empty",
                "documents": len(sources),
                "passages": sum(source["passages"] for source in sources),
                "generation": "gemini" if os.getenv("GEMINI_API_KEY", "").strip() else "extractive",
            })
        elif self.path == "/sources":
            self.send_json(200, {"sources": source_summary()})
        else:
            self.send_json(404, {"error": "Không tìm thấy đường dẫn."})

    def do_POST(self) -> None:
        if self.path != "/chat":
            self.send_json(404, {"error": "Không tìm thấy đường dẫn."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Yêu cầu không hợp lệ."})
            return
        if length < 1:
            self.send_json(400, {"error": "Nội dung yêu cầu trống."})
            return
        if length > MAX_BODY_BYTES:
            self.send_json(413, {"error": "Nội dung yêu cầu quá lớn."})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "JSON không hợp lệ."})
            return
        try:
            question, history = parse_chat_payload(payload)
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
            return
        try:
            result = answer_question(question, history)
        except Exception:
            logging.exception("Failed to answer chat request")
            self.send_json(500, {"error": "Không thể xử lý câu hỏi lúc này."})
            return
        self.send_json(200, {
            "answer": result.answer,
            "sources": [
                {"number": index, "title": hit.passage.title,
                 "heading": hit.passage.heading, "source": hit.passage.source}
                for index, hit in enumerate(result.hits, 1)
            ],
            "warning": result.warning,
            "mode": result.mode,
        })


def main() -> None:
    server = ThreadingHTTPServer((API_HOST, API_PORT), Handler)
    print(f"Python chatbot API: http://{API_HOST}:{API_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
