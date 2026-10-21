'use client'

import { useState } from 'react'
import { Bell, Menu, Search } from 'lucide-react'
import { announcements, student } from '@/lib/data'
import { cn } from '@/lib/utils'

type HeaderProps = {
  onMenuClick: () => void
  menuOpen: boolean
}

export function Header({ onMenuClick, menuOpen }: HeaderProps) {
  const [notifOpen, setNotifOpen] = useState(false)
  const [read, setRead] = useState(false)
  const unread = read ? 0 : 3

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b bg-background/95 px-4 backdrop-blur md:px-6">
      <button
        type="button"
        onClick={onMenuClick}
        className="rounded-md p-2 text-foreground hover:bg-muted lg:hidden"
        aria-label="Mở menu"
        aria-expanded={menuOpen}
        aria-controls="portal-sidebar"
      >
        <Menu className="size-5" />
      </button>

      <form role="search" className="relative max-w-md flex-1" onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="global-search" className="sr-only">
          Tìm kiếm
        </label>
        <Search
          className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden="true"
        />
        <input
          id="global-search"
          type="search"
          placeholder="Tìm môn học, thông báo, biểu mẫu..."
          className="h-10 w-full rounded-lg border bg-muted/60 pr-3 pl-9 text-sm outline-none transition placeholder:text-muted-foreground focus:border-ring focus:bg-background focus:ring-3 focus:ring-ring/20"
        />
      </form>

      <div className="ml-auto flex items-center gap-2 md:gap-3">
        <div className="relative">
          <button
            type="button"
            onClick={() => setNotifOpen((v) => !v)}
            className="relative rounded-full p-2.5 text-foreground hover:bg-muted"
            aria-label={`Thông báo${unread ? `, ${unread} chưa đọc` : ''}`}
            aria-expanded={notifOpen}
          >
            <Bell className="size-5" />
            {unread > 0 && (
              <span className="absolute top-1.5 right-1.5 flex size-4 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white">
                {unread}
              </span>
            )}
          </button>
          {notifOpen && (
            <div
              className="absolute right-0 mt-2 w-[min(20rem,calc(100vw-2rem))] overflow-hidden rounded-xl border bg-popover shadow-lg"
              onKeyDown={(e) => e.key === 'Escape' && setNotifOpen(false)}
            >
              <div className="flex items-center justify-between border-b px-4 py-3">
                <p className="text-sm font-semibold">Thông báo</p>
                <button
                  type="button"
                  className="text-xs font-medium text-primary hover:underline"
                  onClick={() => setRead(true)}
                >
                  Đánh dấu đã đọc
                </button>
              </div>
              <ul className="max-h-80 divide-y overflow-y-auto">
                {announcements.slice(0, 4).map((a, i) => (
                  <li key={a.id} className={cn('px-4 py-3', !read && i < 3 && 'bg-accent/50')}>
                    <p className="text-xs font-medium text-primary">{a.category}</p>
                    <p className="mt-0.5 text-sm leading-snug text-pretty">{a.title}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{a.date}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 border-l pl-3">
          <span
            className="flex size-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground ring-2 ring-gold/70 ring-offset-2"
            aria-hidden="true"
          >
            {student.initials}
          </span>
          <div className="hidden leading-tight md:block">
            <p className="text-sm font-semibold">{student.name}</p>
            <p className="text-xs text-muted-foreground">{student.className}</p>
          </div>
        </div>
      </div>
    </header>
  )
}
