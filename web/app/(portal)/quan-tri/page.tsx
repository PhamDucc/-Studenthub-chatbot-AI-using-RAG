import type { Metadata } from 'next'
import { timingSafeEqual } from 'node:crypto'
import { PageHeader, Card } from '@/components/portal/page-header'
import { backendUrl } from '@/lib/chat-request'

export const metadata: Metadata = { title: 'Quản trị trợ lý AI', robots: { index: false } }
export const dynamic = 'force-dynamic'

type Analytics = {
  days: number
  totals: {
    messages: number; questions: number; unanswered: number; answered_rate: number | null; cached: number
    with_attachment: number; english: number; blocked: number; p50_latency_ms: number | null
    satisfaction: number | null; rated: number
  }
  modes: Record<string, number>
  tools: Record<string, number>
  top_questions: { question: string; count: number }[]
  unanswered: { question: string; count: number; last_seen: string }[]
  document_gaps: { topic: string; questions: number }[]
  feedback_reasons: Record<string, number>
  per_day: { date: string; count: number }[]
}
type Ticket = { code: string; department: string; question: string; status: string; channel: string; created_at: string; student: { name: string } }

const REASONS: Record<string, string> = {
  inaccurate: 'Không chính xác', outdated: 'Thông tin cũ', incomplete: 'Thiếu ý', irrelevant: 'Không liên quan', other: 'Khác',
}
const pct = (value: number | null) => (value === null ? '—' : `${Math.round(value * 100)}%`)

function sameKey(a: string, b: string) {
  const x = Buffer.from(a), y = Buffer.from(b)
  return x.length === y.length && timingSafeEqual(x, y)
}

async function load<T>(path: string, token: string): Promise<T | null> {
  try {
    const response = await fetch(`${backendUrl()}${path}`, {
      headers: { 'X-Admin-Token': token }, cache: 'no-store', signal: AbortSignal.timeout(8_000),
    })
    return response.ok ? ((await response.json()) as T) : null
  } catch {
    return null
  }
}

function Notice({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <PageHeader title="Quản trị trợ lý AI" />
      <Card><div className="p-6 text-sm leading-6"><p className="font-semibold">{title}</p><div className="mt-2 text-muted-foreground">{children}</div></div></Card>
    </div>
  )
}

