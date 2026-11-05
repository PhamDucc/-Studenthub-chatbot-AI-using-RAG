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
      "source": "fees.md"
    }
  ],
  "warning": null,
  "mode": "extractive"
}
```

Field definitions:

- `answer`: final answer or excerpt list
- `sources`: ranked source references
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
