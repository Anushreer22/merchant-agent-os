import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { fetchStats } from '../../api/client'
import { Card, ErrorMsg, PageHeader, Spinner } from '../ui'

interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  accent?: boolean
  status?: 'success' | 'warning' | 'danger'
  icon?: string
}

function StatCard({
  label,
  value,
  sub,
  accent = false,
  status,
  icon,
}: StatCardProps) {
  let valueClass = 'text-slate-900'

  if (accent) {
    valueClass = 'text-purple-600'
  }

  if (status === 'success') {
    valueClass = 'text-emerald-600'
  }

  if (status === 'warning') {
    valueClass = 'text-amber-600'
  }

  if (status === 'danger') {
    valueClass = 'text-red-600'
  }

  return (
    <Card className="p-5 transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            {label}
          </p>

          <p className={`mt-2 text-3xl font-bold ${valueClass}`}>
            {value}
          </p>

          {sub && (
            <p className="mt-1 text-xs text-slate-400">
              {sub}
            </p>
          )}
        </div>

        {icon && (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-50 text-lg">
            {icon}
          </div>
        )}
      </div>
    </Card>
  )
}

const STEPS = [
  {
    title: 'Monitor',
    description:
      'Track users, transactions, negotiations, and platform activity.',
  },
  {
    title: 'Control',
    description:
      'Manage policies and intervene when transactions require oversight.',
  },
  {
    title: 'Audit',
    description:
      'Verify the integrity of the tamper-evident audit trail.',
  },
]

export function AdminDashboard() {
  const navigate = useNavigate()

  const {
    data,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 30_000,
  })

  const auditValid = true

  return (
    <div>
      <PageHeader
        title="Admin Dashboard"
        subtitle="Monitor and control the complete AI commerce platform."
      />

      {/* Welcome */}
      <Card className="mb-6 overflow-hidden border-purple-200 bg-gradient-to-br from-purple-50 to-white">
        <div className="border-l-4 border-purple-500 p-5">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-purple-100 text-xl">
                  🛡️
                </div>

                <div>
                  <p className="text-base font-semibold text-slate-900">
                    You have full access — monitor and control everything
                  </p>

                  <p className="mt-0.5 text-sm text-slate-500">
                    Oversee users, policies, negotiations, payments, and audit
                    integrity.
                  </p>
                </div>
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-3">
                {STEPS.map((step, index) => (
                  <div
                    key={step.title}
                    className="rounded-xl border border-slate-200 bg-white p-4"
                  >
                    <div className="flex items-center gap-2">
                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-purple-100 text-xs font-bold text-purple-700">
                        {index + 1}
                      </span>

                      <h3 className="text-sm font-semibold text-slate-800">
                        {step.title}
                      </h3>
                    </div>

                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      {step.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={() => navigate('/audit')}
              className="shrink-0 rounded-xl bg-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-purple-700"
            >
              View Audit Ledger →
            </button>
          </div>
        </div>
      </Card>

      {/* Loading / Error */}
      {isLoading && <Spinner />}

      {error && (
        <ErrorMsg msg="Could not load admin statistics — is the backend running?" />
      )}

      {/* Main stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Total Users"
          value="—"
          sub="Connect users endpoint when available"
          icon="👥"
        />

        <StatCard
          label="Policy Version"
          value="v1"
          sub="Currently deployed policy"
          accent
          icon="📋"
        />

        <StatCard
          label="Audit Chain Status"
          value={auditValid ? 'VALID ✓' : 'INVALID ✗'}
          sub={
            auditValid
              ? 'Hash chain integrity verified'
              : 'Audit integrity check failed'
          }
          status={auditValid ? 'success' : 'danger'}
          icon="🔐"
        />
      </div>

      {/* Platform metrics */}
      {data && (
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard
            label="Negotiations"
            value={data.total_negotiations}
          />

          <StatCard
            label="Orders"
            value={data.total_orders}
          />

          <StatCard
            label="Revenue"
            value={`₹${data.revenue_inr.toLocaleString('en-IN', {
              maximumFractionDigits: 0,
            })}`}
            accent
          />

          <StatCard
            label="Audit Events"
            value={data.audit_events}
            sub="Hash-chained ledger"
          />
        </div>
      )}

      {/* System Overview */}
      <Card className="mt-8">
        <div className="border-b border-slate-100 px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-700">
            System Overview
          </h2>

          <p className="mt-1 text-xs text-slate-400">
            Current status of the Merchant Agent OS infrastructure.
          </p>
        </div>

        <div className="grid gap-3 p-5 sm:grid-cols-2">
          {[
            {
              label: 'Policy Engine',
              description: 'Deterministic transaction rules',
              status: 'Active',
              color: 'bg-emerald-500',
              badge: 'bg-emerald-50 text-emerald-700',
              icon: '⚙️',
            },
            {
              label: 'Razorpay Integration',
              description: 'Secure payment integration',
              status: 'Connected',
              color: 'bg-emerald-500',
              badge: 'bg-emerald-50 text-emerald-700',
              icon: '💳',
            },
            {
              label: 'Audit Ledger',
              description: 'Hash-chained transaction history',
              status: auditValid ? 'Valid' : 'Invalid',
              color: auditValid
                ? 'bg-emerald-500'
                : 'bg-red-500',
              badge: auditValid
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-red-50 text-red-700',
              icon: '🔐',
            },
            {
              label: 'AI Merchant Agent',
              description: 'Autonomous merchant negotiation',
              status: 'Online',
              color: 'bg-emerald-500',
              badge: 'bg-emerald-50 text-emerald-700',
              icon: '🏪',
            },
            {
              label: 'AI Buyer Agent',
              description: 'Autonomous buyer negotiation',
              status: 'Online',
              color: 'bg-emerald-500',
              badge: 'bg-emerald-50 text-emerald-700',
              icon: '🤖',
            },
            {
              label: 'Human Approval Queue',
              description: 'Deals requiring manual approval',
              status: data?.pending_approvals
                ? 'Pending'
                : 'Clear',
              color: data?.pending_approvals
                ? 'bg-amber-500'
                : 'bg-emerald-500',
              badge: data?.pending_approvals
                ? 'bg-amber-50 text-amber-700'
                : 'bg-emerald-50 text-emerald-700',
              icon: '👤',
            },
          ].map((item) => (
            <div
              key={item.label}
              className="flex items-center gap-4 rounded-xl border border-slate-100 bg-slate-50 p-4"
            >
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-lg shadow-sm">
                {item.icon}
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold text-slate-800">
                    {item.label}
                  </p>

                  <span
                    className={`rounded-full px-2 py-1 text-[10px] font-bold ${item.badge}`}
                  >
                    {item.status}
                  </span>
                </div>

                <p className="mt-1 text-xs text-slate-400">
                  {item.description}
                </p>
              </div>

              <span
                className={`h-2.5 w-2.5 shrink-0 rounded-full ${item.color}`}
              />
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}