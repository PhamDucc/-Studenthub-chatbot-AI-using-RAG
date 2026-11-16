import { backendUrl, parseChatRequest } from '@/lib/chat-request'

export const maxDuration = 60
export const dynamic = 'force-dynamic'

/** Proxy the Python SSE stream to the browser without buffering. */
export async function POST(request: Request) {
  const parsed = await parseChatRequest(request)
  if ('error' in parsed) return parsed.error

  try {
    const upstream = await fetch(`${backendUrl()}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Forwarded-For': request.headers.get('x-forwarded-for') ?? '127.0.0.1',
      },
      body: JSON.stringify(parsed.body),
      cache: 'no-store',
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(55_000)]),
    })
    if (!upstream.ok || !upstream.body) {
      const data = await upstream.json().catch(() => null)
      const message = data && typeof data.error === 'string' ? data.error : 'Backend không xử lý được câu hỏi.'
      return Response.json({ error: message }, { status: upstream.status || 502 })
    }
    return new Response(upstream.body, {
      headers: {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-store, no-transform',
        'X-Accel-Buffering': 'no',
      },
    })
  } catch (error) {
    if (request.signal.aborted) return new Response(null, { status: 499 })
    console.error('RAG backend unavailable:', error)
    return Response.json(
      { error: 'Không kết nối được dịch vụ tra cứu. Hãy kiểm tra Python backend.' },
      { status: 503 },
    )
  }
}
