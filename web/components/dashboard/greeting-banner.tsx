import { CalendarCheck } from 'lucide-react'
import { student } from '@/lib/data'

export function GreetingBanner() {
  return (
    <section className="relative overflow-hidden rounded-2xl bg-primary px-6 py-7 text-primary-foreground md:px-8 md:py-8">
      <div
        className="pointer-events-none absolute -top-16 -right-16 size-64 rounded-full bg-white/5"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute -right-4 -bottom-24 size-48 rounded-full bg-gold/15"
        aria-hidden="true"
      />
      <div className="relative flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium text-primary-foreground/70">{student.semester}</p>
          <h1 className="mt-1 text-2xl font-bold text-balance md:text-3xl">
            Chào mừng trở lại, {student.name}
          </h1>
          <p className="mt-2 max-w-xl text-sm leading-relaxed text-primary-foreground/80 text-pretty">
            {student.major} · {student.className}. Hôm nay bạn có 2 buổi học và 1 hạn nộp học phí sắp đến.
          </p>
        </div>
        <div className="flex items-center gap-3 self-start rounded-xl bg-white/10 px-4 py-3 md:self-auto">
          <CalendarCheck className="size-5 text-gold" aria-hidden="true" />
          <div className="leading-tight">
            <p className="text-xs text-primary-foreground/70">Hôm nay</p>
            <p className="text-sm font-semibold">Thứ Tư, 21/10/2026</p>
          </div>
        </div>
      </div>
    </section>
  )
}
