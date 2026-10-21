import Link from 'next/link'
import { ArrowRight, ClipboardList, CreditCard, FileClock } from 'lucide-react'

const actions = [
  {
    label: 'Đăng ký học phần',
    description: 'Mở đến 05/11/2026',
    href: '/lich-hoc',
    icon: ClipboardList,
    tone: 'bg-primary text-primary-foreground',
  },
  {
    label: 'Nộp học phí',
    description: 'Còn 10 ngày · 8.450.000đ',
    href: '/don-tu',
    icon: CreditCard,
    tone: 'bg-gold text-gold-foreground',
  },
  {
    label: 'Xem lịch thi',
    description: 'Thi giữa kỳ từ 02/11',
    href: '/lich-hoc',
    icon: FileClock,
    tone: 'bg-accent text-primary',
  },
]

export function QuickActions() {
  return (
    <section aria-labelledby="quick-actions-title">
      <h2 id="quick-actions-title" className="mb-3 text-base font-semibold">
        Thao tác nhanh
      </h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {actions.map((a) => {
          const Icon = a.icon
          return (
            <Link
              key={a.label}
              href={a.href}
              className="group flex items-center gap-4 rounded-xl border bg-card p-4 shadow-xs transition hover:border-primary/40 hover:shadow-md focus-visible:ring-3 focus-visible:ring-ring/40 focus-visible:outline-none"
            >
              <span className={`flex size-11 shrink-0 items-center justify-center rounded-lg ${a.tone}`}>
                <Icon className="size-5" aria-hidden="true" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold">{a.label}</span>
                <span className="block truncate text-xs text-muted-foreground">{a.description}</span>
              </span>
              <ArrowRight
                className="size-4 text-muted-foreground transition group-hover:translate-x-0.5 group-hover:text-primary"
                aria-hidden="true"
              />
            </Link>
          )
        })}
      </div>
    </section>
  )
}
