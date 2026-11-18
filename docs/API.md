# API Reference

The Python backend exposes a small REST API for the demo student portal.

## Base URL

```text
http://127.0.0.1:8000
```

## Health check

### GET /health

Returns the state of the local knowledge base and generation mode.

Example response:

```json
{
  "status": "ok",
  "documents": 6,
  "passages": 32,
  "generation": "extractive"
}
```

Field definitions:

- `status`: either `ok` or `empty`
- `documents`: number of source files discovered
- `passages`: total extracted passages from the source documents
- `generation`: either `gemini` or `extractive`

## List sources

### GET /sources

Returns the metadata for each loaded source document.

Example response:

```json
{
  "sources": [
    {
      "source": "fees.md",
      "title": "Học phí",
      "passages": 5
    }
  ]
}
```

## Ask a question

### POST /chat

Sends a question to the retrieval layer.

Request body:

```json
{
  "question": "Một ngày được tạo mã QR học phí tối đa mấy lần?",
  "history": [
    { "role": "user", "content": "Tôi muốn biết về học phí" },
    { "role": "assistant", "content": "Tôi có thể giúp bạn về các quy định học phí." }
  ]
}
```

Response body:

```json
{
  "answer": "Các dòng liên quan trong tài liệu:\n\n- ... [1]",
  "sources": [
    {
      "number": 1,
      "title": "Học phí",
      "heading": "Mã QR",
      "source": "fees.md",
      "score": 8.421,
      "excerpt": "Đoạn văn bản được dùng làm căn cứ..."
    }
  ],
  "warning": null,
  "mode": "extractive"
}
```

Field definitions:

- `answer`: final answer or excerpt list
- `sources`: ranked source references
- `score`: điểm liên quan của passage (chỉ dùng để quan sát/debug, không phải xác suất)
- `excerpt`: phần đầu của passage làm căn cứ
- `warning`: Gemini-related warning if generation was unavailable
- `mode`: `gemini`, `extractive`, or `no_match`

## Error handling

The API returns standard HTTP status codes:

- `200` — success
- `400` — invalid request payload
- `404` — unknown endpoint
- `413` — payload too large
- `500` — internal processing failure

Example error payload:

```json
{
  "error": "Câu hỏi phải có từ 1 đến 2000 ký tự."
}
```

## Streaming chat

### POST /chat/stream

Same request body as `POST /chat`. Responds with `text/event-stream`; each frame is `data: <json>` with a `type`:

- `sources`: `sources[]` (`number`, `title`, `heading`, `source`, `score`, `excerpt`, `text`, `highlight`), sent first
- `delta`: `text` chunk to append
- `replace`: discard the text so far (for example, replace an incomplete answer with a service-error explanation)
- `done`: `mode`, `warning`, `follow_ups[]` (suggested next questions), optional `error`
- `error`: `error` message or `{ code, message, retry_after? }` for a failed connection/stream

If Gemini fails, `done.mode` is `unavailable` and `done.error` contains
`{ code, message, retry_after }`. Codes are `timeout`, `rate_limit`, `unavailable`,
`auth`, or `model`; `retry_after` is seconds or `null`. Failed generation is not
replaced by unrelated document excerpts and must not be treated as a completed
answer. With no API key configured, offline `extractive` answers remain supported.

The backend shares an 80-second budget across retrieval and generation. Each
Gemini call can retry once before emitting text or a function call; permanent
configuration errors and long quota waits are returned immediately. The web
proxy allows 90 seconds, and the browser allows 95 seconds.

Streaming requests also accept optional `response_language: "vi" | "en"` to preserve an
explicit language preference across the bounded history window. Each `done` includes
`lang` (this answer's language) and `response_language` (the persistent preference, or
`null` when unset). The client stores the latter per conversation; UI language and
automatically detected answer language do not set it. A current explicit instruction
overrides earlier preferences. A translation request changes only the current answer.
Language-only commands and requests to repeat the previous question resolve to the
latest substantive user question before retrieval; if it is unavailable, the bot asks
for the question again instead of guessing.

`POST /chat` also returns `follow_ups` and the richer `sources` fields.

## Feedback

### POST /feedback

```json
{ "message_id": "uuid", "rating": "up|down", "reason": "inaccurate|outdated|incomplete|irrelevant|other",
  "question": "...", "answer": "...", "sources": ["file.md"], "mode": "gemini" }
```

One row per `message_id` (re-rating overwrites). Stored in SQLite at `FEEDBACK_DB` (default `backend/feedback.db`).

### GET /feedback/stats

Returns `{ "up": n, "down": n, "reasons": { "outdated": n } }`.

## Personalised assistant (tools)

`POST /chat/stream` lets Gemini call read-only tools backed by `backend/repositories/student.py`
(demo data; swap for the real student API): profile, academic summary, timetable, tuition status,
service requests, announcements, `calc_gpa_scenario`, and `propose_service_request`.
The "today" used for timetable/deadlines is `DEMO_TODAY` (default `2026-10-19`).

Extra stream events: `tool` (`name`, `label`), `action` (`kind: "service_request"` plus a prepared
request: `client_id`, `request_type`, `label`, `fee`, `days`, `reason`, `copies`). `done` also carries
`tools[]` and `cited[]`. Tools never change data; an `action` is only a proposal.

