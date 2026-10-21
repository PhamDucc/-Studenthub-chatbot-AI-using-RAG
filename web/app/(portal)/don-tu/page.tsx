import type { Metadata } from 'next'
import { PageHeader } from '@/components/portal/page-header'
import { ServiceRequests } from '@/components/services/service-requests'

export const metadata: Metadata = { title: 'Đơn từ & Dịch vụ công' }

export default function ServicesPage() {
  return (
    <div>
      <PageHeader
        title="Đơn từ & Dịch vụ công"
        description="Nộp đơn và yêu cầu giấy tờ hành chính trực tuyến, theo dõi trạng thái xử lý."
      />
      <ServiceRequests />
    </div>
  )
}
