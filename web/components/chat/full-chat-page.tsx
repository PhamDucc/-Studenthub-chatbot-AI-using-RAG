'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Bot,
  BellRing,
  CalendarDays,
  Check,
  CheckCircle2,
  Loader2,
  Wrench,
  ChevronDown,
  Clipboard,
  Database,
  FileText,
  History,
  Languages,
  LifeBuoy,
  Menu,
  Mic,
  Paperclip,
  Volume2,
  VolumeX,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  RotateCcw,
  SendHorizontal,
  ThumbsDown,
  ThumbsUp,
  Sparkles,
  Trash2,
  UserRound,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Markdown } from './markdown'
import { LangContext, STRINGS, useLang, type Lang } from './chat-i18n'
import {
  ATTACHMENT_TYPES,
  MAX_ATTACHMENT_BYTES,
  readAttachment,
  useDictation,
  useSpeech,
  type PendingAttachment,
} from './voice'

type ChatSource = {
  number: number
  title: string
  heading: string
  source: string
  score?: number
  excerpt?: string
  text?: string
  highlight?: string
}

type Message = {
  id: string
  role: 'user' | 'assistant'
  text: string
  sources?: ChatSource[]
  followUps?: string[]
  mode?: string
  question?: string
  streaming?: boolean
  failed?: boolean
  feedback?: 'up' | 'down'
  steps?: string[]
  action?: ServiceAction
  attachment?: { name: string; mime: string }
  needsHuman?: boolean
  lang?: string
  handoff?: { status: 'idle' | 'sending' | 'done' | 'error'; code?: string; department?: string }
}

type ServiceAction = {
  client_id: string
  request_type: string
  label: string
  fee: string
  days: string
  reason: string
  copies: number
  status?: 'pending' | 'sending' | 'done' | 'cancelled' | 'error'
  requestId?: string
}

type Reminder = { kind: string; title: string; detail: string; urgent: boolean; prompt: string }

type ChatFailure = {
  code?: string
  message?: string
  retry_after?: number | null
}

function failureMessage(error: ChatFailure, lang: Lang): string {
  const english = lang === 'en'
  switch (error.code) {
    case 'timeout':
      return english
        ? 'The assistant took too long to respond. Please try again; this does not mean you have run out of tokens.'
        : 'Trợ lý phản hồi quá lâu. Bạn có thể thử lại; lỗi này không có nghĩa là đã hết token.'
    case 'rate_limit': {
      const wait = typeof error.retry_after === 'number' && error.retry_after > 0
        ? Math.ceil(error.retry_after) : null
      return english
        ? `The AI service has reached a request or token quota. ${wait ? `Wait ${wait} seconds before retrying.` : 'Please wait and check your Gemini quota if this persists.'}`
        : `Dịch vụ AI đang chạm giới hạn lượt gọi hoặc token. ${wait ? `Chờ ${wait} giây rồi thử lại.` : 'Hãy chờ rồi thử lại; nếu vẫn lỗi, kiểm tra quota Gemini.'}`
    }
    case 'auth':
      return english
        ? 'The AI service rejected the API key. Check the backend API key configuration.'
        : 'Dịch vụ AI từ chối API key. Cần kiểm tra cấu hình API key của backend.'
    case 'model':
      return english
        ? 'The configured AI model is unavailable. Check the model name and access permissions.'
        : 'Model AI đang cấu hình không khả dụng. Cần kiểm tra tên model và quyền truy cập.'
    case 'unavailable':
      return english
        ? 'The assistant is temporarily unavailable or the connection was interrupted. Please try again shortly.'
        : 'Trợ lý tạm thời không khả dụng hoặc kết nối bị gián đoạn. Bạn thử lại sau một lát nhé.'
    default:
      return error.message || (english ? 'Could not receive an answer. Please try again.' : 'Chưa nhận được câu trả lời. Bạn thử lại nhé.')
  }
}

type Conversation = {
  id: string
  title: string
  updatedAt: number
  messages: Message[]
  responseLanguage?: Lang
}

type StreamEvent =
  | { type: 'sources'; sources: ChatSource[] }
  | { type: 'delta'; text: string }
  | { type: 'replace'; text: string }
  | { type: 'tool'; name: string; label: string }
  | { type: 'action'; action: ServiceAction }
  | {
      type: 'done'
      mode: string
      warning: string | null
      follow_ups: string[]
      tools?: string[]
      cited?: number[]
      needs_human?: boolean
      lang?: string
      response_language?: Lang | null
      error?: ChatFailure | null
    }
  | { type: 'error'; error: string | ChatFailure }

const FEEDBACK_REASONS = [
  { value: 'inaccurate', label: 'Không chính xác' },
  { value: 'outdated', label: 'Thông tin cũ' },
  { value: 'incomplete', label: 'Thiếu ý' },
  { value: 'irrelevant', label: 'Không liên quan' },
]

async function* readEvents(response: Response): AsyncGenerator<StreamEvent> {
  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let reachedEnd = false
  const parseFrame = (frame: string): StreamEvent | null => {
    const data = frame.split(/\r?\n/).filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trimStart()).join('\n')
    return data ? JSON.parse(data) as StreamEvent : null
  }
  try {
    while (true) {
      const { done, value } = await reader.read()
      // Mark EOF before yielding final frames: a consumer may stop at a final
      // frame, but the transport has already completed successfully.
      if (done) reachedEnd = true
      buffer += done ? decoder.decode() : decoder.decode(value, { stream: true })
      const frames = buffer.split(/\r?\n\r?\n/)
      buffer = frames.pop() ?? ''
      for (const frame of frames) {
        const event = parseFrame(frame)
        if (event) yield event
      }
      if (done) {
        const event = parseFrame(buffer)
        if (event) yield event
        break
      }
    }
  } finally {
    if (!reachedEnd) await reader.cancel().catch(() => undefined)
    reader.releaseLock()
  }
}

const STORAGE_KEY = 'uet-ai-conversations-v1'

