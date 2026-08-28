import { useQuery } from '@tanstack/react-query'
import { fetchPolicy } from '../api/client'
import { Spinner, ErrorMsg, Card, PageHeader } from '../components/ui'

export function Policies() {
  const { data, isLoading, error } = useQuery({ queryKey: ['policy'], queryFn: fetchPolicy })

  return (
    <div>
      <PageHeader title="Active Policy" subtitle="Discount and approval rules enforced by the policy engine" />
      {isLoading && <Spinner />}
      {error && <ErrorMsg msg="Failed to load policy" />}
      {data && (
        <div className="max-w-2xl space-y-4">
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="font-semibold text-slate-900">Policy v{data.version}</p>
                <p className="text-xs text-slate-400 mt-0.5">
                  Created {new Date(data.created_at).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                </p>
              </div>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Active
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Max Auto Discount', value: `${(data.rules.max_auto_discount * 100).toFixed(0)}%`, desc: 'Approved automatically' },
                { label: 'Max Human Approved Discount', value: `${(data.rules.max_human_approved_discount * 100).toFixed(0)}%`, desc: 'Requires human approval' },
                { label: 'Margin Floor', value: `${(data.rules.margin_floor * 100).toFixed(0)}%`, desc: 'Minimum margin to protect' },
                { label: 'Human Approval Threshold', value: `₹${data.rules.human_approval_amount.toLocaleString('en-IN')}`, desc: 'Amount above which approval needed' },
                { label: 'Max Qty Without Approval', value: `${data.rules.max_quantity_without_approval} units`, desc: 'Bulk order threshold' },
                { label: 'Max Retry Count', value: `${data.rules.max_retry_count}`, desc: 'Payment retry attempts' },
              ].map(({ label, value, desc }) => (
                <div key={label} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                  <p className="text-xs text-slate-400">{label}</p>
                  <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
                  <p className="mt-1 text-xs text-slate-500">{desc}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5">
            <p className="mb-3 text-sm font-semibold text-slate-700">Decision Flow</p>
            <div className="space-y-2 text-sm">
              {[
                { range: `0 – ${(data.rules.max_auto_discount * 100).toFixed(0)}%`, label: 'Auto-Approved', color: 'bg-emerald-500' },
                { range: `${(data.rules.max_auto_discount * 100).toFixed(0)}% – ${(data.rules.max_human_approved_discount * 100).toFixed(0)}%`, label: 'Human Approval Required', color: 'bg-amber-500' },
                { range: `> ${(data.rules.max_human_approved_discount * 100).toFixed(0)}%`, label: 'Rejected', color: 'bg-red-500' },
              ].map(({ range, label, color }) => (
                <div key={label} className="flex items-center gap-3 rounded-lg bg-slate-50 px-4 py-2.5">
                  <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
                  <span className="font-mono text-xs text-slate-500 w-28">{range}</span>
                  <span className="text-slate-700">{label}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
