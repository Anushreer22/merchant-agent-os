import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchNegotiations, type Negotiation } from '../api/client'
import { Spinner, ErrorMsg, Card, PageHeader, EmptyState } from '../components/ui'
import { Badge } from '../components/Badge'

function fmt(d: string) {
  return new Date(d).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

function DetailModal({ neg, onClose }: { neg: Negotiation; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg"
        onClick={(e: React.MouseEvent) => e.stopPropagation()}
      >
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="font-semibold text-slate-900">Negotiation Detail</h2>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">{neg.negotiation_id}</p>
            </div>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {([
              ['Buyer', neg.buyer_id],
              ['Product', neg.product_id],
              ['Quantity', String(neg.quantity)],
              ['Decision', neg.decision],
              ['Status', neg.status],
              ['Requested Discount', `${(neg.requested_discount * 100).toFixed(1)}%`],
              ['Final Discount', `${(neg.final_discount * 100).toFixed(1)}%`],
              ['Final Amount', `₹${Number(neg.final_amount).toLocaleString('en-IN')}`],
              ['Policy Version', neg.policy_version],
              ['Reason Code', neg.reason_code],
              ['Human Approval', neg.requires_human_approval ? 'Yes' : 'No'],
              ['Created', fmt(neg.created_at)],
            ] as [string, string][]).map(([k, v]) => (
              <div key={k} className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs text-slate-400">{k}</p>
                <div className="mt-0.5 font-medium text-slate-800">
                  {k === 'Decision' ? <Badge label={v} /> : k === 'Status' ? <Badge label={v} /> : v}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}

export function Negotiations() {
  const { data, isLoading, error } = useQuery({ queryKey: ['negotiations'], queryFn: fetchNegotiations })
  const [selected, setSelected] = useState<Negotiation | null>(null)

  return (
    <div>
      <PageHeader title="Negotiations" subtitle="All AI-to-AI and manual negotiations" />
      {isLoading && <Spinner />}
      {error && <ErrorMsg msg="Failed to load negotiations" />}
      {data?.length === 0 && <EmptyState label="No negotiations yet" />}
      {data && data.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  {['ID','Buyer','Product','Qty','Req. Disc','Final Disc','Amount','Decision','Status','Created'].map(h => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map(n => (
                  <tr
                    key={n.negotiation_id}
                    onClick={() => setSelected(n)}
                    className="border-b border-slate-50 hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{n.negotiation_id.slice(0, 8)}…</td>
                    <td className="px-4 py-3 text-slate-700">{n.buyer_id}</td>
                    <td className="px-4 py-3 text-slate-700">{n.product_id}</td>
                    <td className="px-4 py-3 text-slate-700">{n.quantity}</td>
                    <td className="px-4 py-3 text-slate-700">{(n.requested_discount * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3 text-slate-700">{(n.final_discount * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3 font-medium text-slate-900">₹{Number(n.final_amount).toLocaleString('en-IN')}</td>
                    <td className="px-4 py-3"><Badge label={n.decision} /></td>
                    <td className="px-4 py-3"><Badge label={n.status} /></td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{fmt(n.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
      {selected && <DetailModal neg={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}