const suggestionIcons = [Sparkles, Database, FileText, Sparkles, FileText, MessageSquareText]

function createConversation(): Conversation {
  return {
    id: crypto.randomUUID(),
    title: 'Cuộc trò chuyện mới',
    updatedAt: Date.now(),
    messages: [],
  }
}

export function FullChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState('')
  const [input, setInput] = useState('')
  const [isBusy, setIsBusy] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [citation, setCitation] = useState<{ messageId: string; number: number } | null>(null)
  const [lang, setLang] = useState<Lang>('vi')
  const [attachment, setAttachment] = useState<PendingAttachment | null>(null)
  const [attachError, setAttachError] = useState<string | null>(null)
  const t = STRINGS[lang]
  const speech = useSpeech(lang)
  const scrollRef = useRef<HTMLDivElement>(null)
  const textAreaRef = useRef<HTMLTextAreaElement>(null)
  const requestRef = useRef<AbortController | null>(null)
  const hydratedRef = useRef(false)

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      const parsed = saved ? JSON.parse(saved) as Conversation[] : []
      if (Array.isArray(parsed) && parsed.length > 0) {
        setConversations(parsed)
        setActiveId(parsed[0].id)
      } else {
        const first = createConversation()
        setConversations([first])
        setActiveId(first.id)
      }
    } catch {
      const first = createConversation()
      setConversations([first])
      setActiveId(first.id)
    }
    hydratedRef.current = true
  }, [])

  useEffect(() => {
    if (hydratedRef.current && conversations.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations.slice(0, 30)))
    }
  }, [conversations])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [conversations, activeId, isBusy])

  useEffect(() => () => requestRef.current?.abort(), [])

  useEffect(() => {
    try {
      const saved = localStorage.getItem('uet-ai-lang')
      if (saved === 'vi' || saved === 'en') setLang(saved)
      else if (navigator.language.toLowerCase().startsWith('en')) setLang('en')
    } catch { /* storage unavailable */ }
  }, [])

  function switchLang() {
    const next: Lang = lang === 'vi' ? 'en' : 'vi'
    setLang(next)
    try { localStorage.setItem('uet-ai-lang', next) } catch { /* ignore */ }
  }

  async function pickFile(file: File | undefined) {
    if (!file) return
    setAttachError(null)
    if (!ATTACHMENT_TYPES.includes(file.type)) return setAttachError(t.attachBad)
    if (file.size > MAX_ATTACHMENT_BYTES) return setAttachError(t.attachBig)
    try { setAttachment(await readAttachment(file)) } catch { setAttachError(t.attachBad) }
  }

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeId),
    [conversations, activeId],
  )

  function updateActive(updater: (conversation: Conversation) => Conversation) {
    setConversations((current) => current.map((conversation) => (
      conversation.id === activeId ? updater(conversation) : conversation
    )))
  }

  function startNewChat() {
    requestRef.current?.abort()
    const next = createConversation()
    setConversations((current) => [next, ...current])
    setActiveId(next.id)
    setInput('')
    setError(null)
    setIsBusy(false)
    setMobileHistoryOpen(false)
    requestAnimationFrame(() => textAreaRef.current?.focus())
  }

  function removeConversation(id: string) {
    if (conversations.length === 1) {
      const replacement = createConversation()
      setConversations([replacement])
      setActiveId(replacement.id)
      return
    }
    const remaining = conversations.filter((conversation) => conversation.id !== id)
    setConversations(remaining)
    if (id === activeId) setActiveId(remaining[0].id)
  }

  async function submit(rawText: string) {
    const sent = attachment
    const question = rawText.trim() || (sent ? t.defaultAttachQuestion : '')
    if (!question || isBusy || !activeConversation) return

    const controller = new AbortController()
    requestRef.current = controller
    const userMessage: Message = {
      id: crypto.randomUUID(), role: 'user', text: question,
      ...(sent ? { attachment: { name: sent.name, mime: sent.mime } } : {}),
    }
    const history = activeConversation.messages.filter((message) => !message.failed && message.text.trim()).slice(-6)
    const conversationId = activeConversation.id

    setConversations((current) => current.map((conversation) => {
      if (conversation.id !== conversationId) return conversation
      return {
        ...conversation,
        title: conversation.messages.length === 0
          ? question.slice(0, 46) + (question.length > 46 ? '…' : '')
          : conversation.title,
        updatedAt: Date.now(),
        messages: [...conversation.messages, userMessage],
      }
    }))
    setInput('')
    setAttachment(null)
    setAttachError(null)
    setError(null)
    setIsBusy(true)

    const assistantId = crypto.randomUUID()
    const patch = (changes: Partial<Message>) => setConversations((current) => current.map((conversation) => (
      conversation.id === conversationId
        ? {
            ...conversation,
            messages: conversation.messages.map((item) => (item.id === assistantId ? { ...item, ...changes } : item)),
          }
        : conversation
    )))
    let text = ''
    let steps: string[] = []
    let created = false
    let completed = false
    const timeout = window.setTimeout(() => controller.abort(new DOMException('Chat timed out', 'TimeoutError')), 95_000)
    const ensureMessage = (initial: Partial<Message>) => {
      if (created) return
      created = true
      const message: Message = { id: assistantId, role: 'assistant', text: '', streaming: true, question, ...initial }
      setConversations((current) => current.map((conversation) => (
        conversation.id === conversationId
          ? { ...conversation, updatedAt: Date.now(), messages: [...conversation.messages, message] }
          : conversation
      )))
    }

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          ...(activeConversation.responseLanguage ? { response_language: activeConversation.responseLanguage } : {}),
          history: history.map((message) => ({
            role: message.role,
            content: message.text.slice(0, 1000),
          })),
          ...(sent ? { attachment: { mime: sent.mime, data: sent.data, name: sent.name } } : {}),
        }),
        signal: controller.signal,
      })
      if (!response.ok || !response.body) {
        const result = await response.json().catch(() => ({}))
        throw new Error(failureMessage({
          code: result.code ?? (response.status === 429 ? 'rate_limit' : undefined),
          message: typeof result.error === 'string' ? result.error : undefined,
          retry_after: result.retry_after,
        }, lang))
      }
      for await (const event of readEvents(response)) {
        // The done frame completes the answer. Drain the HTTP body normally so
        // a successful request is not reported as cancelled in the browser.
        if (completed) continue
        if (event.type === 'sources') {
          ensureMessage({ sources: event.sources })
        } else if (event.type === 'delta') {
          ensureMessage({})
          text += event.text
          patch({ text })
        } else if (event.type === 'replace') {
          ensureMessage({})
          text = event.text
          steps = []
          patch({ text, steps: [], action: undefined })
        } else if (event.type === 'tool') {
          ensureMessage({})
          steps = [...steps, event.label]
          patch({ steps })
        } else if (event.type === 'action') {
          ensureMessage({})
          patch({ action: { ...event.action, status: 'pending' } })
        } else if (event.type === 'done') {
          completed = true
          ensureMessage({})
          // Response language is an explicit conversation preference from the
          // backend, independent of the UI language and this answer's language.
          if (event.response_language === 'vi' || event.response_language === 'en' || event.response_language === null) {
            const responseLanguage = event.response_language ?? undefined
            setConversations((current) => current.map((conversation) => (
              conversation.id === conversationId ? { ...conversation, responseLanguage } : conversation
            )))
          }
          const personalOnly = (event.tools?.length ?? 0) > 0 && (event.cited?.length ?? 0) === 0
          patch({
            streaming: false,
            mode: event.mode,
            followUps: event.follow_ups,
            needsHuman: !!event.needs_human,
            lang: event.lang,
            failed: !!event.error,
            ...(personalOnly ? { sources: [] } : {}),
          })
          if (event.error) {
            patch({ followUps: [], action: undefined, sources: [] })
            setError(failureMessage(event.error, lang))
          } else if (event.warning) {
            patch({ failed: true, followUps: [] })
            setError(lang === 'en'
              ? 'The AI could not finish an answer. Any document excerpts shown are reference material, not a complete answer.'
              : 'AI chưa tạo được câu trả lời. Các đoạn trích đang hiển thị chỉ để tham khảo, chưa phải câu trả lời hoàn chỉnh.')
          }
        } else if (event.type === 'error') {
          throw new Error(typeof event.error === 'string' ? event.error : failureMessage(event.error, lang))
        }
      }
      if (!completed) throw new Error(failureMessage({ code: 'unavailable' }, lang))
      if (created) patch({ streaming: false })
    } catch (cause) {
      // A transport failure after done cannot invalidate a complete answer.
      if (!completed) {
        if (created) patch({ streaming: false, failed: true, followUps: [], action: undefined, sources: [] })
        if (controller.signal.reason?.name === 'TimeoutError') {
          setError(failureMessage({ code: 'timeout' }, lang))
        } else if (!controller.signal.aborted) {
          setError(cause instanceof TypeError || cause instanceof SyntaxError
            ? failureMessage({ code: 'unavailable' }, lang)
            : cause instanceof Error ? cause.message : failureMessage({ code: 'unavailable' }, lang))
        }
      }
    } finally {
      window.clearTimeout(timeout)
      if (requestRef.current === controller) {
        requestRef.current = null
        setIsBusy(false)
      }
    }
  }

  function setFeedback(message: Message, rating: 'up' | 'down', reason?: string) {
    setConversations((current) => current.map((conversation) => (
      conversation.id === activeId
        ? {
            ...conversation,
            messages: conversation.messages.map((item) => (item.id === message.id ? { ...item, feedback: rating } : item)),
          }
        : conversation
    )))
    fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message_id: message.id,
        rating,
        reason,
        question: message.question,
        answer: message.text,
        sources: message.sources?.map((source) => source.source),
        mode: message.mode,
      }),
    }).catch(() => undefined)
  }

  async function requestHandoff(message: Message) {
    const conversation = conversations.find((item) => item.id === activeId)
    if (!conversation || !message.question) return
    const index = conversation.messages.findIndex((item) => item.id === message.id)
    const history = conversation.messages.slice(Math.max(0, index - 6), index).filter((item) => item.text.trim())
    const update = (handoff: Message['handoff']) => setConversations((current) => current.map((item) => (
      item.id === activeId
        ? { ...item, messages: item.messages.map((m) => (m.id === message.id ? { ...m, handoff } : m)) }
        : item
    )))
    update({ status: 'sending' })
    try {
      const response = await fetch('/api/handoff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: message.id,
          question: message.question,
          history: history.map((item) => ({ role: item.role, content: item.text.slice(0, 1000) })),
        }),
      })
      const result = await response.json()
      if (!response.ok) throw new Error(result.error)
      update({ status: 'done', code: result.ticket.code, department: result.ticket.department_name })
    } catch {
      update({ status: 'error' })
    }
  }

  async function confirmAction(message: Message, confirmed: boolean) {
    const action = message.action
    if (!action) return
    const update = (changes: Partial<ServiceAction>) => setConversations((current) => current.map((conversation) => (
      conversation.id === activeId
        ? {
            ...conversation,
            messages: conversation.messages.map((item) => (
              item.id === message.id && item.action ? { ...item, action: { ...item.action, ...changes } } : item
            )),
          }
        : conversation
    )))
    if (!confirmed) {
      update({ status: 'cancelled' })
      return
    }
    update({ status: 'sending' })
    try {
      const response = await fetch('/api/requests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: action.client_id,
          request_type: action.request_type,
          reason: action.reason,
          copies: action.copies,
        }),
      })
      const result = await response.json()
      if (!response.ok) throw new Error(result.error)
      update({ status: 'done', requestId: result.request.id })
    } catch {
      update({ status: 'error' })
    }
  }

  async function copyAnswer(message: Message) {
    await navigator.clipboard.writeText(message.text)
    setCopiedId(message.id)
    window.setTimeout(() => setCopiedId(null), 1500)
  }

  return (
    <LangContext.Provider value={lang}>
    <div className="relative flex h-full min-h-0 overflow-hidden bg-background">
      <ConversationHistory
        conversations={conversations}
        activeId={activeId}
        open={sidebarOpen}
        mobileOpen={mobileHistoryOpen}
        onToggle={() => setSidebarOpen((value) => !value)}
        onMobileClose={() => setMobileHistoryOpen(false)}
        onNew={startNewChat}
        onSelect={(id) => {
          setActiveId(id)
          setMobileHistoryOpen(false)
          setError(null)
        }}
        onRemove={removeConversation}
      />

      <section className="relative flex min-w-0 flex-1 flex-col bg-[radial-gradient(circle_at_top,rgba(223,232,250,0.55),transparent_38%)]">
        <header className="flex h-14 shrink-0 items-center gap-3 border-b bg-background/85 px-4 backdrop-blur-xl">
          <button
            type="button"
            onClick={() => setMobileHistoryOpen(true)}
            className="rounded-lg p-2 hover:bg-muted md:hidden"
            aria-label="Mở lịch sử trò chuyện"
          >
            <Menu className="size-5" />
          </button>
          {!sidebarOpen && (
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="hidden rounded-lg p-2 hover:bg-muted md:block"
              aria-label="Mở lịch sử trò chuyện"
            >
              <PanelLeftOpen className="size-5" />
            </button>
          )}
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <span className="flex size-8 items-center justify-center rounded-xl bg-primary text-gold">
              <Sparkles className="size-4" />
            </span>
            <div className="min-w-0">
              <h1 className="truncate text-sm font-semibold">UET AI Assistant</h1>
              <p className="flex items-center gap-1 text-[11px] text-muted-foreground">
                <span className="size-1.5 rounded-full bg-emerald-500" />
                {t.subtitle}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={switchLang}
            className="flex items-center gap-1.5 rounded-lg border bg-card px-2.5 py-2 text-xs font-semibold shadow-sm hover:bg-muted"
            aria-label={lang === 'vi' ? 'Switch to English' : 'Chuyển sang tiếng Việt'}
          >
            <Languages className="size-4" />
            {lang === 'vi' ? 'VI' : 'EN'}
          </button>
          {activeConversation && activeConversation.messages.length > 0 && (
            <button
              type="button"
              onClick={startNewChat}
              className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2 text-xs font-medium shadow-sm hover:bg-muted"
            >
              <Plus className="size-4" />
              <span className="hidden sm:inline">{t.newChat}</span>
            </button>
          )}
        </header>

        <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto">
          {!activeConversation || activeConversation.messages.length === 0 ? (
            <WelcomeScreen onSelect={submit} />
          ) : (
            <div className="mx-auto w-full max-w-4xl px-4 pb-40 pt-8 sm:px-8">
              {activeConversation.messages.map((message, position) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  isLast={position === activeConversation.messages.length - 1}
                  copied={copiedId === message.id}
                  onCopy={() => copyAnswer(message)}
                  onCite={(number) => setCitation({ messageId: message.id, number })}
                  onFeedback={(rating, reason) => setFeedback(message, rating, reason)}
                  onFollowUp={submit}
                  onConfirm={(confirmed) => confirmAction(message, confirmed)}
                  onHandoff={() => requestHandoff(message)}
                  speaking={speech.speakingId === message.id}
                  canSpeak={speech.supported}
                  onSpeak={() => speech.toggle(message.id, message.text, message.lang)}
                  busy={isBusy}
                />
              ))}
              {isBusy && activeConversation.messages.at(-1)?.role !== 'assistant' && <ThinkingMessage />}
              {error && <ErrorNotice message={error} lang={lang} onRetry={() => {
                const lastQuestion = [...activeConversation.messages].reverse().find((item) => item.role === 'user')
                if (lastQuestion) submit(lastQuestion.text)
              }} />}
            </div>
          )}
        </div>

        <Composer
          value={input}
          busy={isBusy}
          textareaRef={textAreaRef}
          onChange={setInput}
          onSubmit={() => submit(input)}
          onStop={() => requestRef.current?.abort()}
          lang={lang}
          attachment={attachment}
          attachError={attachError}
          onPickFile={pickFile}
          onRemoveAttachment={() => { setAttachment(null); setAttachError(null) }}
        />
      </section>
      {citation && (() => {
        const source = activeConversation?.messages.find((item) => item.id === citation.messageId)
          ?.sources?.find((item) => item.number === citation.number)
        return source ? <SourceDrawer source={source} onClose={() => setCitation(null)} /> : null
      })()}
    </div>
    </LangContext.Provider>
  )
}

