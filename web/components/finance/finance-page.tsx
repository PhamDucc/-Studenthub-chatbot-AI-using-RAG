'use client'

import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, Clock3, Download, Eye, QrCode, WalletCards, X } from 'lucide-react'
import { Card } from '@/components/portal/page-header'
import { cn } from '@/lib/utils'

const initialCharges = [
  { id: 'hp-1', semester: 'Học kỳ I · 2026–2027', name: 'Học phí học kỳ I', amount: 22000000, paid: false },
  { id: 'hp-2', semester: 'Học kỳ I · 2026–2027', name: 'Phí bảo hiểm y tế', amount: 683100, paid: true },
  { id: 'hp-3', semester: 'Học kỳ II · 2025–2026', name: 'Học phí học kỳ II', amount: 22000000, paid: true },
]
const fmt = (n: number) => new Intl.NumberFormat('vi-VN').format(n) + ' đ'

function MockQr() {
  const cells = Array.from({ length: 121 }, (_, i) => i)
  return <div aria-label="Mã QR thanh toán mô phỏng" className="grid size-44 grid-cols-11 gap-0.5 rounded-lg bg-white p-2 shadow-inner ring-1 ring-border">
    {cells.map((i) => <span key={i} className={cn('rounded-[1px]', (i * 17 + i * i) % 7 < 3 ? 'bg-slate-900' : 'bg-white')} />)}
  </div>
}