export default async function AdminPage({ searchParams }: { searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const token = (process.env.ADMIN_TOKEN ?? '').trim()
  if (!token) {
    return (
      <Notice title="Trang quản trị đang tắt">
        Đặt biến môi trường <code>ADMIN_TOKEN</code> cho cả Python backend và Next.js (<code>web/.env.local</code>), khởi động lại, rồi mở
        <code> /quan-tri?key=&lt;ADMIN_TOKEN&gt;</code>.
      </Notice>
    )
  }
  const key = (await searchParams).key
  if (typeof key !== 'string' || !sameKey(key, token)) {
    return <Notice title="Cần mã quản trị">Mở trang này với <code>?key=&lt;ADMIN_TOKEN&gt;</code>.</Notice>
  }

  const [data, tickets] = await Promise.all([load<Analytics>('/admin/analytics', token), load<{ tickets: Ticket[] }>('/admin/tickets', token)])
  if (!data) {
    return <Notice title="Không tải được số liệu">Kiểm tra Python backend đang chạy và <code>ADMIN_TOKEN</code> giống nhau ở hai phía.</Notice>
  }
  const t = data.totals
  const kpis = [
    ['Câu hỏi', String(t.questions), `${data.days} ngày qua`],
    ['Tỉ lệ trả lời được', pct(t.answered_rate), `${t.unanswered} câu chưa trả lời`],
    ['Hài lòng', pct(t.satisfaction), `${t.rated} lượt đánh giá`],
    ['Độ trễ trung vị', t.p50_latency_ms ? `${(t.p50_latency_ms / 1000).toFixed(1)}s` : '—', `${t.cached} lượt từ cache`],
  ]
  const peak = Math.max(1, ...data.per_day.map((d) => d.count))

  return (
    <div>
      <PageHeader title="Quản trị trợ lý AI" description="Câu hỏi phổ biến, khoảng trống tài liệu, mức độ hài lòng và yêu cầu chuyển nhân viên." />
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        {kpis.map(([label, value, hint]) => (
          <Card key={label}><div className="p-5"><p className="text-sm text-muted-foreground">{label}</p><p className="mt-2 text-2xl font-bold">{value}</p><p className="mt-1 text-xs text-muted-foreground">{hint}</p></div></Card>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
        <Card title="Nên bổ sung tài liệu">
          <div className="p-5 text-sm">
            {data.document_gaps.length === 0 ? <p className="text-muted-foreground">Chưa có câu hỏi nào bị bỏ lỡ.</p> : (
              <>
                <p className="text-muted-foreground">Các từ khóa xuất hiện nhiều nhất trong những câu bot không trả lời được:</p>
                <ul className="mt-3 flex flex-wrap gap-2">
                  {data.document_gaps.map((gap) => (
                    <li key={gap.topic} className="rounded-full border bg-accent/50 px-3 py-1 font-medium">{gap.topic} <span className="text-muted-foreground">· {gap.questions}</span></li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </Card>
        <Card title="Câu hỏi chưa trả lời được">
          <ul className="divide-y text-sm">
            {data.unanswered.length === 0 && <li className="p-5 text-muted-foreground">Không có.</li>}
            {data.unanswered.map((item) => (
              <li key={item.question} className="flex items-start justify-between gap-3 px-5 py-3"><span>{item.question}</span><span className="shrink-0 rounded-md bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-800">×{item.count}</span></li>
            ))}
          </ul>
        </Card>
        <Card title="Câu hỏi phổ biến">
          <ol className="divide-y text-sm">
            {data.top_questions.length === 0 && <li className="p-5 text-muted-foreground">Chưa có dữ liệu.</li>}
            {data.top_questions.map((item) => (
              <li key={item.question} className="flex items-start justify-between gap-3 px-5 py-3"><span>{item.question}</span><span className="shrink-0 text-xs font-semibold text-primary">×{item.count}</span></li>
            ))}
          </ol>
        </Card>
        <Card title="Lượt dùng theo ngày">
          <div className="flex h-40 items-end gap-2 p-5" role="img" aria-label="Biểu đồ số tin nhắn theo ngày">
            {data.per_day.length === 0 && <p className="text-sm text-muted-foreground">Chưa có dữ liệu.</p>}
            {data.per_day.map((d) => (
              <div key={d.date} className="flex flex-1 flex-col items-center gap-1" title={`${d.date}: ${d.count}`}>
                <div className="w-full rounded-t bg-primary/80" style={{ height: `${(d.count / peak) * 100}%`, minHeight: 4 }} />
                <span className="text-[10px] text-muted-foreground">{d.date.slice(5)}</span>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Lý do đánh giá chưa tốt">
          <ul className="divide-y text-sm">
            {Object.keys(data.feedback_reasons).length === 0 && <li className="p-5 text-muted-foreground">Chưa có.</li>}
            {Object.entries(data.feedback_reasons).map(([reason, count]) => (
              <li key={reason} className="flex justify-between px-5 py-3"><span>{REASONS[reason] ?? reason}</span><span className="font-semibold">{count}</span></li>
            ))}
          </ul>
        </Card>
        <Card title="Công cụ & chế độ">
          <div className="space-y-3 p-5 text-sm">
            <p className="text-muted-foreground">Chế độ: {Object.entries(data.modes).map(([k, v]) => `${k} ${v}`).join(' · ') || '—'}</p>
            <p className="text-muted-foreground">Công cụ: {Object.entries(data.tools).map(([k, v]) => `${k} ${v}`).join(' · ') || '—'}</p>
            <p className="text-muted-foreground">Tiếng Anh {t.english} · Có đính kèm {t.with_attachment} · Bị chặn {t.blocked}</p>
          </div>
        </Card>
      </div>

      <Card title="Yêu cầu chuyển nhân viên" className="mt-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/60 text-xs text-muted-foreground"><tr><th className="px-5 py-2">Mã</th><th className="px-3 py-2">Phòng ban</th><th className="px-3 py-2">Câu hỏi</th><th className="px-3 py-2">Kênh gửi</th><th className="px-3 py-2">Trạng thái</th></tr></thead>
            <tbody>
              {(tickets?.tickets ?? []).length === 0 && <tr><td colSpan={5} className="px-5 py-4 text-muted-foreground">Chưa có yêu cầu nào.</td></tr>}
              {(tickets?.tickets ?? []).map((ticket) => (
                <tr key={ticket.code} className="border-t"><td className="px-5 py-2 font-medium">{ticket.code}</td><td className="px-3 py-2">{ticket.department}</td><td className="px-3 py-2">{ticket.question}</td><td className="px-3 py-2">{ticket.channel}</td><td className="px-3 py-2">{ticket.status}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