function ConversationHistory({
  conversations,
  activeId,
  open,
  mobileOpen,
  onToggle,
  onMobileClose,
  onNew,
  onSelect,
  onRemove,
}: {
  conversations: Conversation[]
  activeId: string
  open: boolean
  mobileOpen: boolean
  onToggle: () => void
  onMobileClose: () => void
  onNew: () => void
  onSelect: (id: string) => void
  onRemove: (id: string) => void
}) {
  const content = (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center justify-between border-b px-3">
        <p className="flex items-center gap-2 px-2 text-sm font-semibold">
          <History className="size-4 text-primary" />
          Lịch sử
        </p>
        <button type="button" onClick={onToggle} className="hidden rounded-lg p-2 hover:bg-muted md:block" aria-label="Thu gọn lịch sử">
          <PanelLeftClose className="size-4" />
        </button>
        <button type="button" onClick={onMobileClose} className="rounded-lg p-2 hover:bg-muted md:hidden" aria-label="Đóng lịch sử">
          <X className="size-5" />
        </button>
      </div>
      <div className="p-3">
        <button
          type="button"
          onClick={onNew}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-3 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90"
        >
          <Plus className="size-4" />
          Cuộc trò chuyện mới
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-3">
        <p className="px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">Gần đây</p>
        {conversations.map((conversation) => (
          <div
            key={conversation.id}
            className={cn(
              'group flex items-center rounded-xl transition',
              conversation.id === activeId ? 'bg-accent text-accent-foreground' : 'hover:bg-muted',
            )}
          >
            <button
              type="button"
              onClick={() => onSelect(conversation.id)}
              className="min-w-0 flex-1 px-3 py-2.5 text-left"
            >
              <p className="truncate text-sm font-medium">{conversation.title}</p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                {conversation.messages.length} tin nhắn
              </p>
            </button>
            <button
              type="button"
              onClick={() => onRemove(conversation.id)}
              className="mr-2 rounded-md p-1.5 text-muted-foreground opacity-0 hover:bg-background hover:text-destructive group-hover:opacity-100 focus:opacity-100"
              aria-label={`Xóa ${conversation.title}`}
            >
              <Trash2 className="size-3.5" />
            </button>
          </div>
        ))}
      </div>
      <div className="border-t p-3">
        <div className="rounded-xl bg-muted/70 p-3 text-xs text-muted-foreground">
          <p className="flex items-center gap-2 font-semibold text-foreground">
            <Database className="size-4 text-primary" />
            Kho tri thức UET
          </p>
          <p className="mt-1.5 leading-relaxed">6 tài liệu · câu trả lời kèm nguồn kiểm chứng</p>
        </div>
      </div>
    </div>
  )

  return (
    <>
      <aside className={cn('hidden shrink-0 overflow-hidden border-r bg-card transition-[width] duration-200 md:block', open ? 'w-72' : 'w-0')}>
        <div className="h-full w-72">{content}</div>
      </aside>
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button type="button" className="absolute inset-0 bg-foreground/35 backdrop-blur-sm" onClick={onMobileClose} aria-label="Đóng lịch sử" />
          <aside className="absolute inset-y-0 left-0 w-[min(88vw,20rem)] bg-card shadow-2xl">{content}</aside>
        </div>
      )}
    </>
  )
}