export function FinancePage() {
  const [charges, setCharges] = useState(initialCharges)
  const [paymentOpen, setPaymentOpen] = useState(false)
  const [seconds, setSeconds] = useState(300)
  const [tab, setTab] = useState<'fees' | 'history'>('fees')
  const [receipt, setReceipt] = useState(false)
  const total = charges.reduce((s, c) => s + c.amount, 0)
  const paid = charges.filter((c) => c.paid).reduce((s, c) => s + c.amount, 0)
  const debt = total - paid
  const unpaid = charges.find((c) => !c.paid)
  useEffect(() => { if (!paymentOpen) return; const timer = window.setInterval(() => setSeconds((s) => s > 0 ? s - 1 : 0), 1000); return () => window.clearInterval(timer) }, [paymentOpen])
  const grouped = useMemo(() => charges.reduce<Record<string, typeof charges>>((acc, item) => { (acc[item.semester] ??= []).push(item); return acc }, {}), [charges])
  return <div className="flex flex-col gap-6">
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {[["Tổng học phí", total, WalletCards], ["Đã thanh toán", paid, CheckCircle2], ["Còn nợ kỳ này", debt, Clock3]].map(([label, value, Icon], i) => { const C = Icon as typeof WalletCards; return <Card key={String(label)}><div className="flex items-start justify-between p-5"><div><p className="text-sm text-muted-foreground">{String(label)}</p><p className="mt-2 text-2xl font-bold tracking-tight">{fmt(Number(value))}</p></div><span className={cn('flex size-10 items-center justify-center rounded-xl', i === 2 ? 'bg-amber-50 text-amber-600' : 'bg-primary/10 text-primary')}><C className="size-5" /></span></div></Card> })}
    </div>
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4"><div><h2 className="font-semibold">Tài chính sinh viên</h2><p className="mt-1 text-xs text-muted-foreground">Theo dõi học phí và lịch sử thanh toán</p></div><div className="flex rounded-lg bg-muted p-1"><button onClick={() => setTab('fees')} className={cn('rounded-md px-3 py-1.5 text-sm font-medium', tab === 'fees' && 'bg-background shadow-sm')}>Các khoản phí</button><button onClick={() => setTab('history')} className={cn('rounded-md px-3 py-1.5 text-sm font-medium', tab === 'history' && 'bg-background shadow-sm')}>Lịch sử giao dịch</button></div></div>
      {tab === 'fees' ? <div className="flex flex-col gap-6 p-5">{Object.entries(grouped).map(([semester, items]) => <div key={semester}><h3 className="mb-3 text-sm font-semibold text-muted-foreground">{semester}</h3><div className="overflow-hidden rounded-lg border">{items.map((item) => <div key={item.id} className="flex flex-col gap-3 border-b p-4 last:border-0 sm:flex-row sm:items-center sm:justify-between"><div><p className="font-medium">{item.name}</p><p className="mt-1 text-sm text-muted-foreground">Hạn thanh toán: 30/11/2026</p></div><div className="flex items-center justify-between gap-4 sm:justify-end"><span className={cn('rounded-full px-2.5 py-1 text-xs font-semibold', item.paid ? 'bg-emerald-50 text-emerald-700' : 'bg-orange-50 text-orange-700')}>{item.paid ? 'Đã thanh toán' : 'Chưa thanh toán'}</span><strong className="text-sm">{fmt(item.amount)}</strong>{!item.paid && <button onClick={() => { setSeconds(300); setPaymentOpen(true) }} className="rounded-lg bg-primary px-3 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/90">Nộp học phí</button>}</div></div>)}</div></div>)}</div> : <div className="overflow-x-auto"><table className="w-full min-w-[640px] text-left text-sm"><thead className="bg-muted/60 text-xs uppercase text-muted-foreground"><tr><th className="px-5 py-3">Mã giao dịch</th><th className="px-5 py-3">Nội dung</th><th className="px-5 py-3">Thời gian</th><th className="px-5 py-3">Số tiền</th><th className="px-5 py-3">Biên lai</th></tr></thead><tbody className="divide-y">{[['GD20261001','Học phí học kỳ II','18/05/2026',11800000],['GD20260912','Phí bảo hiểm y tế','04/09/2026',1050000]].map((r) => <tr key={r[0]}><td className="px-5 py-4 font-medium">{r[0]}</td><td className="px-5 py-4">{r[1]}</td><td className="px-5 py-4 text-muted-foreground">{r[2]}</td><td className="px-5 py-4 font-medium">{fmt(Number(r[3]))}</td><td className="px-5 py-4"><button onClick={() => setReceipt(true)} className="inline-flex items-center gap-1.5 text-primary hover:underline"><Eye className="size-4" /> Xem</button><button className="ml-3 inline-flex items-center gap-1.5 text-muted-foreground hover:text-foreground"><Download className="size-4" /> Tải</button></td></tr>)}</tbody></table></div>}
    </Card>
    {paymentOpen && <div className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/40 p-4"><div role="dialog" aria-modal="true" className="w-full max-w-md rounded-2xl bg-background shadow-xl"><div className="flex items-center justify-between border-b p-5"><div><h2 className="font-semibold">Thanh toán học phí</h2><p className="text-xs text-muted-foreground">Quét mã bằng ứng dụng ngân hàng</p></div><button onClick={() => setPaymentOpen(false)} aria-label="Đóng"><X className="size-5" /></button></div><div className="flex flex-col items-center gap-4 p-6"><MockQr /><div className="w-full rounded-lg bg-muted/60 p-4 text-sm"><div className="flex justify-between gap-4"><span className="text-muted-foreground">Ngân hàng</span><b>Vietcombank</b></div><div className="mt-2 flex justify-between gap-4"><span className="text-muted-foreground">Số tài khoản</span><b>1029384756</b></div><div className="mt-2 flex justify-between gap-4"><span className="text-muted-foreground">Số tiền</span><b>{fmt(unpaid?.amount ?? 0)}</b></div><div className="mt-2 flex justify-between gap-4"><span className="text-muted-foreground">Nội dung</span><b>UET {unpaid?.id.toUpperCase()}</b></div></div><p className="flex items-center gap-2 text-sm text-amber-700"><Clock3 className="size-4" /> Mã hết hạn sau {String(Math.floor(seconds / 60)).padStart(2, '0')}:{String(seconds % 60).padStart(2, '0')}</p><button onClick={() => { if (unpaid) setCharges((cs) => cs.map((c) => c.id === unpaid.id ? { ...c, paid: true } : c)); setPaymentOpen(false) }} className="h-11 w-full rounded-lg bg-primary font-semibold text-primary-foreground">Xác nhận đã chuyển khoản</button></div></div></div>}
    {receipt && <div className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/40 p-4"><div className="w-full max-w-md rounded-2xl bg-background p-6 shadow-xl"><div className="flex items-center justify-between"><h2 className="font-semibold">Biên lai thanh toán</h2><button onClick={() => setReceipt(false)} aria-label="Đóng"><X className="size-5" /></button></div><div className="mt-5 rounded-xl border border-dashed p-6 text-center"><CheckCircle2 className="mx-auto size-10 text-emerald-600" /><p className="mt-3 font-semibold">Thanh toán thành công</p><p className="mt-1 text-sm text-muted-foreground">GD20261001 · 18/05/2026</p><p className="mt-4 text-2xl font-bold">11.800.000 đ</p></div></div></div>}
  </div>
}
