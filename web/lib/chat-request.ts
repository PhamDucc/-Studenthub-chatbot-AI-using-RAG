export type ChatTurn = { role: 'user' | 'assistant'; content: string }
export type Attachment = { mime: string; data: string; name?: string }

const ATTACHMENT_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'application/pdf']

export const backendUrl = () =>
  (process.env.PYTHON_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

/** Validate the browser payload; returns the body for the Python API or an error response. */
export async function parseChatRequest(
  request: Request,
): Promise<{ body: { question: string; history: ChatTurn[]; attachment?: Attachment; response_language?: 'vi' | 'en' } } | { error: Response }> {
  let payload: { question?: unknown; history?: unknown; attachment?: unknown; response_language?: unknown }
  try {
    payload = await request.json()
  } catch {
    return { error: Response.json({ error: 'JSON không hợp lệ.' }, { status: 400 }) }
  }
  if (payload.response_language !== undefined && payload.response_language !== 'vi' && payload.response_language !== 'en') {
    return { error: Response.json({ error: 'Ngôn ngữ trả lời không hợp lệ (vi hoặc en).' }, { status: 400 }) }
  }
  let attachment: Attachment | undefined
  if (payload.attachment !== undefined && payload.attachment !== null) {
    const a = payload.attachment as Partial<Attachment>
    if (typeof a.mime !== 'string' || !ATTACHMENT_TYPES.includes(a.mime) || typeof a.data !== 'string' || !a.data) {
      return { error: Response.json({ error: 'Chỉ hỗ trợ ảnh PNG, JPEG, WebP hoặc PDF.' }, { status: 400 }) }
    }
    attachment = { mime: a.mime, data: a.data, name: typeof a.name === 'string' ? a.name : undefined }
  }
  const question = typeof payload.question === 'string' ? payload.question.trim() : ''
  if (!question && !attachment) {
    return { error: Response.json({ error: 'Câu hỏi không được để trống.' }, { status: 400 }) }
  }
  const history: ChatTurn[] = Array.isArray(payload.history)
    ? payload.history
        .filter(
          (turn): turn is ChatTurn =>
            typeof turn === 'object' && turn !== null &&
            'role' in turn && (turn.role === 'user' || turn.role === 'assistant') &&
            'content' in turn && typeof turn.content === 'string',
        )
        .slice(-6)
    : []
  return { body: {
    question,
    history,
    ...(attachment ? { attachment } : {}),
    ...(payload.response_language ? { response_language: payload.response_language } : {}),
  } }
}
