import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchAudit, fetchAuditVerify } from '../api/client'
import { ErrorMsg, Card, PageHeader, EmptyState } from '../components/ui'
import { Badge } from '../components/Badge'
import { SkeletonTable } from '../components/Skeleton'

function fmt(d: string) {
  return new Date(d).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

function truncHash(h: string) {
  return h.length > 16 ? `${h.slice(0, 8)}…${h.slice(-8)}` : h
}

export function Audit() {
  const { data, isLoading, error } = useQuery({ queryKey: ['audit'], queryFn: fetchAudit })
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; events_checked: number; first_invalid_event_id: string | null } | null>(null)
  const [verifying, setVerifying] = useState(false)

  const verify = async () => {
    setVerifying(true)
    try {
      const r = await fetchAuditVerify()
      setVerifyResult(r)
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <PageHeader title="Audit Ledger" subtitle="Immutable hash-chained event log" />
        <button
          onClick={verify}
          disabled={verifying}
          title="Check if the audit ledger hash chain has been tampered with"
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-50 transition-colors"
        >
          {verifying ? 'Verifying…' : 'VERIFY CHAIN'}
        </button>
      </div>

      {verifyResult && (
        <div className={`mb-6 flex items-center gap-3 rounded-xl border px-5 py-4 text-sm font-semibold ${
          verifyResult.valid
            ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
            : 'border-red-200 bg-red-50 text-red-700'
        }`}>
          <span className="text-xl">{verifyResult.valid ? '✓' : '✗'}</span>
          <div>
            <p>{verifyResult.valid ? 'CHAIN VALID' : 'TAMPERING DETECTED'}</p>
            <p className="text-xs font-normal mt-0.5">
              {verifyResult.events_checked} events checked
              {!verifyResult.valid && verifyResult.first_invalid_event_id &&
                ` · First invalid: ${verifyResult.first_invalid_event_id}`}
            </p>
          </div>
        </div>
      )}

      {isLoading && <SkeletonTable rows={5} columns={9} />}
      {error && <ErrorMsg msg="Failed to load audit events" />}
      {data?.length === 0 && <EmptyState label="No audit events recorded yet" />}
      {data && data.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left">
                  {['Event ID','Timestamp','Actor','Action','Policy Ver','Negotiation','Payload Hash','Prev Hash','Hash'].map(h => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500 whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map(e => (
                  <tr key={e.event_id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-700">{e.event_id}</td>
                    <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">{fmt(e.timestamp)}</td>
                    <td className="px-4 py-3"><Badge label={e.actor} variant="blue" /></td>
                    <td className="px-4 py-3 text-xs text-slate-700 whitespace-nowrap">{e.action_type}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">{e.policy_version ?? '—'}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">
                      {e.negotiation_id ? `${e.negotiation_id.slice(0, 8)}…` : '—'}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-400" title={e.payload_hash}>{truncHash(e.payload_hash)}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-400" title={e.previous_hash}>{truncHash(e.previous_hash)}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-400" title={e.hash}>{truncHash(e.hash)}</td>
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
