import { AppShell } from '@/components/portal/app-shell'

export default function PortalLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>
}
