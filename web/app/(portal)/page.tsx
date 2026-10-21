import { GreetingBanner } from '@/components/dashboard/greeting-banner'
import { StatCards } from '@/components/dashboard/stat-cards'
import { QuickActions } from '@/components/dashboard/quick-actions'
import { UpcomingClasses } from '@/components/dashboard/upcoming-classes'
import { Announcements } from '@/components/dashboard/announcements'

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <GreetingBanner />
      <StatCards />
      <QuickActions />
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
        <div className="xl:col-span-3">
          <UpcomingClasses />
        </div>
        <div className="xl:col-span-2">
          <Announcements />
        </div>
      </div>
    </div>
  )
}