function WelcomeScreen({ onSelect }: { onSelect: (prompt: string) => void }) {
  const t = useLang()
  return (
    <div className="mx-auto flex min-h-full w-full max-w-4xl flex-col justify-center px-5 pb-32 pt-10 sm:px-8">
      <div className="mb-8">
        <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-primary text-gold shadow-lg shadow-primary/20">
          <Sparkles className="size-7" />
        </span>
        <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
          {t.welcomeTitle}
        </h2>
        <p className="mt-3 max-w-2xl text-pretty text-sm leading-6 text-muted-foreground sm:text-base">
          {t.welcomeBody}
        </p>
      </div>
      <Reminders onSelect={onSelect} />
      <div className="grid gap-3 sm:grid-cols-2">
        {t.suggestions.map((suggestion, index) => {
          const Icon = suggestionIcons[index] ?? Sparkles
          return (
            <button
              key={suggestion.prompt}
              type="button"
              onClick={() => onSelect(suggestion.prompt)}
              className="group rounded-2xl border bg-card p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-primary/35 hover:shadow-md"
            >
              <span className="mb-4 flex size-9 items-center justify-center rounded-xl bg-accent text-primary">
                <Icon className="size-4" />
              </span>
              <p className="text-sm font-semibold">{suggestion.title}</p>
              <p className="mt-1 line-clamp-2 text-xs leading-5 text-muted-foreground">{suggestion.prompt}</p>
            </button>
          )
        })}
      </div>
      <div className="mt-6 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50/80 px-3 py-2.5 text-xs leading-5 text-amber-900">
        <Database className="mt-0.5 size-4 shrink-0" />
        {t.notice}
      </div>
    </div>
  )
}

