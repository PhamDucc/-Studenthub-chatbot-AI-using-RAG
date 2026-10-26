import {
  streamText,
  convertToModelMessages,
  createUIMessageStreamResponse,
  toUIMessageStream,
  type UIMessage,
} from 'ai'

export const maxDuration = 30

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json()

  const result = streamText({
    model: 'google/gemini-1.5-flash',
    system: `Bạn là "UET AI Assistant", trợ lý ảo của Trường Đại học Công nghệ - ĐHQGHN (UET), hỗ trợ sinh viên về quy chế đào tạo, học phí và thủ tục hành chính.

Quy tắc:
- Trả lời bằng ngôn ngữ người dùng sử dụng (mặc định tiếng Việt), ngắn gọn, thân thiện, rõ ràng.
- Hỗ trợ giải đáp thắc mắc về học vụ, lịch trình đào tạo, thủ tục sinh viên theo thông tin của trường.
- Nếu gặp câu hỏi về trường hợp cá biệt hoặc thông tin cần tra cứu hồ sơ chính xác, khuyên sinh viên liên hệ trực tiếp Phòng Đào tạo (P.213-G2) hoặc Phòng Công tác Sinh viên (P.107-G2). Không tự bịa số liệu.
- Định dạng câu trả lời bằng văn bản ngắn gọn, dùng gạch đầu dòng "- " khi liệt kê.`,
    messages: await convertToModelMessages(messages),
  })

  return createUIMessageStreamResponse({
    stream: toUIMessageStream({ stream: result.stream }),
  })
}