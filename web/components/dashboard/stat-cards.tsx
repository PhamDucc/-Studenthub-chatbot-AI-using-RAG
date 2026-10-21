import { Award, BookOpen, Layers, TrendingUp } from 'lucide-react'
import { student } from '@/lib/data'

export function StatCards() {
  const creditPct = Math.round((student.credits / student.totalCredits) * 100)

  const stats = [
    {
      label: 'GPA tích lũy',
      value: student.gpa.toFixed(2),
      suffix: '/ 4.0',
      note: '+0.06 so với kỳ trước',
      icon: TrendingUp,
      progress: (student.gpa / 4) * 100,
    },
    {
      label: 'Tín chỉ tích lũy',
      value: String(student.credits),
      suffix: `/ ${student.totalCredits}`,
      note: `Hoàn thành ${creditPct}% chương trình`,
      icon: Layers,
      progress: creditPct,
    },
    {
      label: 'Xếp loại học lực',
      value: student.ranking,
      suffix: '',
      note: 'Đủ điều kiện xét học bổng',
      icon: Award,
    },
    {
      label: 'Môn học trong kỳ',
      value: String(student.currentCourses),
      suffix: 'môn',
      note: '17 tín chỉ đã đăng ký',
      icon: BookOpen,
    },
  ]

  return (
    <section aria-label="Thống kê nhanh" className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((s) => {
        const Icon = s.icon
        return (
          <article key={s.label} className="flex flex-col gap-3 rounded-xl border bg-card p-5 shadow-xs">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-muted-foreground">{s.label}</p>
              <span className="flex size-9 items-center justify-center rounded-lg bg-accent text-primary">
                <Icon className="size-[18px]" aria-hidden="true" />
              </span>
            </div>
            <p className="flex items-baseline gap-1.5">
              <span className="text-3xl font-bold text-foreground">{s.value}</span>
              {s.suffix && <span className="text-sm font-medium text-muted-foreground">{s.suffix}</span>}
            </p>
            {s.progress !== undefined ? (
              <div
                className="h-1.5 w-full overflow-hidden rounded-full bg-muted"
                role="progressbar"
                aria-valuenow={Math.round(s.progress)}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={s.label}
              >
                <div className="h-full rounded-full bg-primary" style={{ width: `${s.progress}%` }} />
              </div>
            ) : (
              <div className="h-1.5" aria-hidden="true" />
            )}
            <p className="text-xs text-muted-foreground">{s.note}</p>
          </article>
        )
      })}
    </section>
  )
}