function ChatMessage({
  message,
  isLast,
  copied,
  busy,
  onCopy,
  onCite,
  onFeedback,
  onFollowUp,
  onConfirm,
  onHandoff,
  speaking,
  canSpeak,
  onSpeak,
}: {
  message: Message
  isLast: boolean
  copied: boolean
  busy: boolean
  onCopy: () => void
  onCite: (number: number) => void
  onFeedback: (rating: 'up' | 'down', reason?: string) => void
  onFollowUp: (question: string) => void
  onConfirm: (confirmed: boolean) => void
  onHandoff: () => void
  speaking: boolean
  canSpeak: boolean
  onSpeak: () => void
}) {
  const t = useLang()
  const [reasonOpen, setReasonOpen] = useState(false)

  if (message.role === 'user') {
    return (
      <article className="mb-8 flex justify-end gap-3">
        <div className="max-w-[85%] rounded-3xl rounded-tr-md bg-primary px-5 py-3 text-sm leading-6 text-primary-foreground shadow-sm">
          {message.attachment && (
            <p className="mb-1.5 flex items-center gap-1.5 rounded-lg bg-primary-foreground/15 px-2 py-1 text-xs">
              <Paperclip className="size-3.5 shrink-0" />
              <span className="truncate">{message.attachment.name}</span>
            </p>
          )}
          <p className="whitespace-pre-wrap">{message.text}</p>
        </div>
        <span className="mt-1 flex size-8 shrink-0 items-center justify-center rounded-full bg-secondary text-primary">
          <UserRound className="size-4" />
        </span>
      </article>
    )
  }

  return (
    <article className="mb-10 flex gap-3 sm:gap-4">
      <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary text-gold shadow-sm">
        <Bot className="size-4" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="mb-2 text-xs font-semibold text-primary">UET AI Assistant</p>
        {message.steps && message.steps.length > 0 && <ToolSteps steps={message.steps} streaming={!!message.streaming} />}
        {message.text ? (
          <div className={cn(message.streaming && 'streaming-caret')}>
            <Markdown text={message.text} sourceCount={message.sources?.length ?? 0} onCite={onCite} />
          </div>
        ) : message.streaming ? (
          <p className="text-sm text-muted-foreground">Đang soạn câu trả lời…</p>
        ) : null}
        {!message.streaming && message.needsHuman && isLast && (
          <div className="my-4 flex flex-wrap items-center gap-3 rounded-2xl border border-amber-300/70 bg-amber-50/80 p-4">
            <LifeBuoy className="size-5 shrink-0 text-amber-700" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-amber-950">{t.handoffTitle}</p>
              <p className="mt-0.5 text-xs leading-5 text-amber-900/80">{t.handoffBody}</p>
            </div>
            {message.handoff?.status === 'done' ? (
              <p className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                <CheckCircle2 className="size-4" />
                {t.handoffDone(message.handoff.code ?? '', message.handoff.department ?? '')}
              </p>
            ) : (
              <button
                type="button"
                disabled={message.handoff?.status === 'sending'}
                onClick={onHandoff}
                className="flex items-center gap-2 rounded-lg bg-amber-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-amber-700 disabled:opacity-60"
              >
                {message.handoff?.status === 'sending' && <Loader2 className="size-3.5 animate-spin" />}
                {message.handoff?.status === 'sending' ? t.handoffSending : t.handoffButton}
              </button>
            )}
            {message.handoff?.status === 'error' && <p className="w-full text-xs text-destructive">{t.handoffError}</p>}
          </div>
        )}
        {message.action && <ActionCard action={message.action} onConfirm={onConfirm} />}
        {!message.streaming && message.sources && message.sources.length > 0 && (
          <Sources sources={message.sources} onOpen={onCite} />
        )}
        {!message.streaming && (
          <div className="mt-3 flex items-center gap-1">
            <button type="button" onClick={onCopy} className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground" aria-label="Sao chép câu trả lời">
              {copied ? <Check className="size-4 text-emerald-600" /> : <Clipboard className="size-4" />}
            </button>
            {canSpeak && message.text && (
              <button
                type="button"
                onClick={onSpeak}
                className={cn('rounded-lg p-2 hover:bg-muted', speaking ? 'text-primary' : 'text-muted-foreground hover:text-foreground')}
                aria-label={speaking ? t.stopSpeaking : t.speak}
                aria-pressed={speaking}
              >
                {speaking ? <VolumeX className="size-4" /> : <Volume2 className="size-4" />}
              </button>
            )}
            {!message.failed && (
              <>
                <button
                  type="button"
                  onClick={() => { setReasonOpen(false); onFeedback('up') }}
                  className={cn('rounded-lg p-2 hover:bg-muted', message.feedback === 'up' ? 'text-emerald-600' : 'text-muted-foreground hover:text-foreground')}
                  aria-label="Câu trả lời hữu ích"
                  aria-pressed={message.feedback === 'up'}
                >
                  <ThumbsUp className="size-4" />
                </button>
                <button
                  type="button"
                  onClick={() => { setReasonOpen(true); onFeedback('down') }}
                  className={cn('rounded-lg p-2 hover:bg-muted', message.feedback === 'down' ? 'text-destructive' : 'text-muted-foreground hover:text-foreground')}
                  aria-label="Câu trả lời chưa tốt"
                  aria-pressed={message.feedback === 'down'}
                >
                  <ThumbsDown className="size-4" />
                </button>
              </>
            )}
          </div>
        )}
        {!message.failed && reasonOpen && message.feedback === 'down' && (
          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs">
            <span className="text-muted-foreground">Vấn đề là gì?</span>
            {FEEDBACK_REASONS.map((reason) => (
              <button
                key={reason.value}
                type="button"
                onClick={() => { onFeedback('down', reason.value); setReasonOpen(false) }}
                className="rounded-full border bg-card px-3 py-1 font-medium hover:border-primary/40 hover:bg-accent"
              >
                {reason.label}
              </button>
            ))}
          </div>
        )}
        {isLast && !busy && !message.streaming && message.followUps && message.followUps.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {message.followUps.map((question) => (
              <button
                key={question}
                type="button"
                onClick={() => onFollowUp(question)}
                className="flex items-center gap-1.5 rounded-full border bg-card px-3.5 py-2 text-left text-xs font-medium shadow-sm transition hover:-translate-y-0.5 hover:border-primary/40 hover:bg-accent"
              >
                <Sparkles className="size-3.5 shrink-0 text-primary" />
                {question}
              </button>
            ))}
          </div>
        )}
      </div>
    </article>
  )
}

