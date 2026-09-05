import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { fetchApprovals, decideApproval } from '../api/client'
import { ErrorMsg, Card, PageHeader } from '../components/ui'
import { Badge } from '../components/Badge'
import { SkeletonTable } from '../components/Skeleton'

function fmt(d: string | null) {
  return d ? new Date(d).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : '—'
}

export function Approvals() {
  const qc = useQueryClient()
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({ queryKey: ['approvals'], queryFn: fetchApprovals })
  const [deciding, setDeciding] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: string }) => decideApproval(id, decision),
    onSuccess: (_, { decision }) => {
      qc.invalidateQueries({ queryKey: ['approvals'] })
      setDeciding(null)
      toast.success(decision === 'APPROVED' ? 'Approval granted' : 'Deal rejected')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Action failed — please try again')
    }
  })

  return (
    <div>
      <PageHeader title="Approvals" subtitle="Human-in-the-loop approval queue" />
      {isLoading && <SkeletonTable rows={5} columns={10} />}
      {error && <ErrorMsg msg="Failed to load approvals" />}

      {data?.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-slate-400">
          <svg className="mb-3 h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm mb-3">No approvals pending — all clear!</p>
          <button
            onClick={() => navigate('/negotiations')}
            className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 transition-colors"
          >
            View negotiations →
          </button>
        </div>
      )}

      {data && data.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  {['Approval ID', 'Negotiation', 'Buyer', 'Product', 'Amount', 'Req. Disc', 'Proposed Disc', 'Status', 'Created', 'Actions'].map(h => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map(a => (
                  <tr key={a.approval_id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{a.approval_id.slice(0, 12)}…</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{a.negotiation_id.slice(0, 8)}…</td>
                    <td className="px-4 py-3 text-slate-700">{a.buyer_id}</td>
                    <td className="px-4 py-3 text-slate-700">{a.product_id}</td>
                    <td className="px-4 py-3 font-medium text-slate-900">₹{Number(a.final_price).toLocaleString('en-IN')}</td>
                    <td className="px-4 py-3">{(a.requested_discount * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3">{(a.proposed_discount * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3"><Badge label={a.status} /></td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{fmt(a.created_at)}</td>
                    <td className="px-4 py-3">
                      {a.status === 'PENDING' ? (
                        <div className="flex gap-2">
                          <button
                            title="Approve this negotiation to allow the buyer to proceed to payment"
                            onClick={() => { setDeciding(a.approval_id); mutation.mutate({ id: a.approval_id, decision: 'APPROVED' }) }}
                            disabled={mutation.isPending && deciding === a.approval_id}
                            className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            title="Reject this negotiation — the buyer's offer will not proceed"
                            onClick={() => { setDeciding(a.approval_id); mutation.mutate({ id: a.approval_id, decision: 'REJECTED' }) }}
                            disabled={mutation.isPending && deciding === a.approval_id}
                            className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700 disabled:opacity-50 transition-colors"
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-400">{a.human_user_id ?? '—'}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
      {mutation.error && <div className="mt-4"><ErrorMsg msg="Action failed — please try again" /></div>}
    </div>
  )
}
