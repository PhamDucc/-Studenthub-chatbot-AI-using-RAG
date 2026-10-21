import { Megaphone } from 'lucide-react'
import { announcements } from '@/lib/data'
import { Card } from '@/components/portal/page-header'

export function Announcements() {
  return (
    <Card
      title="Thông báo mới nhất"
      action={<Megaphone className="size-4 text-muted-foreground" aria-hidden="true" />}
    >
      <ul className="divide-y">
        {announcements.map((a) => (
          <li key={a.id}>
            <a href="#" className="block px-5 py-4 transition hover:bg-muted/60">
              <div className="flex items-center gap-2">
                <span className="rounded-md bg-accent px-2 py-0.5 text-[11px] font-semibold text-primary">
                  {a.category}
                </span>
                {a.important && (
                  <span className="rounded-md bg-destructive/10 px-2 py-0.5 text-[11px] font-semibold text-destructive">
                    Quan trọng
                  </span>
                )}
                <time className="ml-auto text-xs text-muted-foreground">{a.date}</time>
              </div>
              <p className="mt-2 text-sm leading-snug font-medium text-pretty">{a.title}</p>
            </a>
          </li>
        ))}
      </ul>
    </Card>
  )
}
