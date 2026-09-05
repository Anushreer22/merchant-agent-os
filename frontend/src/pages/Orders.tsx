import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { fetchOrders, simulateWebhook } from '../api/client'
import { ErrorMsg, Card, PageHeader } from '../components/ui'
import { Badge } from '../components/Badge'
import { SkeletonTable } from '../components/Skeleton'

function fmt(d: string) {
  return new Date(d).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

function WebhookButton({ orderId, currentStatus }: { orderId: string; currentStatus: string }) {
  const qc = useQueryClient()
  const [state, setState] = useState<'idle' | 'loading' | 'done' | 'error'>('idle')

  if (currentStatus === 'paid') {
    return <span className="text-xs text-slate-400">Already paid</span>
  }

  const fire = async () => {
    setState('loading')
    try {
      await simulateWebhook(orderId)
      setState('done')
      qc.invalidateQueries({ queryKey: ['orders'] })
      toast.success('Payment marked as paid')
    } catch {
      setState('error')
      toast.error('Failed to simulate webhook — please try again')
      setTimeout(() => setState('idle'), 3000)
    }
  }

  if (state === 'done') return <span className="text-xs text-green-600 font-medium">✓ Captured</span>
  if (state === 'error') return <span className="text-xs text-red-500">Failed — retry</span>

  return (
    <button
      onClick={fire}
      disabled={state === 'loading'}
      title="Click to simulate Razorpay payment confirmation for demo — marks this order as paid"
      className="rounded-md bg-emerald-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
    >
      {state === 'loading' ? '…' : 'Simulate Webhook'}
    </button>
  )
}

export function Orders() {
  const { data, isLoading, error } = useQuery({ queryKey: ['orders'], queryFn: fetchOrders })
  const navigate = useNavigate()

  return (
    <div>
      <PageHeader title="Orders" subtitle="Razorpay orders created from negotiations" />
      {isLoading && <SkeletonTable rows={5} columns={8} />}
      {error && <ErrorMsg msg="Failed to load orders" />}

      {data?.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-slate-400">
          <svg className="mb-3 h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="text-sm mb-3">No orders yet</p>
          <button
            onClick={() => navigate('/buyer-simulator')}
            className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 transition-colors"
          >
            Create your first purchase →
          </button>
        </div>
      )}

      {data && data.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  {['Order ID', 'Negotiation ID', 'Amount', 'Currency', 'Receipt', 'Status', 'Created', 'Action'].map(h => (
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
                    <td className="px-4 py-3">
                      <WebhookButton orderId={o.order_id} currentStatus={o.status} />
                    </td>
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
