import type { Metadata } from 'next'
import { PageHeader } from '@/components/portal/page-header'
import { FinancePage } from '@/components/finance/finance-page'

export const metadata: Metadata = { title: 'Tài chính sinh viên' }

export default function FinanceRoute() {
  return <div><PageHeader title="Tài chính sinh viên" description="Theo dõi học phí, các khoản phải nộp và lịch sử giao dịch của bạn." /><FinancePage /></div>
}
