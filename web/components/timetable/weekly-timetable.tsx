'use client'

import { useState } from 'react'
import { ChevronLeft, ChevronRight, Clock, MapPin, User } from 'lucide-react'
import { periods, timetable, weekDays, type ClassSession } from '@/lib/data'
import { cn } from '@/lib/utils'

const colorMap: Record<ClassSession['color'], string> = {
  navy: 'bg-primary/10 border-primary text-primary',
  sky: 'bg-sky-50 border-sky-500 text-sky-900',
  amber: 'bg-amber-50 border-amber-500 text-amber-900',
  emerald: 'bg-emerald-50 border-emerald-500 text-emerald-900',
  rose: 'bg-rose-50 border-rose-500 text-rose-900',
  violet: 'bg-violet-50 border-violet-500 text-violet-900',
}

const BASE_MONDAY = new Date(2026, 9, 19)
const TODAY_INDEX = 2

function addDays(d: Date, n: number) {
  const r = new Date(d)
  r.setDate(r.getDate() + n)
  return r
}

function fmt(d: Date) {
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}`
}

function timeRange(s: ClassSession) {
  const start = periods[s.startPeriod - 1].time
  const endHour = 7 + s.startPeriod - 1 + s.periods - 1
  return `${start} – ${String(endHour).padStart(2, '0')}:50`
}

export function WeeklyTimetable() {
  const [week, setWeek] = useState(0)
  const [mobileDay, setMobileDay] = useState(TODAY_INDEX)
  const monday = addDays(BASE_MONDAY, week * 7)
  const dates = weekDays.map((_, i) => addDays(monday, i))
  const isCurrentWeek = week === 0
  const examWeek = week >= 2

  return (
    <div className="rounded-xl border bg-card shadow-xs">
      <div className="flex flex-col gap-3 border-b px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">Tuần {8 + week}</h2>
          <p className="text-sm text-muted-foreground">
            {fmt(dates[0])} – {fmt(dates[5])}/{monday.getFullYear()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setWeek((w) => w - 1)}
            className="flex size-9 items-center justify-center rounded-lg border hover:bg-muted"
            aria-label="Tuần trước"
          >
            <ChevronLeft className="size-4" />
          </button>
          <button
            type="button"
            onClick={() => setWeek(0)}
            disabled={isCurrentWeek}
            className="h-9 rounded-lg border px-3 text-sm font-medium hover:bg-muted disabled:bg-primary disabled:text-primary-foreground"
          >
            Tuần này
          </button>
          <button
            type="button"
            onClick={() => setWeek((w) => w + 1)}
            className="flex size-9 items-center justify-center rounded-lg border hover:bg-muted"
            aria-label="Tuần sau"
          >
            <ChevronRight className="size-4" />
          </button>
        </div>
      </div>

      {examWeek ? (
        <div className="px-5 py-16 text-center">
          <p className="text-sm font-semibold">Tuần thi giữa kỳ</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Lịch học tạm ngừng. Vui lòng xem lịch thi ở bảng bên dưới.
          </p>
        </div>
      ) : (
        <>
          {/* Desktop grid */}
          <div className="hidden overflow-x-auto md:block">
            <div
              className="grid min-w-[760px]"
              style={{
                gridTemplateColumns: '72px repeat(6, minmax(0, 1fr))',
                gridTemplateRows: `48px repeat(${periods.length}, 56px)`,
              }}
            >
              <div className="border-r border-b bg-muted/50" />
              {weekDays.map((d, i) => {
                const today = isCurrentWeek && i === TODAY_INDEX
                return (
                  <div
                    key={d}
                    className={cn(
                      'flex flex-col items-center justify-center border-b text-center',
                      i < 5 && 'border-r',
                      today ? 'bg-primary text-primary-foreground' : 'bg-muted/50',
                    )}
                    style={{ gridColumn: i + 2, gridRow: 1 }}
                  >
                    <span className="text-xs font-semibold">{d}</span>
                    <span className={cn('text-[11px]', today ? 'text-primary-foreground/80' : 'text-muted-foreground')}>
                      {fmt(dates[i])}
                    </span>
                  </div>
                )
              })}

              {periods.map((p, r) => (
                <div
                  key={p.period}
                  className="flex flex-col items-center justify-start border-r border-b pt-1.5 text-center"
                  style={{ gridColumn: 1, gridRow: r + 2 }}
                >
                  <span className="text-[11px] font-semibold text-foreground">Tiết {p.period}</span>
                  <span className="text-[10px] text-muted-foreground">{p.time}</span>
                </div>
              ))}

              {periods.map((p, r) =>
                weekDays.map((d, c) => (
                  <div
                    key={`${p.period}-${d}`}
                    className={cn(
                      'border-b',
                      c < 5 && 'border-r',
                      isCurrentWeek && c === TODAY_INDEX && 'bg-accent/40',
                      r === 5 && 'bg-muted/40',
                    )}
                    style={{ gridColumn: c + 2, gridRow: r + 2 }}
                    aria-hidden="true"
                  />
                )),
              )}

              {timetable.map((s) => (
                <article
                  key={s.id}
                  className={cn(
                    'z-10 m-1 flex flex-col overflow-hidden rounded-lg border-l-4 px-2.5 py-2',
                    colorMap[s.color],
                  )}
                  style={{
                    gridColumn: s.day + 2,
                    gridRow: `${s.startPeriod + 1} / span ${s.periods}`,
                  }}
                >
                  <p className="text-[11px] font-semibold opacity-80">
                    {s.code} · {s.type}
                  </p>
                  <h3 className="mt-0.5 line-clamp-2 text-xs leading-snug font-semibold">{s.name}</h3>
                  <p className="mt-auto flex items-center gap-1 pt-1 text-[11px] opacity-80">
                    <MapPin className="size-3" aria-hidden="true" />
                    {s.room}
                  </p>
                </article>
              ))}
            </div>
          </div>

          {/* Mobile day list */}
          <div className="md:hidden">
            <div className="flex gap-1.5 overflow-x-auto border-b px-4 py-3" role="tablist" aria-label="Chọn ngày">
              {weekDays.map((d, i) => (
                <button
                  key={d}
                  type="button"
                  role="tab"
                  aria-selected={mobileDay === i}
                  onClick={() => setMobileDay(i)}
                  className={cn(
                    'flex min-w-14 flex-col items-center rounded-lg px-2 py-2 text-xs font-medium transition',
                    mobileDay === i ? 'bg-primary text-primary-foreground' : 'bg-muted text-foreground',
                  )}
                >
                  <span>{d}</span>
                  <span className="text-[11px] opacity-75">{fmt(dates[i])}</span>
                </button>
              ))}
            </div>
            <ul className="flex flex-col gap-3 p-4" role="tabpanel">
              {timetable
                .filter((s) => s.day === mobileDay)
                .sort((a, b) => a.startPeriod - b.startPeriod)
                .map((s) => (
                  <li key={s.id} className={cn('rounded-lg border-l-4 p-3', colorMap[s.color])}>
                    <p className="text-[11px] font-semibold opacity-80">
                      {s.code} · {s.type} · Tiết {s.startPeriod}–{s.startPeriod + s.periods - 1}
                    </p>
                    <h3 className="mt-0.5 text-sm font-semibold">{s.name}</h3>
                    <div className="mt-2 flex flex-col gap-1 text-xs opacity-80">
                      <span className="flex items-center gap-1.5">
                        <Clock className="size-3.5" aria-hidden="true" />
                        {timeRange(s)}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <MapPin className="size-3.5" aria-hidden="true" />
                        {s.room}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <User className="size-3.5" aria-hidden="true" />
                        {s.lecturer}
                      </span>
                    </div>
                  </li>
                ))}
              {timetable.filter((s) => s.day === mobileDay).length === 0 && (
                <li className="py-10 text-center text-sm text-muted-foreground">Không có lịch học trong ngày này.</li>
              )}
            </ul>
          </div>
        </>
      )}
    </div>
  )
}
