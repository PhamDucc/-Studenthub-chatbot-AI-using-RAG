import Link from 'next/link'
import { GraduationCap } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Logo({ inverted = false }: { inverted?: boolean }) {
  return (
    <Link href="/" className="flex items-center gap-2.5" aria-label="Student Hub UET – Trang chủ">
      <span
        className={cn(
          'flex size-9 shrink-0 items-center justify-center rounded-lg',
          inverted ? 'bg-white text-primary' : 'bg-primary text-primary-foreground',
        )}
      >
        <GraduationCap className="size-5" aria-hidden="true" />
      </span>
      <span className="flex flex-col leading-tight">
        <span className={cn('text-sm font-bold', inverted ? 'text-white' : 'text-primary')}>
          Student Hub UET
        </span>
        <span
          className={cn(
            'text-[11px] font-medium',
            inverted ? 'text-sidebar-foreground/70' : 'text-muted-foreground',
          )}
        >
          UET – VNU
        </span>
      </span>
    </Link>
  )
}