### POST /requests

File a request the student confirmed. Body: `client_id` (idempotency key), `request_type`
(`xac-nhan-sv|bang-diem|hoan-thi|nghi-hoc|phuc-khao|mien-giam`), `reason` (10-500 chars), `copies` (1-10).
Returns `{ "request": { "id": "DV-2026-0413", ... } }`. Stored in SQLite at `REQUESTS_DB`
(default `backend/requests.db`).

### GET /requests · GET /reminders

All requests (filed ones first, then seeded history), and proactive reminders for the chat welcome screen.

## Retrieval, routing and safety (Sprint 3)

**Hybrid retrieval.** `search()` fuses BM25 with Gemini embeddings (`gemini-embedding-001`, 768 dims) by
reciprocal-rank fusion. Passage vectors are built in the background at server start and cached in
`backend/embeddings_cache.json`; until ready, or if the API fails, retrieval is BM25-only. With dense
available, a question whose best cosine is below `RAG_DENSE_MIN` (0.60) is treated as off-topic unless BM25
has a very strong exact match (`RAG_LEXICAL_STRONG`). Optional LLM reranking of the top 8 candidates:
`RAG_RERANK=1` (one extra Gemini call per question).

**Query rewriting.** Follow-ups ("thế còn D+ thì sao?") are rewritten into standalone queries with one small
Gemini call (`RAG_REWRITE=0` disables it); offline it falls back to prepending the previous question.

**Intent routing** (`services/intent.py`). Greetings/thanks/"bạn là ai" get a canned reply (`mode: "smalltalk"`)
and prompt-injection attempts are refused (`mode: "blocked"`), both without retrieval or a model call.
Purely personal questions ("mai mình học gì?") skip retrieval and use tools only.

**Answer cache.** Context-free regulation answers produced by Gemini without tools are cached in memory for
1 hour (keyed by the question's token set, answer language and knowledge-base version). Replays set `cached: true` on `done`.

**Rate limit.** `/chat` and `/chat/stream`: `RATE_LIMIT_PER_MINUTE` (default 20) per client; excess requests get
`429` with `Retry-After`. The Next.js proxy forwards `X-Forwarded-For`, which the backend trusts only from loopback.

**PII.** Feedback text (question, answer, comment) is stored with emails, phone numbers, 8-digit student IDs and
12-digit ID numbers replaced by placeholders.

## Evaluation

```bash
python -m backend.eval                 # hybrid (needs GEMINI_API_KEY; builds the dense index first)
python -m backend.eval --no-dense      # BM25 only, offline and deterministic
python -m backend.eval --rerank -v     # also LLM-rerank; -v lists every case
```

Reports hit@1/3/6 and MRR for (a) the 20 supplied benchmark cases (file-level) and (b) `backend/eval/paraphrases.json`:
colloquial rewordings judged at passage level by heading anchors, plus off-topic questions that retrieval must reject.

## Voice, attachments, handoff, admin, languages (Sprint 4)

**Attachments.** `POST /chat/stream` accepts `"attachment": {"mime": "image/png|image/jpeg|image/webp|application/pdf",
"data": "<base64>", "name": "..."}` (max 4 MB; only this endpoint accepts a large body). The file is sent to Gemini inline
with the question (an empty question defaults to "explain the attachment"). Attachment answers need no `[n]` citation,
are never cached, and when Gemini is unavailable the reply says so instead of falling back to unrelated regulation lines.

**Handoff.** `done` events carry `needs_human: true` when nothing in the knowledge base answers the question. The UI offers
"send to staff"; on confirm it calls `POST /handoff` `{client_id, question, history[]}`, which creates a ticket
(`HT-2026-NNNN`, idempotent per `client_id`), routes it to Đào tạo / CTSV / KHTC by keywords, stores a PII-redacted summary in
`TICKETS_DB` (default `backend/tickets.db`) and notifies through whichever channels are configured:

| Env | Channel |
|---|---|
| `SMTP_HOST` (+ `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`) and `HANDOFF_EMAIL_DAO_TAO` / `_CTSV` / `_KHTC` / `_DEFAULT` | email |
| `HANDOFF_WEBHOOK_URL` | JSON webhook (Slack/Teams-compatible, or a bridge to Zalo OA) |
| neither | ticket stored with channel `outbox` |

**Chat log & admin.** Every answered question is logged (PII-redacted) to `CHATLOG_DB` (default `backend/chatlog.db`).
`GET /admin/analytics` and `GET /admin/tickets` require the `X-Admin-Token` header to equal `ADMIN_TOKEN` (disabled with 403 when unset).
The portal page `/quan-tri?key=<ADMIN_TOKEN>` (set `ADMIN_TOKEN` in `web/.env.local` too) shows volume, answered rate,
satisfaction, top and unanswered questions, document-gap keywords and tickets.

**Languages.** The reply language follows explicit conversation preferences, then the question (`lang` on `done`: `vi`/`en`); canned replies, "no match" text and
default follow-ups exist in both. English retrieval relies on the dense index (cross-lingual); BM25-only mode matches Vietnamese
terms. The chat UI has a VI/EN toggle, Web Speech dictation (`vi-VN`/`en-US`, Chromium/Safari) and read-aloud.