function Sources({ sources, onOpen }: { sources: ChatSource[]; onOpen: (number: number) => void }) {
  return (
    <details className="group mt-5 overflow-hidden rounded-2xl border bg-card shadow-sm">
      <summary className="flex cursor-pointer list-none items-center gap-2 px-4 py-3 text-xs font-semibold">
        <Database className="size-4 text-primary" />
        {sources.length} nguồn tham khảo
        <ChevronDown className="ml-auto size-4 transition group-open:rotate-180" />
      </summary>
      <div className="space-y-2 border-t p-3">
        {sources.map((source) => (
          <button
            type="button"
            key={`${source.number}-${source.source}-${source.heading}`}
            onClick={() => onOpen(source.number)}
            className="block w-full rounded-xl bg-muted/70 p-3 text-left transition hover:bg-accent"
          >
            <div className="flex items-start gap-2">
              <span className="flex size-6 shrink-0 items-center justify-center rounded-md bg-primary text-[10px] font-bold text-primary-foreground">
                {source.number}
              </span>
              <div className="min-w-0">
                <p className="truncate text-xs font-semibold">{source.title}</p>
                <p className="mt-0.5 text-[11px] text-muted-foreground">{source.heading}</p>
                {source.excerpt && <p className="mt-2 line-clamp-3 text-xs leading-5 text-muted-foreground">{source.excerpt}</p>}
              </div>
            </div>
          </button>
        ))}
      </div>
    </details>
  )
}

