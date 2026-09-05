import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { runSimulation, type SimulateRequest, type TranscriptStep } from '../api/client'
import { Card, PageHeader, ErrorMsg } from '../components/ui'

const ACTORS: Record<string, string> = {
  buyer_agent: 'Buyer Agent',
  merchant_agent: 'Merchant Agent',
  orchestrator: 'Orchestrator',
}

const ACTOR_COLORS: Record<string, string> = {
  buyer_agent: 'bg-blue-100 text-blue-700',
  merchant_agent: 'bg-emerald-100 text-emerald-700',
  orchestrator: 'bg-slate-100 text-slate-600',
}

function TranscriptCard({ step }: { step: TranscriptStep }) {
  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-200 text-xs font-bold text-slate-600">
          {step.step}
        </div>
        <div className="mt-1 flex-1 w-px bg-slate-200" />
      </div>
      <div className="mb-4 flex-1">
        <div className="flex items-center gap-2 mb-1.5">
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${ACTOR_COLORS[step.actor] ?? 'bg-slate-100 text-slate-600'}`}>
            {ACTORS[step.actor] ?? step.actor}
          </span>
          <span className="text-xs text-slate-400">{step.action}</span>
        </div>
        <Card className="p-3">
          <pre className="whitespace-pre-wrap text-xs text-slate-700 font-mono">
            {JSON.stringify(step.detail, null, 2)}
          </pre>
        </Card>
      </div>
    </div>
  )
}

export function BuyerSimulator() {
  const location = useLocation()
  const preProduct = (location.state as { product?: { product_id: string } } | null)?.product

  const [form, setForm] = useState<SimulateRequest>({
    buyer_id: 'BUYER_DEFAULT_001',
    product_id: preProduct?.product_id ?? 'PROD_001',
    quantity: 1,
    desired_discount: 0.10,
  })

  const mutation = useMutation({ 
    mutationFn: runSimulation,
    onSuccess: (data) => {
      toast.success(`Simulation completed: ${data.status.replace(/_/g, ' ').toUpperCase()}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Simulation failed — check backend connection')
    }
  })

  const set = (k: keyof SimulateRequest, v: string | number) =>
    setForm(f => ({ ...f, [k]: v }))

  const STATUS_COLOR: Record<string, string> = {
    payment_pending: 'bg-blue-50 border-blue-200 text-blue-700',
    approval_required: 'bg-amber-50 border-amber-200 text-amber-700',
    rejected: 'bg-red-50 border-red-200 text-red-700',
    budget_exceeded: 'bg-orange-50 border-orange-200 text-orange-700',
  }

  return (
    <div>
      <PageHeader title="Buyer Simulator" subtitle="Run an AI-to-AI commerce transaction end-to-end" />
      <div className="grid gap-6 lg:grid-cols-5">
        {/* Form */}
        <Card className="p-5 lg:col-span-2">
          <h2 className="mb-4 text-sm font-semibold text-slate-700">Transaction Parameters</h2>
          <div className="space-y-4">
            <label className="block">
              <span className="text-xs font-medium text-slate-600">Buyer ID</span>
              <input value={form.buyer_id} onChange={e => set('buyer_id', e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-slate-600">Product ID</span>
              <input value={form.product_id} onChange={e => set('product_id', e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-slate-600">Quantity</span>
              <input type="number" min={1} value={form.quantity} onChange={e => set('quantity', Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-slate-600">
                Desired Discount — {(form.desired_discount * 100).toFixed(0)}%
              </span>
              <input type="range" min={0} max={0.30} step={0.01} value={form.desired_discount}
                onChange={e => set('desired_discount', Number(e.target.value))}
                className="mt-2 w-full accent-blue-600" />
              <div className="flex justify-between text-xs text-slate-400 mt-0.5">
                <span>0%</span><span>30%</span>
              </div>
            </label>
            <button
              onClick={() => mutation.mutate(form)}
              disabled={mutation.isPending}
              className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {mutation.isPending ? 'Running…' : 'Start Purchase'}
            </button>
          </div>
        </Card>

        {/* Transcript */}
        <div className="lg:col-span-3">
          {mutation.error && <ErrorMsg msg="Simulation failed — check backend connection" />}

          {mutation.data && (
            <div className="space-y-4">
              <div className={`rounded-xl border px-4 py-3 text-sm font-semibold ${STATUS_COLOR[mutation.data.status] ?? 'bg-slate-50 border-slate-200 text-slate-700'}`}>
                Result: {mutation.data.status.replace(/_/g, ' ').toUpperCase()}
                {mutation.data.final_price != null && (
                  <span className="ml-3 font-normal">
                    · Final Price: ₹{Number(mutation.data.final_price).toLocaleString('en-IN')}
                  </span>
                )}
              </div>

              {mutation.data.payment && (
                <Card className="p-4">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Payment Details</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(mutation.data.payment).map(([k, v]) => (
                      <div key={k} className="rounded bg-slate-50 p-2">
                        <p className="text-slate-400">{k}</p>
                        <p className="font-medium text-slate-800 truncate">{String(v)}</p>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              <Card className="p-5">
                <p className="mb-4 text-xs font-semibold uppercase tracking-wide text-slate-500">Conversation Transcript</p>
                <div>
                  {mutation.data.transcript.map((step, i) => (
                    <TranscriptCard key={i} step={step} />
                  ))}
                </div>
              </Card>
            </div>
          )}

          {!mutation.data && !mutation.isPending && (
            <Card className="flex flex-col items-center justify-center py-20 text-slate-400">
              <svg className="mb-3 h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm">Configure parameters and click Start Purchase</p>
            </Card>
          )}

          {mutation.isPending && (
            <Card className="flex flex-col items-center justify-center py-20">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600 mb-3" />
              <p className="text-sm text-slate-500">AI agents negotiating…</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
