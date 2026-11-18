import { backendUrl } from '@/lib/chat-request'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const upstream = await fetch(`${backendUrl()}/reminders`, { cache: 'no-store', signal: AbortSignal.timeout(5_000) })
    return Response.json(await upstream.json(), { status: upstream.status })
  } catch {
    return Response.json({ reminders: [] })
  }
}
