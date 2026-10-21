import type { Metadata } from 'next'
import { Mail, MapPin, Phone } from 'lucide-react'
import { PageHeader, Card } from '@/components/portal/page-header'
import { FaqList } from '@/components/faq/faq-list'

export const metadata: Metadata = { title: 'Câu hỏi thường gặp' }

export default function FaqPage() {
  return (
    <div>
      <PageHeader title="Câu hỏi thường gặp" description="Giải đáp nhanh các thắc mắc về đào tạo, học phí và thủ tục hành chính." />
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <FaqList />
        </div>
        <Card title="Cần hỗ trợ thêm?" className="h-fit">
          <div className="flex flex-col gap-4 p-5 text-sm">
            <p className="text-muted-foreground">Liên hệ Phòng Công tác Sinh viên trong giờ hành chính (Thứ 2 – Thứ 6).</p>
            <p className="flex items-center gap-2">
              <MapPin className="size-4 text-primary" aria-hidden="true" />
              Phòng 105, Nhà E3, 144 Xuân Thủy, Cầu Giấy
            </p>
            <p className="flex items-center gap-2">
              <Phone className="size-4 text-primary" aria-hidden="true" />
              024 3754 7865
            </p>
            <p className="flex items-center gap-2">
              <Mail className="size-4 text-primary" aria-hidden="true" />
              ctsv.uet@vnu.edu.vn
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
