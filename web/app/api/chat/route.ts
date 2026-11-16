import { backendUrl, parseChatRequest } from '@/lib/chat-request'

export const maxDuration = 35

export async function POST(request: Request) {
  const parsed = await parseChatRequest(request)
  if ('error' in parsed) return parsed.error

  try {
    const upstream = await fetch(`${backendUrl()}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Forwarded-For': request.headers.get('x-forwarded-for') ?? '127.0.0.1',
      },
      body: JSON.stringify(parsed.body),
      cache: 'no-store',
      signal: AbortSignal.timeout(30_000),
    })
    const data: unknown = await upstream.json()
    if (typeof data !== 'object' || data === null) {
      throw new Error('Phản hồi backend không hợp lệ.')
    }
    if (!upstream.ok) {
      const message = 'error' in data && typeof data.error === 'string'
        ? data.error
        : 'Backend không xử lý được câu hỏi.'
      return Response.json({ error: message }, { status: upstream.status })
    }
    return Response.json(data, { headers: { 'Cache-Control': 'no-store' } })
  } catch (error) {
    console.error('RAG backend unavailable:', error)
    return Response.json(
      { error: 'Không kết nối được dịch vụ tra cứu. Hãy kiểm tra Python backend.' },
      { status: 503 },
    )
  }
}
