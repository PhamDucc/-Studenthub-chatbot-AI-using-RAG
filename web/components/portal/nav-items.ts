import {
  CalendarDays,
  FileText,
  HelpCircle,
  WalletCards,
  ClipboardCheck,
  LayoutDashboard,
  UserRound,
  type LucideIcon,
} from 'lucide-react'

export type NavItem = {
  href: string
  label: string
  icon: LucideIcon
}

export const navItems: NavItem[] = [
  { href: '/', label: 'Trang chủ', icon: LayoutDashboard },
  { href: '/lich-hoc', label: 'Lịch học & Thời khóa biểu', icon: CalendarDays },
  { href: '/thong-tin', label: 'Thông tin sinh viên', icon: UserRound },
  { href: '/don-tu', label: 'Đơn từ & Dịch vụ công', icon: FileText },
  { href: '/tai-chinh', label: 'Tài chính sinh viên', icon: WalletCards },
  { href: '/ren-luyen', label: 'Đánh giá rèn luyện', icon: ClipboardCheck },
  { href: '/faq', label: 'Câu hỏi thường gặp', icon: HelpCircle },
]
