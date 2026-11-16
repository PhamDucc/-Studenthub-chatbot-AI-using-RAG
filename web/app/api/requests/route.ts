import { backendUrl } from '@/lib/chat-request'

export const dynamic = 'force-dynamic'

async function forward(path: string, init?: RequestInit) {
  try {
    const upstream = await fetch(`${backendUrl()}${path}`, {
      ...init,
      cache: 'no-store',
      signal: AbortSignal.timeout(10_000),
    })
    const data = await upstream.json().catch(() => ({}))
    return Response.json(data, { status: upstream.status })
  } catch (error) {
    console.error('Requests backend unavailable:', error)
    return Response.json({ error: 'Không kết nối được dịch vụ.' }, { status: 503 })
  }
}

export const GET = () => forward('/requests')

export async function POST(request: Request) {
  let payload: unknown
  try {
    payload = await request.json()
  } catch {
    return Response.json({ error: 'JSON không hợp lệ.' }, { status: 400 })
  }
  return forward('/requests', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
