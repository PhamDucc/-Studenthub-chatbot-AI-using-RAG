import { backendUrl, parseChatRequest } from '@/lib/chat-request'

export const maxDuration = 95
export const dynamic = 'force-dynamic'

/** Proxy the Python SSE stream to the browser without buffering. */
export async function POST(request: Request) {
  const parsed = await parseChatRequest(request)
  if ('error' in parsed) return parsed.error

  // Keep the proxy alive beyond the backend's total request budget, including
  // reading the response body (fetch resolves as soon as headers arrive).
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(new DOMException('Chat timed out', 'TimeoutError')), 90_000)
  const abort = () => controller.abort(request.signal.reason)
  request.signal.addEventListener('abort', abort, { once: true })
  if (request.signal.aborted) abort()
  const cleanup = () => {
    clearTimeout(timeout)
    request.signal.removeEventListener('abort', abort)
  }
  const failure = () => controller.signal.reason?.name === 'TimeoutError'
    ? { code: 'timeout', message: 'Trợ lý phản hồi quá lâu. Bạn có thể thử lại.' }
    : { code: 'unavailable', message: 'Kết nối tới dịch vụ tra cứu bị gián đoạn. Bạn có thể thử lại.' }

  try {
    const upstream = await fetch(`${backendUrl()}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Forwarded-For': request.headers.get('x-forwarded-for') ?? '127.0.0.1',
      },
      body: JSON.stringify(parsed.body),
      cache: 'no-store',
      signal: controller.signal,
    })
    if (!upstream.ok || !upstream.body) {
      const data = await upstream.json().catch(() => null)
      const message = data && typeof data.error === 'string' ? data.error : 'Backend không xử lý được câu hỏi.'
      cleanup()
      return Response.json({
        error: message,
        code: data?.code ?? (upstream.status === 429 ? 'rate_limit' : 'unavailable'),
        retry_after: data?.retry_after,
      }, { status: upstream.ok ? 502 : upstream.status })
    }
    const reader = upstream.body.getReader()
    const encoder = new TextEncoder()
    let cancelled = false
    const body = new ReadableStream<Uint8Array>({
      async pull(stream) {
        try {
          const { done, value } = await reader.read()
          if (cancelled) return
          if (done) {
            cleanup()
            reader.releaseLock()
            stream.close()
          } else {
            stream.enqueue(value)
          }
        } catch {
          if (cancelled) return
          cleanup()
          reader.releaseLock()
          if (!request.signal.aborted) {
            stream.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'error', error: failure() })}\n\n`))
          }
          stream.close()
        }
      },
      async cancel(reason) {
        cancelled = true
        cleanup()
        controller.abort(reason)
        await reader.cancel(reason).catch(() => undefined)
        reader.releaseLock()
      },
    })
    return new Response(body, {
      headers: {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-store, no-transform',
        'X-Accel-Buffering': 'no',
      },
    })
  } catch (error) {
    cleanup()
    if (request.signal.aborted) return new Response(null, { status: 499 })
    console.error('RAG backend unavailable:', error)
    return Response.json(
      { error: failure().message, code: failure().code },
      { status: failure().code === 'timeout' ? 504 : 503 },
    )
  }
}
