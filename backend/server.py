"""Local HTTP API for the Next.js demo in web/."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import base64
import hmac
import binascii
import logging
import os
import time

from .services.chat import answer_question, hit_to_dict, stream_chat
from .config import (
    ADMIN_TOKEN, API_HOST, API_PORT, ATTACHMENT_MIME_TYPES, MAX_ATTACHMENT_BYTES, MAX_BODY_BYTES, MAX_FEEDBACK_TEXT, MAX_HISTORY_CONTENT,
    MAX_HISTORY_TURNS, MAX_QUESTION_LENGTH,
)
from .models import ConversationTurn
from .repositories.documents import load_passages
from .services.embeddings import start_warmup
from .services.handoff import open_ticket
from .services.lang import detect
from .services.safety import chat_limiter, redact
from .repositories.chatlog import analytics, log_chat
from .repositories.tickets import list_tickets
from .repositories.requests import create_request, list_requests
from .services.tools import reminders
from .repositories.feedback import REASONS, feedback_stats, save_feedback


def parse_chat_payload(payload: object) -> tuple[str, list[ConversationTurn]]:
    if not isinstance(payload, dict):
        raise ValueError("Yêu cầu phải là một JSON object.")
    question = payload.get("question")
    if isinstance(payload.get("attachment"), dict) and (question is None or question == ""):
        question = "Hãy giải thích nội dung tệp đính kèm."
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


def parse_attachment(payload: object) -> dict | None:
    """Validate an optional {mime, data(base64), name} image/PDF attachment."""
    attachment = payload.get("attachment") if isinstance(payload, dict) else None
    if attachment is None:
        return None
    if not isinstance(attachment, dict):
        raise ValueError("Tệp đính kèm không hợp lệ.")
    mime, data = attachment.get("mime"), attachment.get("data")
    if mime not in ATTACHMENT_MIME_TYPES:
        raise ValueError("Chỉ hỗ trợ ảnh PNG, JPEG, WebP hoặc PDF.")
    if not isinstance(data, str) or not data:
        raise ValueError("Tệp đính kèm trống.")
    try:
        size = len(base64.b64decode(data, validate=True))
    except (binascii.Error, ValueError):
        raise ValueError("Tệp đính kèm không hợp lệ.") from None
    if size > MAX_ATTACHMENT_BYTES:
        raise ValueError(f"Tệp quá lớn (tối đa {MAX_ATTACHMENT_BYTES // (1024 * 1024)} MB).")
    name = attachment.get("name")
    return {"mime": mime, "data": data, "name": name[:120] if isinstance(name, str) else "tệp"}


def parse_feedback_payload(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Yêu cầu phải là một JSON object.")
    message_id, rating = payload.get("message_id"), payload.get("rating")
    if not isinstance(message_id, str) or not 1 <= len(message_id) <= 80:
        raise ValueError("message_id không hợp lệ.")
    if rating not in ("up", "down"):
        raise ValueError("rating phải là 'up' hoặc 'down'.")
    reason = payload.get("reason")
    if reason is not None and reason not in REASONS:
        raise ValueError("Lý do không hợp lệ.")

    def text(key: str, limit: int = MAX_FEEDBACK_TEXT) -> str | None:
        value = payload.get(key)
        return value[:limit] if isinstance(value, str) and value.strip() else None

    sources = payload.get("sources")
    return {
        "message_id": message_id, "rating": rating,
        "reason": reason if rating == "down" else None,
        "comment": redact(text("comment", 500)), "question": redact(text("question", MAX_QUESTION_LENGTH)),
        "answer": redact(text("answer")),
        "sources": ", ".join(str(item)[:120] for item in sources[:12]) if isinstance(sources, list) else None,
        "mode": text("mode", 20),
    }


def source_summary() -> list[dict]:
    sources: dict[str, dict] = {}
    for passage in load_passages():
        item = sources.setdefault(passage.source, {
            "source": passage.source, "title": passage.title, "passages": 0,
        })
        item["passages"] += 1
    return list(sources.values())

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict, retry_after: int | None = None) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if retry_after:
            self.send_header("Retry-After", str(retry_after))
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
        elif self.path.startswith("/admin/"):
            if not self.admin_ok():
                return
            if self.path == "/admin/analytics":
                self.send_json(200, analytics())
            elif self.path == "/admin/tickets":
                self.send_json(200, {"tickets": list_tickets()})
            else:
                self.send_json(404, {"error": "Không tìm thấy đường dẫn."})
        elif self.path == "/reminders":
            self.send_json(200, {"reminders": reminders()})
        elif self.path == "/requests":
            self.send_json(200, {"requests": list_requests()})
        elif self.path == "/feedback/stats":
            self.send_json(200, feedback_stats())
        elif self.path == "/sources":
            self.send_json(200, {"sources": source_summary()})
        else:
            self.send_json(404, {"error": "Không tìm thấy đường dẫn."})

    def read_json(self, max_bytes: int = MAX_BODY_BYTES) -> object | None:
        """Read the JSON body; send an error and return None when it is unusable."""
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Yêu cầu không hợp lệ."})
            return None
        if length < 1:
            self.send_json(400, {"error": "Nội dung yêu cầu trống."})
            return None
        if length > max_bytes:
            self.send_json(413, {"error": "Nội dung yêu cầu quá lớn."})
            return None
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "JSON không hợp lệ."})
            return None

    def do_POST(self) -> None:
        routes = {"/chat": self.handle_chat, "/chat/stream": self.handle_chat_stream,
                  "/feedback": self.handle_feedback, "/requests": self.handle_create_request,
                  "/handoff": self.handle_handoff}
        route = routes.get(self.path)
        if route is None:
            self.send_json(404, {"error": "Không tìm thấy đường dẫn."})
            return
        if self.path.startswith("/chat"):
            wait = chat_limiter.check(self.client_key())
            if wait:
                self.send_json(429, {"error": f"Bạn gửi quá nhiều câu hỏi. Vui lòng thử lại sau {int(wait)} giây."},
                               retry_after=int(wait))
                return
        # Only the streaming chat endpoint accepts attachments, so only it may carry a large body.
        limit = MAX_BODY_BYTES + MAX_ATTACHMENT_BYTES * 4 // 3 + 1024 if self.path == "/chat/stream" else MAX_BODY_BYTES
        payload = self.read_json(limit)
        if payload is not None:
            route(payload)

    def client_key(self) -> str:
        """Client identity for rate limiting; trust X-Forwarded-For only from the local Next.js proxy."""
        peer = (getattr(self, "client_address", None) or ("local",))[0]
        forwarded = self.headers.get("X-Forwarded-For", "") if hasattr(self.headers, "get") else ""
        if peer in ("127.0.0.1", "::1", "local") and forwarded:
            return forwarded.split(",")[0].strip()[:64]
        return peer

    def handle_chat(self, payload: object) -> None:
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
        self.record(question, result.mode, "", ",".join(h.passage.source for h in result.hits), False,
                    result.mode == "no_match", False, None)
        self.send_json(200, {
            "answer": result.answer,
            "sources": [hit_to_dict(index, hit, question) for index, hit in enumerate(result.hits, 1)],
            "warning": result.warning,
            "mode": result.mode,
            "follow_ups": result.follow_ups,
        })

    def handle_chat_stream(self, payload: object) -> None:
        try:
            question, history = parse_chat_payload(payload)
            attachment = parse_attachment(payload)
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        started, sources, done = time.monotonic(), [], {}
        try:
            for event in stream_chat(question, history, attachment):
                if event["type"] == "sources":
                    sources = [item["source"] for item in event["sources"]]
                elif event["type"] == "done":
                    done = event
                self.send_event(event)
        except (BrokenPipeError, ConnectionResetError):
            return  # client aborted
        except Exception:
            logging.exception("Failed to stream chat response")
            try:
                self.send_event({"type": "error", "error": "Không thể xử lý câu hỏi lúc này."})
            except OSError:
                pass
            return
        if done:
            self.record(question, done.get("mode", "unknown"), ",".join(done.get("tools", [])), ",".join(sources),
                        bool(done.get("cached")), bool(done.get("needs_human")), attachment is not None,
                        int((time.monotonic() - started) * 1000))

    def record(self, question: str, mode: str, tools_used: str, sources: str, cached: bool, needs_human: bool,
               has_attachment: bool, latency_ms: int | None) -> None:
        """Best-effort analytics log; never affects the response."""
        try:
            log_chat({"question": redact(question)[:500], "lang": detect(question), "mode": mode, "tools": tools_used,
                      "sources": ",".join(sorted(set(filter(None, sources.split(","))))), "cached": int(cached),
                      "needs_human": int(needs_human), "has_attachment": int(has_attachment), "latency_ms": latency_ms})
        except Exception:
            logging.exception("Failed to write chat log")

    def handle_handoff(self, payload: object) -> None:
        """Create a staff ticket for a question the student confirmed should be escalated."""
        try:
            question, history = parse_chat_payload(payload)
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
            return
        client_id = payload.get("client_id")
        if not isinstance(client_id, str) or not 8 <= len(client_id) <= 64:
            self.send_json(400, {"error": "client_id không hợp lệ."})
            return
        try:
            ticket = open_ticket(client_id, question, history)
        except Exception:
            logging.exception("Failed to open handoff ticket")
            self.send_json(500, {"error": "Không tạo được yêu cầu hỗ trợ."})
            return
        self.send_json(200, {"ticket": {k: ticket[k] for k in ("code", "department_name", "status", "channel")}})

    def admin_ok(self) -> bool:
        if not ADMIN_TOKEN:
            self.send_json(403, {"error": "Chưa cấu hình ADMIN_TOKEN nên trang quản trị đang tắt."})
            return False
        supplied = self.headers.get("X-Admin-Token", "") if hasattr(self.headers, "get") else ""
        if not hmac.compare_digest(supplied.encode(), ADMIN_TOKEN.encode()):
            self.send_json(401, {"error": "Sai mã quản trị."})
            return False
        return True

    def send_event(self, event: dict) -> None:
        self.wfile.write(b"data: " + json.dumps(event, ensure_ascii=False).encode("utf-8") + b"\n\n")
        self.wfile.flush()

    def handle_create_request(self, payload: object) -> None:
        """File a request the student confirmed in the chat UI."""
        if not isinstance(payload, dict):
            self.send_json(400, {"error": "Yêu cầu phải là một JSON object."})
            return
        client_id = payload.get("client_id")
        if not isinstance(client_id, str) or not 8 <= len(client_id) <= 64:
            self.send_json(400, {"error": "client_id không hợp lệ."})
            return
        try:
            created = create_request(client_id, payload.get("request_type"), payload.get("reason"), payload.get("copies"))
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
            return
        except Exception:
            logging.exception("Failed to create request")
            self.send_json(500, {"error": "Không gửi được đơn."})
            return
        self.send_json(200, {"request": created})

    def handle_feedback(self, payload: object) -> None:
        try:
            entry = parse_feedback_payload(payload)
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
            return
        try:
            save_feedback(entry)
        except Exception:
            logging.exception("Failed to save feedback")
            self.send_json(500, {"error": "Không lưu được phản hồi."})
            return
        self.send_json(200, {"ok": True})


def main() -> None:
    start_warmup(load_passages())
    server = ThreadingHTTPServer((API_HOST, API_PORT), Handler)
    print(f"Python chatbot API: http://{API_HOST}:{API_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
