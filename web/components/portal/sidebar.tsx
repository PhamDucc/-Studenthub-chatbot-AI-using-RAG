'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LogOut, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { navItems } from './nav-items'
import { Logo } from './logo'
import { student } from '@/lib/data'

type SidebarProps = {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      <div
        className={cn(
          'fixed inset-0 z-40 bg-foreground/40 backdrop-blur-sm transition-opacity lg:hidden',
          open ? 'opacity-100' : 'pointer-events-none opacity-0',
        )}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside
        id="portal-sidebar"
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-sidebar text-sidebar-foreground transition-transform duration-200 lg:sticky lg:top-0 lg:h-screen lg:w-64 lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
        aria-label="Điều hướng chính"
      >
        <div className="flex h-16 items-center justify-between border-b border-sidebar-border px-5">
          <Logo inverted />
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-sidebar-foreground hover:bg-sidebar-accent lg:hidden"
            aria-label="Đóng menu"
          >
            <X className="size-5" />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-5">
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-sidebar-foreground/50">
            Menu
          </p>
          <ul className="flex flex-col gap-1">
            {navItems.map((item) => {
              const active = item.href === '/' ? pathname === '/' : pathname.startsWith(item.href)
              const Icon = item.icon
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={onClose}
                    aria-current={active ? 'page' : undefined}
                    className={cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                      active
                        ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-sm'
                        : 'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                    )}
                  >
                    <Icon className="size-[18px] shrink-0" aria-hidden="true" />
                    <span className="text-pretty">{item.label}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        <div className="border-t border-sidebar-border p-3">
          <div className="mb-2 flex items-center gap-3 rounded-lg bg-sidebar-accent/60 px-3 py-2.5">
            <span className="flex size-9 items-center justify-center rounded-full bg-gold text-sm font-semibold text-gold-foreground">
              {student.initials}
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">{student.name}</p>
              <p className="truncate text-xs text-sidebar-foreground/70">MSV: {student.studentId}</p>
            </div>
          </div>
          <Link
            href="/dang-nhap"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors hover:bg-sidebar-accent hover:text-white"
          >
            <LogOut className="size-[18px]" aria-hidden="true" />
            Đăng xuất
          </Link>
        </div>
      </aside>
    </>
  )
}
