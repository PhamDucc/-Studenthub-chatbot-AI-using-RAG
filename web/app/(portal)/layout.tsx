import { AppShell } from '@/components/portal/app-shell'
import { ChatWidget } from '@/components/chat/chat-widget'

export default function PortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <AppShell>{children}</AppShell>
      <ChatWidget />
    </>
  )
}