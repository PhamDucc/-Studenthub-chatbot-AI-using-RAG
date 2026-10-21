'use client'

import { useState } from 'react'
import { CheckCircle2, Paperclip, Send } from 'lucide-react'
import { requestHistory, requestTypes, student, type ServiceRequest } from '@/lib/data'
import { Card } from '@/components/portal/page-header'
import { cn } from '@/lib/utils'

const statusStyle: Record<ServiceRequest['status'], string> = {
  'Đang xử lý': 'bg-amber-50 text-amber-700',
  'Đã duyệt': 'bg-sky-50 text-sky-700',
  'Hoàn thành': 'bg-emerald-50 text-emerald-700',
  'Từ chối': 'bg-rose-50 text-rose-700',
}

const inputClass =
  'h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20'

export function ServiceRequests() {
  const [type, setType] = useState(requestTypes[0].value)
  const [history, setHistory] = useState<ServiceRequest[]>(requestHistory)
  const [submitted, setSubmitted] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const selected = requestTypes.find((t) => t.value === type)!

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = e.currentTarget
    const data = new FormData(form)
    const reason = String(data.get('reason') ?? '').trim()
    const copies = Number(data.get('copies'))

    if (reason.length < 10) {
      setError('Vui lòng mô tả lý do / mục đích tối thiểu 10 ký tự.')
      return
    }
    if (!Number.isInteger(copies) || copies < 1 || copies > 10) {
      setError('Số bản phải từ 1 đến 10.')
      return
    }

    const id = `DV-2026-${String(413 + history.length).padStart(4, '0')}`
    setHistory((h) => [
      { id, type: selected.label, submittedAt: '21/10/2026', status: 'Đang xử lý', copies },
      ...h,
    ])
    setSubmitted(id)
    setError(null)
    form.reset()
    setType(requestTypes[0].value)
  }

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
      <div className="xl:col-span-3">
        <Card title="Tạo yêu cầu mới">
          <form onSubmit={handleSubmit} className="flex flex-col gap-5 p-5" noValidate>
            {submitted && (
              <div
                role="status"
                className="flex items-start gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800"
              >
                <CheckCircle2 className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
                <p>
                  Đã gửi yêu cầu <strong>{submitted}</strong>. Bạn sẽ nhận thông báo qua email khi đơn được xử lý.
                </p>
              </div>
            )}

            <fieldset>
              <legend className="mb-2 text-sm font-medium">Loại đơn / dịch vụ</legend>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {requestTypes.map((t) => (
                  <label
                    key={t.value}
                    className={cn(
                      'flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition',
                      type === t.value ? 'border-primary bg-accent/60 ring-1 ring-primary' : 'hover:bg-muted/60',
                    )}
                  >
                    <input
                      type="radio"
                      name="type"
                      value={t.value}
                      checked={type === t.value}
                      onChange={() => setType(t.value)}
                      className="mt-0.5 accent-primary"
                    />
                    <span>
                      <span className="block text-sm font-medium">{t.label}</span>
                      <span className="block text-xs text-muted-foreground">
                        {t.fee} · {t.days}
                      </span>
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="fullname" className="mb-1.5 block text-sm font-medium">
                  Họ và tên
                </label>
                <input id="fullname" readOnly value={student.name} className={cn(inputClass, 'bg-muted')} />
              </div>
              <div>
                <label htmlFor="sid" className="mb-1.5 block text-sm font-medium">
                  Mã sinh viên
                </label>
                <input id="sid" readOnly value={student.studentId} className={cn(inputClass, 'bg-muted')} />
              </div>
              <div>
                <label htmlFor="copies" className="mb-1.5 block text-sm font-medium">
                  Số bản
                </label>
                <input id="copies" name="copies" type="number" min={1} max={10} defaultValue={1} className={inputClass} />
              </div>
              <div>
                <label htmlFor="receive" className="mb-1.5 block text-sm font-medium">
                  Hình thức nhận
                </label>
                <select id="receive" name="receive" className={inputClass} defaultValue="truc-tiep">
                  <option value="truc-tiep">Nhận trực tiếp tại Phòng CTSV</option>
                  <option value="ban-mem">Bản mềm qua email VNU</option>
                  <option value="buu-dien">Gửi qua bưu điện</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="reason" className="mb-1.5 block text-sm font-medium">
                Lý do / Mục đích sử dụng
              </label>
              <textarea
                id="reason"
                name="reason"
                rows={4}
                required
                aria-invalid={!!error}
                aria-describedby={error ? 'form-error' : undefined}
                placeholder="Ví dụ: Bổ sung hồ sơ xin học bổng, hồ sơ vay vốn ngân hàng chính sách..."
                className="w-full rounded-lg border bg-background p-3 text-sm outline-none transition focus:border-ring focus:ring-3 focus:ring-ring/20 aria-invalid:border-destructive"
              />
            </div>

            <div>
              <label
                htmlFor="attachment"
                className="flex cursor-pointer flex-col items-center gap-1 rounded-lg border border-dashed px-4 py-6 text-center transition hover:bg-muted/60"
              >
                <Paperclip className="size-5 text-muted-foreground" aria-hidden="true" />
                <span className="text-sm font-medium">Đính kèm minh chứng (không bắt buộc)</span>
                <span className="text-xs text-muted-foreground">PDF, JPG, PNG · tối đa 5MB</span>
              </label>
              <input id="attachment" name="attachment" type="file" accept=".pdf,.jpg,.jpeg,.png" className="sr-only" />
            </div>

            {error && (
              <p id="form-error" role="alert" className="text-sm font-medium text-destructive">
                {error}
              </p>
            )}

            <div className="flex flex-col-reverse gap-3 border-t pt-5 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs text-muted-foreground">
                Lệ phí: <strong className="text-foreground">{selected.fee}</strong> · Thời gian xử lý: {selected.days}
              </p>
              <button
                type="submit"
                className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary px-5 text-sm font-semibold text-primary-foreground shadow-sm transition hover:bg-primary/90 focus-visible:ring-3 focus-visible:ring-ring/40 focus-visible:outline-none"
              >
                <Send className="size-4" aria-hidden="true" />
                Gửi yêu cầu
              </button>
            </div>
          </form>
        </Card>
      </div>

      <div className="xl:col-span-2">
        <Card title="Lịch sử yêu cầu">
          <ul className="divide-y">
            {history.map((r) => (
              <li key={r.id} className="flex items-start justify-between gap-3 px-5 py-4">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-pretty">{r.type}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {r.id} · {r.submittedAt} · {r.copies} bản
                  </p>
                </div>
                <span className={cn('shrink-0 rounded-full px-2.5 py-0.5 text-[11px] font-semibold', statusStyle[r.status])}>
                  {r.status}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  )
}
