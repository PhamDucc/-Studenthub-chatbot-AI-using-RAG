import type { Metadata } from 'next'
import { Download } from 'lucide-react'
import { PageHeader, Card } from '@/components/portal/page-header'
import { WeeklyTimetable } from '@/components/timetable/weekly-timetable'
import { currentCourses } from '@/lib/data'

export const metadata: Metadata = { title: 'Lịch học & Thời khóa biểu' }

const exams = [
  { code: 'INT3401', name: 'Trí tuệ nhân tạo', date: '02/11/2026', time: '08:00', room: '301-G2', form: 'Viết' },
  { code: 'INT3306', name: 'Phát triển ứng dụng Web', date: '04/11/2026', time: '13:30', room: 'PM 207-G2', form: 'Thực hành' },
  { code: 'INT3209', name: 'Khai phá dữ liệu', date: '06/11/2026', time: '08:00', room: '309-GĐ3', form: 'Trắc nghiệm' },
]

export default function TimetablePage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Lịch học & Thời khóa biểu"
        description="Học kỳ I, năm học 2026–2027 · 6 học phần · 17 tín chỉ"
        action={
          <button
            type="button"
            className="inline-flex h-10 items-center gap-2 self-start rounded-lg border bg-card px-4 text-sm font-medium shadow-xs hover:bg-muted"
          >
            <Download className="size-4" aria-hidden="true" />
            Xuất lịch (.ics)
          </button>
        }
      />

      <WeeklyTimetable />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <Card title="Lịch thi giữa kỳ">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead className="bg-muted/60 text-xs text-muted-foreground">
                <tr>
                  <th className="px-5 py-3 font-medium">Học phần</th>
                  <th className="px-3 py-3 font-medium">Ngày thi</th>
                  <th className="px-3 py-3 font-medium">Phòng</th>
                  <th className="px-5 py-3 font-medium">Hình thức</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {exams.map((e) => (
                  <tr key={e.code}>
                    <td className="px-5 py-3">
                      <p className="font-medium">{e.name}</p>
                      <p className="text-xs text-muted-foreground">{e.code}</p>
                    </td>
                    <td className="px-3 py-3">
                      {e.date}
                      <span className="block text-xs text-muted-foreground">{e.time}</span>
                    </td>
                    <td className="px-3 py-3">{e.room}</td>
                    <td className="px-5 py-3">
                      <span className="rounded-md bg-accent px-2 py-0.5 text-xs font-medium text-primary">{e.form}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="Học phần đã đăng ký">
          <ul className="divide-y">
            {currentCourses.map((c) => (
              <li key={c.code} className="flex items-center justify-between gap-4 px-5 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{c.name}</p>
                  <p className="text-xs text-muted-foreground">Lớp {c.group}</p>
                </div>
                <span className="shrink-0 text-sm font-semibold text-primary">{c.credits} TC</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  )
}