function ToolSteps({ steps, streaming }: { steps: string[]; streaming: boolean }) {
  return (
    <div className="mb-3 flex flex-wrap gap-1.5" aria-label="Các bước tra cứu dữ liệu">
      {steps.map((step, index) => (
        <span
          key={`${step}-${index}`}
          className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-accent/60 px-2.5 py-1 text-[11px] font-medium text-primary"
        >
          {streaming && index === steps.length - 1
            ? <Loader2 className="size-3 animate-spin" />
            : <Wrench className="size-3" />}
          Đã tra cứu: {step}
        </span>
      ))}
    </div>
  )
}

function ActionCard({ action, onConfirm }: { action: ServiceAction; onConfirm: (confirmed: boolean) => void }) {
  const status = action.status ?? 'pending'
  return (
    <div className="my-4 overflow-hidden rounded-2xl border border-primary/25 bg-card shadow-sm">
      <div className="flex items-center gap-2 border-b bg-accent/50 px-4 py-2.5 text-xs font-semibold text-primary">
        <FileText className="size-4" />
        Đơn đã soạn sẵn · cần bạn xác nhận
      </div>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 px-4 py-3 text-[13px]">
        <dt className="text-muted-foreground">Loại đơn</dt><dd className="font-medium">{action.label}</dd>
        <dt className="text-muted-foreground">Số bản</dt><dd>{action.copies}</dd>
        <dt className="text-muted-foreground">Lệ phí</dt><dd>{action.fee}</dd>
        <dt className="text-muted-foreground">Thời gian xử lý</dt><dd>{action.days}</dd>
        <dt className="text-muted-foreground">Lý do</dt><dd>{action.reason}</dd>
      </dl>
      <div className="flex items-center gap-2 border-t px-4 py-3">
        {status === 'done' ? (
          <p className="flex items-center gap-2 text-sm font-medium text-emerald-700">
            <CheckCircle2 className="size-4" />
            Đã gửi đơn · mã {action.requestId}
          </p>
        ) : status === 'cancelled' ? (
          <p className="text-sm text-muted-foreground">Đã huỷ, đơn chưa được gửi.</p>
        ) : (
          <>
            <button
              type="button"
              disabled={status === 'sending'}
              onClick={() => onConfirm(true)}
              className="flex items-center gap-2 rounded-lg bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
            >
              {status === 'sending' ? <Loader2 className="size-3.5 animate-spin" /> : <Check className="size-3.5" />}
              Xác nhận gửi
            </button>
            <button
              type="button"
              disabled={status === 'sending'}
              onClick={() => onConfirm(false)}
              className="rounded-lg border px-3.5 py-2 text-xs font-semibold hover:bg-muted disabled:opacity-60"
            >
              Huỷ
            </button>
            {status === 'error' && <p className="text-xs text-destructive">Không gửi được, thử lại nhé.</p>}
          </>
        )}
      </div>
    </div>
  )
}

