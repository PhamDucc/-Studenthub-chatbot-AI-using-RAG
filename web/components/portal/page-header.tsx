export function PageHeader({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: React.ReactNode
}) {
  return (
    <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-balance text-foreground">{title}</h1>
        {description && <p className="mt-1 text-sm text-muted-foreground text-pretty">{description}</p>}
      </div>
      {action}
    </div>
  )
}

export function Card({
  title,
  action,
  children,
  className = '',
}: {
  title?: string
  action?: React.ReactNode
  children: React.ReactNode
  className?: string
}) {
  return (
    <section className={`rounded-xl border bg-card shadow-xs ${className}`}>
      {title && (
        <div className="flex items-center justify-between gap-3 border-b px-5 py-4">
          <h2 className="text-base font-semibold">{title}</h2>
          {action}
        </div>
      )}
      {children}
    </section>
  )
}
