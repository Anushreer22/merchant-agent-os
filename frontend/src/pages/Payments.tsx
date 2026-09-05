import { useQuery } from '@tanstack/react-query'
import { fetchPaymentLinks } from '../api/client'
import { ErrorMsg, Card, PageHeader, EmptyState } from '../components/ui'
import { Badge } from '../components/Badge'
import { SkeletonTable } from '../components/Skeleton'

function fmt(d: string) {
  return new Date(d).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

export function Payments() {
  const { data, isLoading, error } = useQuery({ queryKey: ['payment-links'], queryFn: fetchPaymentLinks })

  return (
    <div>
      <PageHeader title="Payment Links" subtitle="Razorpay payment links generated for orders" />
      {isLoading && <SkeletonTable rows={5} columns={6} />}
      {error && <ErrorMsg msg="Failed to load payment links" />}
      {data?.length === 0 && <EmptyState label="No payment links yet" />}
      {data && data.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  {['Link ID','Order ID','Negotiation ID','Short URL','Status','Created'].map(h => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map(l => (
                  <tr key={l.link_id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-700">{l.link_id}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{l.order_id}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{l.negotiation_id.slice(0, 8)}…</td>
                    <td className="px-4 py-3">
                      {l.short_url ? (
                        <a href={l.short_url} target="_blank" rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-xs">
                          {l.short_url}
                        </a>
                      ) : <span className="text-slate-400 text-xs">—</span>}
                    </td>
                    <td className="px-4 py-3"><Badge label={l.status} /></td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{fmt(l.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
