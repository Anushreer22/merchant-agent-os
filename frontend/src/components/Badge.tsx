interface BadgeProps { label: string; variant?: 'green' | 'amber' | 'red' | 'blue' | 'slate' }

const MAP: Record<string, BadgeProps['variant']> = {
  ALLOWED: 'green', APPROVED: 'green', paid: 'green', created: 'blue', processed: 'green',
  PENDING: 'amber', APPROVAL_REQUIRED: 'amber', expired: 'amber',
  REJECTED: 'red', failed: 'red',
}

const COLORS: Record<NonNullable<BadgeProps['variant']>, string> = {
  green: 'bg-emerald-100 text-emerald-700 ring-emerald-200',
  amber: 'bg-amber-100 text-amber-700 ring-amber-200',
  red:   'bg-red-100 text-red-700 ring-red-200',
  blue:  'bg-blue-100 text-blue-700 ring-blue-200',
  slate: 'bg-slate-100 text-slate-600 ring-slate-200',
}

export function Badge({ label, variant }: BadgeProps) {
  const v = variant ?? MAP[label] ?? 'slate'
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${COLORS[v]}`}>
      {label}
    </span>
  )
}
