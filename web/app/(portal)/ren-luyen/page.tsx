import type { Metadata } from 'next'
import { PageHeader } from '@/components/portal/page-header'
import { TrainingPage } from '@/components/training/training-page'

export const metadata: Metadata = { title: 'Đánh giá rèn luyện' }

export default function TrainingRoute() {
  return <div><PageHeader title="Đánh giá rèn luyện" description="Tự đánh giá kết quả rèn luyện học kỳ I năm học 2026–2027." /><TrainingPage /></div>
}
