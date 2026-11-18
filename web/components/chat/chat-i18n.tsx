'use client'

import { createContext, useContext } from 'react'

export type Lang = 'vi' | 'en'

export const STRINGS = {
  vi: {
    subtitle: 'RAG từ tài liệu nội bộ',
    newChat: 'Đoạn chat mới',
    welcomeTitle: 'Xin chào, mình có thể giúp gì?',
    welcomeBody:
      'Tra cứu quy chế, học phí, học bổng, thủ tục — và hỏi về chính bạn: lịch học, GPA, học phí còn nợ, đơn từ. Bạn cũng có thể gửi ảnh hoặc PDF thông báo để mình giải thích. Câu trả lời từ tài liệu đều kèm nguồn kiểm chứng.',
    notice:
      'Quy định chỉ được trả lời từ tài liệu UET; dữ liệu cá nhân lấy trực tiếp từ hệ thống. Trợ lý chỉ soạn đơn, bạn phải bấm xác nhận thì đơn mới được gửi.',
    reminders: 'Việc cần chú ý hôm nay',
    placeholder: 'Hỏi UET AI về học phí, học bổng, quy chế...',
    hint: 'Enter để gửi · Shift + Enter để xuống dòng',
    disclaimer: 'UET AI có thể mắc lỗi. Hãy đối chiếu nguồn trước khi sử dụng thông tin quan trọng.',
    mic: 'Nói để nhập câu hỏi',
    micStop: 'Dừng ghi âm',
    listening: 'Đang nghe…',
    attach: 'Đính kèm ảnh hoặc PDF',
    attachBad: 'Chỉ hỗ trợ ảnh PNG, JPEG, WebP hoặc PDF.',
    attachBig: 'Tệp quá lớn (tối đa 4 MB).',
    attachRemove: 'Bỏ tệp đính kèm',
    defaultAttachQuestion: 'Hãy giải thích nội dung tệp đính kèm.',
    speak: 'Đọc câu trả lời',
    stopSpeaking: 'Dừng đọc',
    handoffTitle: 'Chưa tìm thấy câu trả lời phù hợp',
    handoffBody: 'Mình có thể chuyển câu hỏi cùng tóm tắt hội thoại cho nhân viên hỗ trợ.',
    handoffButton: 'Gửi cho nhân viên hỗ trợ',
    handoffSending: 'Đang gửi…',
    handoffDone: (code: string, dept: string) => `Đã gửi · mã ${code} · ${dept} sẽ phản hồi`,
    handoffError: 'Không gửi được, thử lại nhé.',
    suggestions: [
      { title: 'Học bổng khuyến khích học tập', prompt: 'Điều kiện để nhận học bổng khuyến khích học tập là gì?' },
      { title: 'Học phí và thanh toán', prompt: 'Hướng dẫn quy trình thanh toán học phí bằng mã QR.' },
      { title: 'Thủ tục sinh viên', prompt: 'Thủ tục xin giấy xác nhận sinh viên gồm những bước nào?' },
      { title: 'Học bổng của riêng mình', prompt: 'Với GPA và điểm rèn luyện hiện tại, mình có đủ điều kiện xét học bổng khuyến khích học tập không?' },
      { title: 'Xin bảng điểm', prompt: 'Giúp mình xin 2 bản bảng điểm để nộp hồ sơ học bổng.' },
      { title: 'Quy chế đào tạo', prompt: 'Khi nào sinh viên bị cảnh báo học vụ?' },
    ],
  },
  en: {
    subtitle: 'Answers grounded in UET documents',
    newChat: 'New chat',
    welcomeTitle: 'Hi, how can I help?',
    welcomeBody:
      'Look up regulations, tuition, scholarships and procedures — and ask about yourself: timetable, GPA, outstanding tuition, requests. You can also send a photo or PDF of a notice and I will explain it. Answers from documents come with sources.',
    notice:
      'Regulations are answered only from UET documents; personal data comes straight from the system. I only draft requests: nothing is submitted until you confirm.',
    reminders: "What needs attention today",
    placeholder: 'Ask UET AI about tuition, scholarships, regulations...',
    hint: 'Enter to send · Shift + Enter for a new line',
    disclaimer: 'UET AI can make mistakes. Check the sources before relying on important information.',
    mic: 'Speak your question',
    micStop: 'Stop recording',
    listening: 'Listening…',
    attach: 'Attach an image or PDF',
    attachBad: 'Only PNG, JPEG, WebP images or PDF are supported.',
    attachBig: 'File too large (max 4 MB).',
    attachRemove: 'Remove attachment',
    defaultAttachQuestion: 'Please explain the attached file.',
    speak: 'Read answer aloud',
    stopSpeaking: 'Stop reading',
    handoffTitle: "I couldn't find a good answer",
    handoffBody: 'I can pass your question and a conversation summary to a support staff member.',
    handoffButton: 'Send to support staff',
    handoffSending: 'Sending…',
    handoffDone: (code: string, dept: string) => `Sent · ticket ${code} · ${dept} will reply`,
    handoffError: 'Could not send, please try again.',
    suggestions: [
      { title: 'Academic scholarship', prompt: 'What are the requirements for the academic encouragement scholarship?' },
      { title: 'Tuition and payment', prompt: 'How do I pay tuition with a QR code?' },
      { title: 'Student procedures', prompt: 'What are the steps to request a student certificate?' },
      { title: 'My scholarship chances', prompt: 'With my current GPA and conduct score, am I eligible for the academic scholarship?' },
      { title: 'Request a transcript', prompt: 'Please request 2 copies of my transcript for a scholarship application.' },
      { title: 'Academic regulations', prompt: 'When does a student receive an academic warning?' },
    ],
  },
} as const

export const LangContext = createContext<Lang>('vi')
export const useLang = () => STRINGS[useContext(LangContext)]
export const useLangCode = () => useContext(LangContext)
