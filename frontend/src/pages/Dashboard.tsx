import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { fetchStats } from '../api/client'
import { Spinner, ErrorMsg, Card, PageHeader } from '../components/ui'

const CHART_DATA = [
  { day: 'Mon', negotiations: 4, orders: 2 },
  { day: 'Tue', negotiations: 7, orders: 5 },
  { day: 'Wed', negotiations: 3, orders: 3 },
  { day: 'Thu', negotiations: 9, orders: 6 },
  { day: 'Fri', negotiations: 12, orders: 8 },
  { day: 'Sat', negotiations: 5, orders: 4 },
  { day: 'Sun', negotiations: 6, orders: 5 },
]

function StatCard({ label, value, sub, accent = false }: {
  label: string; value: string | number; sub?: string; accent?: boolean
}) {
  return (
    <Card className="p-5">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${accent ? 'text-blue-600' : 'text-slate-900'}`}>{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-400">{sub}</p>}
    </Card>
  )
}

export function Dashboard() {
  const { data, isLoading, error } = useQuery({ queryKey: ['stats'], queryFn: fetchStats, refetchInterval: 30_000 })

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Real-time overview of your AI commerce platform" />

      {isLoading && <Spinner />}
      {error && <ErrorMsg msg="Could not load stats — is the backend running?" />}

      {data && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Total Negotiations" value={data.total_negotiations} />
          <StatCard label="Successful Payments" value={data.paid_orders} accent />
          <StatCard label="Pending Approvals" value={data.pending_approvals}
            sub={data.pending_approvals > 0 ? 'Action required' : 'All clear'} />
          <StatCard label="Total Orders" value={data.total_orders} />
          <StatCard label="Revenue (INR)" value={`₹${data.revenue_inr.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`} accent />
          <StatCard label="Avg Discount" value={`${data.avg_discount_pct}%`} sub="Across all negotiations" />
          <StatCard label="Allowed" value={data.allowed_negotiations}
            sub={`${data.rejected_negotiations} rejected`} />
          <StatCard label="Audit Events" value={data.audit_events} sub="Hash-chained ledger" />
        </div>
      )}

      {!data && !isLoading && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {['Total Negotiations','Successful Payments','Pending Approvals','Total Orders',
            'Revenue (INR)','Avg Discount','Allowed','Audit Events'].map(l => (
            <Card key={l} className="p-5 animate-pulse">
              <div className="h-3 w-24 rounded bg-slate-200" />
              <div className="mt-3 h-8 w-16 rounded bg-slate-200" />
            </Card>
          ))}
        </div>
      )}

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-700">Weekly Activity</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={CHART_DATA} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
              <Bar dataKey="negotiations" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Negotiations" />
              <Bar dataKey="orders" fill="#10b981" radius={[4, 4, 0, 0]} name="Orders" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-700">Platform Overview</h2>
          <div className="space-y-3">
            {[
              { label: 'Policy Engine', status: 'Active', color: 'bg-emerald-500' },
              { label: 'Razorpay Integration', status: 'Connected', color: 'bg-emerald-500' },
              { label: 'Audit Ledger', status: 'Recording', color: 'bg-blue-500' },
              { label: 'AI Merchant Agent', status: 'Online', color: 'bg-emerald-500' },
              { label: 'AI Buyer Agent', status: 'Online', color: 'bg-emerald-500' },
              { label: 'Human Approval Queue', status: data?.pending_approvals ? 'Pending' : 'Clear', color: data?.pending_approvals ? 'bg-amber-500' : 'bg-emerald-500' },
            ].map(({ label, status, color }) => (
              <div key={label} className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-2.5">
                <span className="text-sm text-slate-700">{label}</span>
                <span className="flex items-center gap-2 text-xs font-medium text-slate-600">
                  <span className={`h-2 w-2 rounded-full ${color}`} />
                  {status}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
