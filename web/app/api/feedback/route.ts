import { backendUrl } from '@/lib/chat-request'

export async function POST(request: Request) {
  let payload: unknown
  try {
    payload = await request.json()
  } catch {
    return Response.json({ error: 'JSON không hợp lệ.' }, { status: 400 })
  }
  try {
    const upstream = await fetch(`${backendUrl()}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      cache: 'no-store',
      signal: AbortSignal.timeout(10_000),
    })
    const data = await upstream.json().catch(() => ({}))
    return Response.json(data, { status: upstream.status })
  } catch (error) {
    console.error('Feedback backend unavailable:', error)
    return Response.json({ error: 'Không gửi được phản hồi.' }, { status: 503 })
  }
}
