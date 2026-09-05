export function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="space-y-3">
        <div className="h-4 w-1/3 animate-pulse rounded bg-slate-200" />
        <div className="h-8 w-1/2 animate-pulse rounded bg-slate-300" />
        <div className="h-3 w-1/4 animate-pulse rounded bg-slate-200" />
      </div>
    </div>
  )
}

export function SkeletonProductCard() {
  return (
    <div className="flex flex-col p-5 rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="h-5 w-32 animate-pulse rounded bg-slate-200" />
          <div className="h-3 w-24 animate-pulse rounded bg-slate-200" />
        </div>
        <div className="h-6 w-16 animate-pulse rounded bg-slate-200" />
      </div>
      <div className="mt-3 space-y-2">
        <div className="h-4 w-full animate-pulse rounded bg-slate-200" />
        <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200" />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <div className="rounded-lg bg-slate-50 p-2.5 space-y-2">
          <div className="h-3 w-16 animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-20 animate-pulse rounded bg-slate-300" />
        </div>
        <div className="rounded-lg bg-slate-50 p-2.5 space-y-2">
          <div className="h-3 w-16 animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-20 animate-pulse rounded bg-slate-300" />
        </div>
        <div className="rounded-lg bg-slate-50 p-2.5 space-y-2">
          <div className="h-3 w-16 animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-20 animate-pulse rounded bg-slate-300" />
        </div>
        <div className="rounded-lg bg-slate-50 p-2.5 space-y-2">
          <div className="h-3 w-16 animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-20 animate-pulse rounded bg-slate-300" />
        </div>
      </div>
      <div className="mt-4 h-10 w-full animate-pulse rounded bg-slate-200" />
    </div>
  )
}

export function SkeletonTable({ rows = 5, columns = 6 }: { rows?: number; columns?: number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-6 py-5">
        <div className="h-6 w-1/3 animate-pulse rounded bg-slate-200" />
        <div className="mt-2 h-4 w-1/2 animate-pulse rounded bg-slate-200" />
      </div>
      <div className="p-6">
        <div className="space-y-3">
          {Array.from({ length: rows }).map((_, i) => (
            <div key={i} className="flex items-center gap-4">
              {Array.from({ length: columns }).map((_, j) => (
                <div key={j} className="h-10 flex-1 animate-pulse rounded bg-slate-200" />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export function SkeletonGrid({ cards = 3, variant = 'card' }: { cards?: number; variant?: 'card' | 'product' }) {
  const SkeletonComponent = variant === 'product' ? SkeletonProductCard : SkeletonCard
  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: cards }).map((_, i) => (
        <SkeletonComponent key={i} />
      ))}
    </div>
  )
}

export function SkeletonPolicy() {
  return (
    <div className="max-w-2xl space-y-4">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="space-y-2">
            <div className="h-6 w-32 animate-pulse rounded bg-slate-200" />
            <div className="h-4 w-48 animate-pulse rounded bg-slate-200" />
          </div>
          <div className="h-6 w-24 animate-pulse rounded bg-slate-200" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-slate-100 bg-slate-50 p-4 space-y-2">
              <div className="h-3 w-20 animate-pulse rounded bg-slate-200" />
              <div className="h-8 w-24 animate-pulse rounded bg-slate-300" />
              <div className="h-3 w-28 animate-pulse rounded bg-slate-200" />
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="h-5 w-32 animate-pulse rounded bg-slate-200 mb-3" />
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 rounded-lg bg-slate-50 px-4 py-2.5">
              <div className="h-2.5 w-2.5 rounded-full animate-pulse bg-slate-300" />
              <div className="h-4 w-28 animate-pulse rounded bg-slate-200" />
              <div className="h-4 w-32 animate-pulse rounded bg-slate-200" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}