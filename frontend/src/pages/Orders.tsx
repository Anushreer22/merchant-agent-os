import { useQuery } from '@tanstack/react-query'
import { fetchOrders } from '../api/client'
import { Spinner, ErrorMsg, Card, PageHeader, EmptyState } from '../components/ui'
import { Badge } from '../components/Badge'

function fmt(d: string) {
  return new Date(d).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

export function Orders() {
  const { data, isLoading, error } = useQuery({ queryKey: ['orders'], queryFn: fetchOrders })

  return (
    <div>
      <PageHeader title="Orders" subtitle="Razorpay orders created from negotiations" />
      {isLoading && <Spinner />}
      {error && <ErrorMsg msg="Failed to load orders" />}
      {data?.length === 0 && <EmptyState label="No orders yet" />}
      {data && data.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  {['Order ID','Negotiation ID','Amount','Currency','Receipt','Status','Created'].map(h => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map(o => (
                  <tr key={o.order_id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-700">{o.order_id}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{o.negotiation_id.slice(0, 8)}…</td>
                    <td className="px-4 py-3 font-semibold text-slate-900">₹{Number(o.amount).toLocaleString('en-IN')}</td>
                    <td className="px-4 py-3 text-slate-600">{o.currency}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{o.receipt}</td>
                    <td className="px-4 py-3"><Badge label={o.status} /></td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{fmt(o.created_at)}</td>
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
