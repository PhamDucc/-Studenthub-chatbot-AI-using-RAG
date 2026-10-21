import type { Metadata } from 'next'
import Link from 'next/link'
import { GraduationCap } from 'lucide-react'

export const metadata: Metadata = { title: 'Đăng nhập' }

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-primary px-4 py-10">
      <div className="w-full max-w-sm rounded-2xl bg-card p-7 shadow-xl">
        <div className="mb-6 flex flex-col items-center text-center">
          <span className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <GraduationCap className="size-6" aria-hidden="true" />
          </span>
          <h1 className="mt-3 text-xl font-bold text-primary">Student Hub UET</h1>
          <p className="text-sm text-muted-foreground">Bạn đã đăng xuất. Đăng nhập lại để tiếp tục.</p>
        </div>
        <form action="/" className="flex flex-col gap-4">
          <div>
            <label htmlFor="username" className="mb-1.5 block text-sm font-medium">
              Mã sinh viên
            </label>
            <input
              id="username"
              name="username"
              autoComplete="username"
              placeholder="22021234"
              className="h-10 w-full rounded-lg border px-3 text-sm outline-none focus:border-ring focus:ring-3 focus:ring-ring/20"
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1.5 block text-sm font-medium">
              Mật khẩu
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              className="h-10 w-full rounded-lg border px-3 text-sm outline-none focus:border-ring focus:ring-3 focus:ring-ring/20"
            />
          </div>
          <button
            type="submit"
            className="h-10 rounded-lg bg-primary text-sm font-semibold text-primary-foreground hover:bg-primary/90"
          >
            Đăng nhập
          </button>
          <Link href="/faq" className="text-center text-xs font-medium text-primary hover:underline">
            Quên mật khẩu?
          </Link>
        </form>
      </div>
    </main>
  )
}
