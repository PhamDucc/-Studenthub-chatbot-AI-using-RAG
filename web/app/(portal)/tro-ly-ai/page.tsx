import type { Metadata } from 'next'
import { FullChatPage } from '@/components/chat/full-chat-page'

export const metadata: Metadata = {
  title: 'Trợ lý UET AI',
  description: 'Tra cứu quy chế, học phí và thủ tục sinh viên từ tài liệu UET.',
}

export default function AiAssistantPage() {
  return <FullChatPage />
}
