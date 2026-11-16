import { backendUrl, parseChatRequest } from '@/lib/chat-request'

/** Create a staff ticket for a question the assistant could not answer. */
export async function POST(request: Request) {
  const raw = await request.clone().json().catch(() => null)
  const parsed = await parseChatRequest(request)
  if ('error' in parsed) return parsed.error
  const clientId = raw && typeof raw.client_id === 'string' ? raw.client_id : ''
  try {
    const upstream = await fetch(`${backendUrl()}/handoff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: clientId, question: parsed.body.question, history: parsed.body.history }),
      cache: 'no-store',
      signal: AbortSignal.timeout(20_000),
    })
    return Response.json(await upstream.json().catch(() => ({})), { status: upstream.status })
  } catch (error) {
    console.error('Handoff backend unavailable:', error)
    return Response.json({ error: 'Không gửi được yêu cầu hỗ trợ.' }, { status: 503 })
  }
}
