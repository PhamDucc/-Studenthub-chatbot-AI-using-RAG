'use client'

import { useState } from 'react'
import { ChevronDown, Search } from 'lucide-react'
import { faqs } from '@/lib/data'
import { cn } from '@/lib/utils'

const categories = ['Tất cả', ...Array.from(new Set(faqs.map((f) => f.category)))]

export function FaqList() {
  const [category, setCategory] = useState('Tất cả')
  const [query, setQuery] = useState('')

  const q = query.trim().toLowerCase()
  const filtered = faqs.filter(
    (f) =>
      (category === 'Tất cả' || f.category === category) &&
      (!q || f.q.toLowerCase().includes(q) || f.a.toLowerCase().includes(q)),
  )

  return (
    <div className="flex flex-col gap-5">
      <div className="relative">
        <label htmlFor="faq-search" className="sr-only">
          Tìm câu hỏi
        </label>
        <Search className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
        <input
          id="faq-search"
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Nhập từ khóa, ví dụ: học phí, phúc khảo..."
          className="h-11 w-full rounded-xl border bg-card pr-3 pl-10 text-sm shadow-xs outline-none focus:border-ring focus:ring-3 focus:ring-ring/20"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {categories.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setCategory(c)}
            aria-pressed={category === c}
            className={cn(
              'rounded-full border px-3.5 py-1.5 text-sm font-medium transition',
              category === c ? 'border-primary bg-primary text-primary-foreground' : 'bg-card hover:bg-muted',
            )}
          >
            {c}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-3">
        {filtered.map((f) => (
          <details key={f.q} className="group rounded-xl border bg-card shadow-xs open:ring-1 open:ring-primary/30">
            <summary className="flex cursor-pointer list-none items-center gap-3 px-5 py-4 [&::-webkit-details-marker]:hidden">
              <span className="rounded-md bg-accent px-2 py-0.5 text-[11px] font-semibold text-primary">{f.category}</span>
              <span className="flex-1 text-sm font-semibold text-pretty">{f.q}</span>
              <ChevronDown className="size-4 shrink-0 text-muted-foreground transition group-open:rotate-180" aria-hidden="true" />
            </summary>
            <p className="px-5 pb-5 text-sm leading-relaxed text-muted-foreground">{f.a}</p>
          </details>
        ))}
        {filtered.length === 0 && (
          <p className="rounded-xl border bg-card py-10 text-center text-sm text-muted-foreground">
            Không tìm thấy câu hỏi phù hợp.
          </p>
        )}
      </div>
    </div>
  )
}
