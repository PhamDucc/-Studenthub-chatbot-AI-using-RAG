import type { Metadata } from 'next'
import { Mail, Phone } from 'lucide-react'
import { PageHeader, Card } from '@/components/portal/page-header'
import { academicRecords, student } from '@/lib/data'

export const metadata: Metadata = { title: 'Thông tin sinh viên' }

function InfoGrid({ items }: { items: [string, string][] }) {
  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-4 p-5 sm:grid-cols-2">
      {items.map(([k, v]) => (
        <div key={k}>
          <dt className="text-xs font-medium text-muted-foreground">{k}</dt>
          <dd className="mt-0.5 text-sm font-medium">{v}</dd>
        </div>
      ))}
    </dl>
  )
}

export default function StudentInfoPage() {
  const maxGpa = 4

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Thông tin sinh viên" description="Hồ sơ cá nhân và kết quả học tập" />

      <section className="flex flex-col gap-5 rounded-xl border bg-card p-5 shadow-xs sm:flex-row sm:items-center">
        <span className="flex size-20 shrink-0 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground ring-4 ring-gold/40">
          {student.initials}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-xl font-bold">{student.name}</h2>
            <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
              {student.status}
            </span>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            MSV {student.studentId} · {student.major} · {student.faculty}
          </p>
          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <Mail className="size-4" aria-hidden="true" />
              {student.email}
            </span>
            <span className="flex items-center gap-1.5">
              <Phone className="size-4" aria-hidden="true" />
              {student.phone}
            </span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:w-56">
          <div className="rounded-lg bg-accent p-3 text-center">
            <p className="text-xl font-bold text-primary">{student.gpa.toFixed(2)}</p>
            <p className="text-xs text-muted-foreground">GPA</p>
          </div>
          <div className="rounded-lg bg-accent p-3 text-center">
            <p className="text-xl font-bold text-primary">{student.credits}</p>
            <p className="text-xs text-muted-foreground">Tín chỉ</p>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <Card title="Thông tin cá nhân">
          <InfoGrid
            items={[
              ['Họ và tên', student.name],
              ['Ngày sinh', student.dob],
              ['Giới tính', student.gender],
              ['Quê quán', student.hometown],
              ['Email VNU', student.email],
              ['Số điện thoại', student.phone],
            ]}
          />
        </Card>
        <Card title="Thông tin học vụ">
          <InfoGrid
            items={[
              ['Khoa', student.faculty],
              ['Ngành', student.major],
              ['Lớp khóa học', student.className],
              ['Khóa', student.cohort],
              ['Hệ đào tạo', student.program],
              ['Cố vấn học tập', student.advisor],
            ]}
          />
        </Card>
      </div>

      <Card title="Kết quả học tập theo học kỳ">
        <div className="p-5">
          <ul className="flex flex-col gap-4">
            {academicRecords.map((r) => (
              <li key={r.semester} className="grid grid-cols-[7.5rem_1fr_3rem] items-center gap-3 sm:grid-cols-[9rem_1fr_3rem_4rem]">
                <span className="text-sm font-medium">{r.semester}</span>
                <div
                  className="h-2.5 overflow-hidden rounded-full bg-muted"
                  role="progressbar"
                  aria-label={`GPA ${r.semester}`}
                  aria-valuenow={r.gpa}
                  aria-valuemin={0}
                  aria-valuemax={maxGpa}
                >
                  <div className="h-full rounded-full bg-primary" style={{ width: `${(r.gpa / maxGpa) * 100}%` }} />
                </div>
                <span className="text-right text-sm font-semibold text-primary">{r.gpa.toFixed(2)}</span>
                <span className="hidden text-right text-xs text-muted-foreground sm:block">{r.credits} TC</span>
              </li>
            ))}
          </ul>
        </div>
      </Card>
    </div>
  )
}
