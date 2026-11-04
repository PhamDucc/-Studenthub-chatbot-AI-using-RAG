import {
  createUIMessageStream,
  createUIMessageStreamResponse,
} from 'ai'

export const maxDuration = 180

export async function POST(req: Request) {
  let body: { messages?: unknown }

  try {
    body = await req.json()

    if (
      !body ||
      !Array.isArray(body.messages) ||
      body.messages.length === 0
    ) {
      return Response.json(
        { error: 'Thiếu lịch sử hoặc câu hỏi.' },
        { status: 400 },
      )
    }
  } catch {
    return Response.json(
      { error: 'JSON không hợp lệ.' },
      { status: 400 },
    )
  }

  try {
    const baseUrl =
      process.env.CHATBOT_API_URL || 'http://127.0.0.1:8000'

    const upstream = await fetch(
      `${baseUrl.replace(/\/$/, '')}/api/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },

        // Python nhận lịch sử và lấy tối đa 5 lượt trước.
        body: JSON.stringify({
          messages: body.messages,
        }),

        signal: AbortSignal.timeout(170_000),
        cache: 'no-store',
      },
    )

    if (!upstream.ok) {
      console.error(
        'FastAPI /api/chat status:',
        upstream.status,
      )

      return Response.json(
        { error: 'Không xử lý được câu hỏi. Vui lòng thử lại.' },
        { status: upstream.status },
      )
    }

    const data = await upstream.json()

    if (
      typeof data.response !== 'string' ||
      !Array.isArray(data.sources)
    ) {
      throw new Error('Phản hồi FastAPI không hợp lệ')
    }

    const sources = data.sources.filter(
      (source: unknown): source is string =>
        typeof source === 'string',
    )

    const text =
      data.response +
      (sources.length
        ? `\n\nNguồn: ${sources.join(', ')}`
        : '')

    // Chuyển JSON của FastAPI sang định dạng useChat() cần.
    const stream = createUIMessageStream({
      execute: ({ writer }) => {
        writer.write({
          type: 'text-start',
          id: 'answer',
        })

        writer.write({
          type: 'text-delta',
          id: 'answer',
          delta: text,
        })

        writer.write({
          type: 'text-end',
          id: 'answer',
        })

        writer.write({
          type: 'data-handoff',
          data: {
            needs_human: data.needs_human === true,
            reason: data.handoff_reason ?? null,
          },
        })
      },
    })

    return createUIMessageStreamResponse({ stream })
  } catch {
    return Response.json(
      {
        error: 'Không kết nối được backend hoặc hết thời gian chờ.',
      },
      { status: 503 },
    )
  }
}