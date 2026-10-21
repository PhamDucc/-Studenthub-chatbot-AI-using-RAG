'use client'

import { useState } from 'react'
import { Header } from './header'
import { Sidebar } from './sidebar'

export function AppShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="flex min-h-screen">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onMenuClick={() => setOpen(true)} menuOpen={open} />
        <main className="flex-1 px-4 py-6 md:px-6 lg:px-8">
          <div className="mx-auto w-full max-w-7xl">{children}</div>
        </main>
      </div>
    </div>
  )
}
