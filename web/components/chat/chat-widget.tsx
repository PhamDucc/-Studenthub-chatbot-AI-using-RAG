'use client'

import { useEffect, useRef, useState } from 'react'
import { useChat } from '@ai-sdk/react'
import { Bot, Database, Minus, RotateCcw, SendHorizontal, Sparkles, X } from 'lucide-react'
import { cn } from '@/lib/utils'

const suggestions = [
  'Học phí CLC bao nhiêu một tín chỉ?',
  'Điều kiện nhận học bổng là gì?',
  'Thủ tục xin giấy xác nhận sinh viên?',
  'Khi nào bị cảnh báo học vụ?',
]

export function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const { messages, sendMessage, status, setMessages, error } = useChat()
  const scrollRef = useRef<HTMLDivElement>(null)
  const isBusy = status === 'submitted' || status === 'streaming'

  const lastMessage = messages[messages.length - 1]
  const showTyping =
    status === 'submitted' ||
    (status === 'streaming' && lastMessage?.role === 'assistant' && !lastMessage.parts.some((p) => p.type === 'text' && p.text))

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, showTyping])

  function submit(text: string) {
    const value = text.trim()
    if (!value || isBusy) return
    sendMessage({ text: value })
    setInput('')
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-3 sm:bottom-6 sm:right-6">
      <section
        aria-label="UET AI Assistant"
        className={cn(
          'flex h-[min(600px,calc(100dvh-7rem))] w-[calc(100vw-2rem)] origin-bottom-right flex-col overflow-hidden rounded-2xl border bg-card shadow-2xl transition-all duration-200 sm:w-96',
          open ? 'scale-100 opacity-100' : 'pointer-events-none hidden scale-95 opacity-0',
        )}
      >
        <header className="flex items-center gap-3 bg-primary px-4 py-3 text-primary-foreground">
          <span className="relative flex size-9 items-center justify-center rounded-full bg-gold text-gold-foreground">
            <Bot className="size-5" aria-hidden="true" />
            <span className="absolute -bottom-0.5 -right-0.5 size-3 rounded-full bg-success ring-2 ring-primary" />
          </span>
          <div className="min-w-0 flex-1">
            <h2 className="truncate text-sm font-semibold">UET AI Assistant (RAG)</h2>
            <p className="flex items-center gap-1 text-xs text-primary-foreground/70">
              <Database className="size-3" aria-hidden="true" />
              Quy chế · Học phí · Thủ tục
            </p>
          </div>
          {messages.length > 0 && (
            <button
              type="button"
              onClick={() => setMessages([])}
              className="rounded-md p-1.5 text-primary-foreground/80 hover:bg-primary-foreground/10 hover:text-primary-foreground"
            >
              <RotateCcw className="size-4" aria-hidden="true" />
              <span className="sr-only">Cuộc trò chuyện mới</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="rounded-md p-1.5 text-primary-foreground/80 hover:bg-primary-foreground/10 hover:text-primary-foreground"
          >
            <Minus className="size-4" aria-hidden="true" />
            <span className="sr-only">Thu nhỏ</span>
          </button>
        </header>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto bg-muted/50 px-4 py-4" aria-live="polite">
          <AssistantBubble>
            Xin chào! Mình là trợ lý AI của UET. Mình có thể giải đáp về quy chế đào tạo, học phí và các thủ tục hành chính.
            Bạn cần hỗ trợ gì?
          </AssistantBubble>

          {messages.length === 0 && (
            <div className="flex flex-wrap gap-2 pl-10">
              {suggestions.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => submit(s)}
                  className="rounded-full border bg-card px-3 py-1.5 text-left text-xs text-primary transition hover:border-primary hover:bg-accent"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {messages.map((message) => {
            const text = message.parts.map((p) => (p.type === 'text' ? p.text : '')).join('')
            if (message.role === 'user') {
              return (
                <div key={message.id} className="flex justify-end">
                  <p className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-primary px-3.5 py-2.5 text-sm text-primary-foreground">
                    {text}
                  </p>
                </div>
              )
            }
            if (!text) return null
            return <AssistantBubble key={message.id}>{text}</AssistantBubble>
          })}

          {showTyping && (
            <div className="flex items-end gap-2">
              <BotAvatar />
              <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm border bg-card px-4 py-3" role="status">
                <span className="sr-only">Trợ lý đang soạn câu trả lời</span>
                <span className="typing-dot size-1.5 rounded-full bg-primary" />
                <span className="typing-dot size-1.5 rounded-full bg-primary [animation-delay:0.15s]" />
                <span className="typing-dot size-1.5 rounded-full bg-primary [animation-delay:0.3s]" />
              </div>
            </div>
          )}

          {error && (
            <p className="rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive">
              Đã xảy ra lỗi khi kết nối tới trợ lý. Vui lòng thử lại.
            </p>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            submit(input)
          }}
          className="border-t bg-card p-3"
        >
          <div className="flex items-end gap-2 rounded-xl border bg-muted/60 p-1.5 focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/20">
            <label htmlFor="chat-input" className="sr-only">
              Nhập câu hỏi
            </label>
            <textarea
              id="chat-input"
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  if (e.nativeEvent.isComposing || e.keyCode === 229) return
                  e.preventDefault()
                  submit(input)
                }
              }}
              placeholder="Hỏi về quy chế, học phí, thủ tục..."
              className="max-h-28 min-h-9 flex-1 resize-none bg-transparent px-2 py-2 text-sm outline-none placeholder:text-muted-foreground"
            />
            <button
              type="submit"
              disabled={!input.trim() || isBusy}
              className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground transition hover:bg-primary/90 disabled:opacity-40"
            >
              <SendHorizontal className="size-4" aria-hidden="true" />
              <span className="sr-only">Gửi</span>
            </button>
          </div>
          <p className="mt-2 text-center text-[11px] text-muted-foreground">
            Câu trả lời được truy xuất từ quy chế & thông báo chính thức của UET.
          </p>
        </form>
      </section>

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="group flex items-center gap-2 rounded-full bg-primary py-3 pl-3 pr-3 text-primary-foreground shadow-xl ring-4 ring-primary/15 transition hover:bg-primary/90 sm:pr-5"
      >
        <span className="flex size-8 items-center justify-center rounded-full bg-gold text-gold-foreground">
          {open ? <X className="size-4" aria-hidden="true" /> : <Sparkles className="size-4" aria-hidden="true" />}
        </span>
        <span className="hidden text-sm font-semibold sm:inline">{open ? 'Đóng trợ lý' : 'Hỏi UET AI'}</span>
        <span className="sr-only sm:hidden">{open ? 'Đóng trợ lý AI' : 'Mở trợ lý AI'}</span>
      </button>
    </div>
  )
}

function BotAvatar() {
  return (
    <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-gold">
      <Bot className="size-4" aria-hidden="true" />
    </span>
  )
}

function AssistantBubble({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-end gap-2">
      <BotAvatar />
      <p className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-bl-sm border bg-card px-3.5 py-2.5 text-sm leading-relaxed text-card-foreground">
        {children}
      </p>
    </div>
  )
}