function Reminders({ onSelect }: { onSelect: (prompt: string) => void }) {
  const t = useLang()
  const [items, setItems] = useState<Reminder[]>([])
  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/reminders', { signal: controller.signal })
      .then((response) => response.json())
      .then((data) => setItems(Array.isArray(data.reminders) ? data.reminders : []))
      .catch(() => undefined)
    return () => controller.abort()
  }, [])
  if (items.length === 0) return null
  return (
    <div className="mb-6">
      <p className="mb-2 flex items-center gap-2 text-xs font-semibold text-muted-foreground">
        <BellRing className="size-3.5" />
        {t.reminders}
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        {items.slice(0, 4).map((item) => (
          <button
            key={item.title + item.detail}
            type="button"
            onClick={() => onSelect(item.prompt)}
            className={cn(
              'flex items-start gap-3 rounded-xl border p-3 text-left transition hover:-translate-y-0.5 hover:shadow-md',
              item.urgent ? 'border-amber-300 bg-amber-50/80' : 'bg-card',
            )}
          >
            <span className={cn('mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg', item.urgent ? 'bg-amber-200 text-amber-900' : 'bg-accent text-primary')}>
              {item.kind === 'class' ? <CalendarDays className="size-4" /> : <BellRing className="size-4" />}
            </span>
            <span className="min-w-0">
              <span className="block text-sm font-semibold">{item.title}</span>
              <span className="mt-0.5 line-clamp-2 block text-xs leading-5 text-muted-foreground">{item.detail}</span>
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

function SourceDrawer({ source, onClose }: { source: ChatSource; onClose: () => void }) {
  const body = source.text ?? source.excerpt ?? ''
  const at = source.highlight ? body.indexOf(source.highlight) : -1
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])
  return (
    <div className="fixed inset-0 z-50">
      <button type="button" className="absolute inset-0 bg-foreground/30 backdrop-blur-[2px]" onClick={onClose} aria-label="Đóng nguồn" />
      <aside className="absolute inset-y-0 right-0 flex w-[min(94vw,28rem)] flex-col bg-card shadow-2xl" role="dialog" aria-label={`Nguồn ${source.number}`}>
        <header className="flex items-start gap-3 border-b p-4">
          <span className="flex size-7 shrink-0 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">{source.number}</span>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold">{source.title}</p>
            <p className="mt-0.5 text-xs text-muted-foreground">{source.heading}</p>
            <p className="mt-1 truncate text-[11px] text-muted-foreground/80">{source.source}</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-lg p-1.5 hover:bg-muted" aria-label="Đóng"><X className="size-4" /></button>
        </header>
        <div className="min-h-0 flex-1 overflow-y-auto p-4">
          {source.highlight && (
            <div className="mb-4 rounded-xl border border-amber-300/60 bg-amber-50 p-3 text-xs leading-5 text-amber-950">
              <p className="mb-1 font-semibold">Đoạn khớp nhất với câu hỏi</p>
              {source.highlight}
            </div>
          )}
          <p className="whitespace-pre-wrap text-[13px] leading-6 text-foreground/85">
            {at >= 0 ? (
              <>
                {body.slice(0, at)}
                <mark className="rounded bg-amber-200/80 px-0.5 text-foreground">{source.highlight}</mark>
                {body.slice(at + (source.highlight?.length ?? 0))}
              </>
            ) : body}
          </p>
        </div>
      </aside>
    </div>
  )
}

function ThinkingMessage() {
  return (
    <div className="mb-10 flex gap-4" role="status">
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary text-gold">
        <Bot className="size-4" />
      </span>
      <div>
        <p className="mb-2 text-xs font-semibold text-primary">Đang tra cứu tài liệu</p>
        <div className="flex items-center gap-1.5 rounded-2xl border bg-card px-4 py-3 shadow-sm">
          {[0, 1, 2].map((item) => (
            <span key={item} className="typing-dot size-1.5 rounded-full bg-primary" style={{ animationDelay: `${item * 0.15}s` }} />
          ))}
        </div>
      </div>
    </div>
  )
}

function ErrorNotice({ message, lang, onRetry }: { message: string; lang: Lang; onRetry: () => void }) {
  return (
    <div className="ml-0 mt-4 flex items-center gap-3 rounded-2xl border border-destructive/25 bg-destructive/5 p-4 text-sm text-destructive sm:ml-13">
      <p className="flex-1">{message}</p>
      <button type="button" onClick={onRetry} className="flex shrink-0 items-center gap-1 rounded-lg border border-destructive/20 px-2.5 py-1.5 text-xs font-semibold hover:bg-destructive/10">
        <RotateCcw className="size-3.5" />
        {lang === 'en' ? 'Retry' : 'Thử lại'}
      </button>
    </div>
  )
}

function Composer({
  value,
  busy,
  textareaRef,
  onChange,
  onSubmit,
  onStop,
  lang,
  attachment,
  attachError,
  onPickFile,
  onRemoveAttachment,
}: {
  lang: Lang
  attachment: PendingAttachment | null
  attachError: string | null
  onPickFile: (file: File | undefined) => void
  onRemoveAttachment: () => void
  value: string
  busy: boolean
  textareaRef: React.RefObject<HTMLTextAreaElement | null>
  onChange: (value: string) => void
  onSubmit: () => void
  onStop: () => void
}) {
  const t = useLang()
  const fileRef = useRef<HTMLInputElement>(null)
  const dictation = useDictation(lang, value, onChange)
  const canSend = !!value.trim() || !!attachment
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-background via-background/95 to-transparent px-4 pb-4 pt-12 sm:px-8 sm:pb-6">
      <form
        onSubmit={(event) => {
          event.preventDefault()
          onSubmit()
        }}
        className="pointer-events-auto mx-auto max-w-4xl"
      >
        <div className="rounded-2xl border bg-card p-2 shadow-[0_12px_40px_rgba(30,58,123,0.12)] focus-within:border-primary/50 focus-within:ring-4 focus-within:ring-primary/5">
          {attachment && (
            <div className="mx-1 mb-1 mt-1 flex w-fit max-w-full items-center gap-2 rounded-lg border bg-accent/50 px-2.5 py-1.5 text-xs">
              {attachment.mime.startsWith('image/')
                // eslint-disable-next-line @next/next/no-img-element
                ? <img src={`data:${attachment.mime};base64,${attachment.data}`} alt="" className="size-8 rounded object-cover" />
                : <FileText className="size-4 text-primary" />}
              <span className="truncate font-medium">{attachment.name}</span>
              <button type="button" onClick={onRemoveAttachment} className="rounded p-0.5 hover:bg-muted" aria-label={t.attachRemove}>
                <X className="size-3.5" />
              </button>
            </div>
          )}
          <textarea
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={(event) => {
              onChange(event.target.value)
              event.target.style.height = 'auto'
              event.target.style.height = `${Math.min(event.target.scrollHeight, 160)}px`
            }}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                if (event.nativeEvent.isComposing || event.keyCode === 229) return
                event.preventDefault()
                onSubmit()
              }
            }}
            placeholder={dictation.listening ? t.listening : t.placeholder}
            className="max-h-40 min-h-12 w-full resize-none bg-transparent px-3 py-3 text-sm leading-6 outline-none placeholder:text-muted-foreground"
            aria-label="Nhập câu hỏi cho UET AI"
          />
          {attachError && <p className="px-3 pb-1 text-xs text-destructive sm:hidden">{attachError}</p>}
          <div className="flex items-center justify-between px-2 pb-1">
            <div className="flex items-center gap-1">
              <input
                ref={fileRef}
                type="file"
                accept={ATTACHMENT_TYPES.join(',')}
                className="hidden"
                onChange={(event) => { onPickFile(event.target.files?.[0]); event.target.value = '' }}
              />
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
                aria-label={t.attach}
                title={t.attach}
              >
                <Paperclip className="size-4" />
              </button>
              {dictation.supported && (
                <button
                  type="button"
                  onClick={dictation.toggle}
                  className={cn(
                    'rounded-lg p-2 hover:bg-muted',
                    dictation.listening ? 'animate-pulse bg-destructive/10 text-destructive' : 'text-muted-foreground hover:text-foreground',
                  )}
                  aria-label={dictation.listening ? t.micStop : t.mic}
                  aria-pressed={dictation.listening}
                  title={dictation.listening ? t.micStop : t.mic}
                >
                  <Mic className="size-4" />
                </button>
              )}
              <p className="ml-1 hidden text-[10px] text-muted-foreground sm:block">{attachError ? <span className="text-destructive">{attachError}</span> : t.hint}</p>
            </div>
            <div className="ml-auto">
              {busy ? (
                <button type="button" onClick={onStop} className="flex size-9 items-center justify-center rounded-xl bg-foreground text-background" aria-label="Dừng trả lời">
                  <span className="size-3 rounded-sm bg-background" />
                </button>
              ) : (
                <button type="submit" disabled={!canSend} className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground transition hover:bg-primary/90 disabled:opacity-35" aria-label="Gửi câu hỏi">
                  <SendHorizontal className="size-4" />
                </button>
              )}
            </div>
          </div>
        </div>
        <p className="mt-2 text-center text-[10px] text-muted-foreground">{t.disclaimer}</p>
      </form>
    </div>
  )
}
