'use client'

import { useState } from 'react'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Header } from './header'
import { Sidebar } from './sidebar'

export function AppShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()
  const isChatPage = pathname === '/tro-ly-ai'

  return (
    <div className="flex min-h-screen">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onMenuClick={() => setOpen(true)} menuOpen={open} />
        <main className={cn('flex-1', isChatPage ? 'min-h-0 overflow-hidden' : 'px-4 py-6 md:px-6 lg:px-8')}>
          <div className={cn(isChatPage ? 'h-[calc(100dvh-4rem)]' : 'mx-auto w-full max-w-7xl')}>{children}</div>
        </main>
      </div>
    </div>
  )
}
