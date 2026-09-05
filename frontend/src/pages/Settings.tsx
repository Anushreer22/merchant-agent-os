import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { runResetDemo } from '../api/client'
import { Card, PageHeader } from '../components/ui'

export function Settings() {
  const { user } = useAuth()
  const [resetting, setResetting] = useState(false)
  const qc = useQueryClient()

  const handleReset = async () => {
    setResetting(true)
    try {
      await runResetDemo()
      toast.success('Demo data reset successfully')
      qc.invalidateQueries()
    } catch {
      toast.error('Failed to reset demo data')
    } finally {
      setResetting(false)
    }
  }
  const ENV = [
    { key: 'VITE_API_URL', value: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1 (default)', desc: 'Backend API base URL' },
    { key: 'Backend', value: 'FastAPI + SQLAlchemy + PostgreSQL', desc: 'Runtime stack' },
    { key: 'Payments', value: 'Razorpay (sandbox)', desc: 'Payment provider' },
    { key: 'AI Agent', value: 'OpenAI GPT-4o-mini', desc: 'LLM for merchant agent' },
    { key: 'Audit', value: 'SHA-256 hash-chained ledger', desc: 'Tamper-evident event log' },
  ]

  return (
    <div>
      <PageHeader title="Settings" subtitle="Environment configuration and platform information" />
      <div className="max-w-2xl space-y-4">
        <Card className="p-5">
          <p className="mb-4 text-sm font-semibold text-slate-700">Environment</p>
          <div className="space-y-2">
            {ENV.map(({ key, value, desc }) => (
              <div key={key} className="flex items-start justify-between rounded-lg bg-slate-50 px-4 py-3">
                <div>
                  <p className="text-xs font-mono font-medium text-slate-700">{key}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{desc}</p>
                </div>
                <span className="text-xs text-slate-600 font-medium text-right max-w-xs">{value}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-5">
          <p className="mb-4 text-sm font-semibold text-slate-700">Demo Data</p>
          <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-700">
            This is a demonstration environment. No real transactions are processed.
            Razorpay credentials are in sandbox mode.
          </div>
          <div className="mt-3 space-y-2 text-sm text-slate-600">
            <p>• Default buyer: <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono">BUYER_DEFAULT_001</code></p>
            <p>• Default product: <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono">SUB_PRO_001</code></p>
            <p>• Policy version: <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono">1.0</code></p>
          </div>
          {user?.role === 'admin' && (
            <button
              onClick={handleReset}
              disabled={resetting}
              className="mt-4 rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {resetting ? 'Resetting...' : 'Reset Demo Data'}
            </button>
          )}
        </Card>

        <Card className="p-5">
          <p className="mb-3 text-sm font-semibold text-slate-700">About</p>
          <p className="text-sm text-slate-600">
            <strong>Merchant Agent OS</strong> is an AI-powered commerce platform that enables autonomous
            buyer-merchant negotiations, policy-enforced discounts, human-in-the-loop approvals,
            and Razorpay payment processing — all with a tamper-evident audit trail.
          </p>
        </Card>
      </div>
    </div>
  )
}
