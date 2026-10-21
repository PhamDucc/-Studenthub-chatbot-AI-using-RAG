import Link from 'next/link'
import { Clock, MapPin, User } from 'lucide-react'
import { upcomingClasses } from '@/lib/data'
import { Card } from '@/components/portal/page-header'

export function UpcomingClasses() {
  return (
    <Card
      title="Lịch học sắp tới"
      action={
        <Link href="/lich-hoc" className="text-sm font-medium text-primary hover:underline">
          Xem tất cả
        </Link>
      }
    >
      <ul className="divide-y">
        {upcomingClasses.map((c, i) => (
          <li key={c.id} className="flex gap-4 px-5 py-4">
            <div className="flex w-16 shrink-0 flex-col items-center justify-center rounded-lg bg-accent py-2 text-center">
              <span className="text-[11px] font-medium text-muted-foreground">{c.day}</span>
              <span className="text-sm font-bold text-primary">{c.time.split(' – ')[0]}</span>
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-sm font-semibold text-pretty">{c.name}</p>
                {i === 0 && (
                  <span className="rounded-full bg-gold/20 px-2 py-0.5 text-[11px] font-semibold text-gold-foreground">
                    {c.status}
                  </span>
                )}
              </div>
              <p className="mt-0.5 text-xs font-medium text-muted-foreground">{c.code}</p>
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="size-3.5" aria-hidden="true" />
                  {c.time}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="size-3.5" aria-hidden="true" />
                  {c.room}
                </span>
                <span className="flex items-center gap-1">
                  <User className="size-3.5" aria-hidden="true" />
                  {c.lecturer}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  )
}
