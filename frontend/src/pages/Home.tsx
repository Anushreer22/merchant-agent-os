import { Link } from 'react-router-dom'

const FEATURES = [
  {
    icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    title: 'AI-to-AI Commerce',
    desc: 'Buyer and Merchant agents negotiate autonomously using structured policy rules — no LLM required for core flows.',
    color: 'bg-blue-50 text-blue-600',
  },
  {
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
    title: 'Deterministic Policy Engine',
    desc: 'Discount rules, margin floors, and approval thresholds enforced consistently on every transaction.',
    color: 'bg-emerald-50 text-emerald-600',
  },
  {
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    title: 'Human Approval Queue',
    desc: 'Deals above policy thresholds are automatically escalated for human review before proceeding.',
    color: 'bg-amber-50 text-amber-600',
  },
  {
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    title: 'Immutable Audit Trail',
    desc: 'Every negotiation, approval, and payment is hash-chained into a tamper-evident ledger.',
    color: 'bg-purple-50 text-purple-600',
  },
  {
    icon: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
    title: 'Razorpay Integration',
    desc: 'Orders and payment links created automatically on deal approval. Webhook-driven status updates.',
    color: 'bg-rose-50 text-rose-600',
  },
  {
    icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
    title: 'Role-Based Access',
    desc: 'Admin, Merchant, and Buyer roles with JWT authentication. Protected routes and scoped permissions.',
    color: 'bg-slate-100 text-slate-600',
  },
]

const ARCH_NODES = [
  { label: 'Buyer Agent', x: 60, y: 40, color: '#3b82f6' },
  { label: 'Orchestrator', x: 220, y: 40, color: '#6366f1' },
  { label: 'Merchant Agent', x: 380, y: 40, color: '#10b981' },
  { label: 'Policy Engine', x: 220, y: 130, color: '#f59e0b' },
  { label: 'Razorpay', x: 380, y: 130, color: '#ef4444' },
  { label: 'Audit Ledger', x: 60, y: 130, color: '#8b5cf6' },
]

const ARCH_EDGES = [
  [0, 1], [1, 2], [1, 3], [2, 3], [2, 4], [1, 5],
]

export function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="sticky top-0 z-10 border-b border-slate-100 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
              <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-slate-900">Merchant Agent OS</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
              Sign In
            </Link>
            <Link to="/signup" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition-colors">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-4 py-1.5 text-xs font-medium text-blue-700 mb-6">
          <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
          AI-Powered Commerce Platform
        </div>
        <h1 className="text-5xl font-bold tracking-tight text-slate-900 sm:text-6xl">
          Autonomous AI Commerce,<br />
          <span className="text-blue-600">Policy-Governed</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-500">
          Merchant Agent OS orchestrates AI buyer and seller agents to negotiate, approve, and settle
          transactions — with deterministic policy enforcement and a full audit trail.
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link to="/signup" className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 transition-colors shadow-sm">
            Start Free →
          </Link>
          <Link to="/login" className="rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors">
            Sign In
          </Link>
          <Link to="/dashboard" className="rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors">
            Live Demo
          </Link>
        </div>

        {/* Stats bar */}
        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-3 gap-8 rounded-2xl border border-slate-100 bg-slate-50 px-8 py-6">
          {[
            { label: 'Policy Rules', value: '6' },
            { label: 'Audit Events', value: '∞' },
            { label: 'Uptime', value: '99.9%' },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="text-3xl font-bold text-slate-900">{value}</p>
              <p className="mt-1 text-xs text-slate-500">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="bg-slate-50 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900">Everything you need</h2>
            <p className="mt-3 text-slate-500">A complete platform for AI-driven B2B commerce</p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ icon, title, desc, color }) => (
              <div key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className={`mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl ${color}`}>
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d={icon} />
                  </svg>
                </div>
                <h3 className="mb-2 font-semibold text-slate-900">{title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900">System Architecture</h2>
            <p className="mt-3 text-slate-500">How the agents, policy engine, and payments connect</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-8 flex justify-center">
            <svg viewBox="0 0 480 200" className="w-full max-w-2xl" aria-label="Architecture diagram">
              {ARCH_EDGES.map(([a, b], i) => {
                const na = ARCH_NODES[a], nb = ARCH_NODES[b]
                return (
                  <line key={i}
                    x1={na.x + 55} y1={na.y + 18} x2={nb.x + 55} y2={nb.y + 18}
                    stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="4 3"
                  />
                )
              })}
              {ARCH_NODES.map(({ label, x, y, color }) => (
                <g key={label}>
                  <rect x={x} y={y} width={110} height={36} rx={8}
                    fill="white" stroke={color} strokeWidth="1.5" />
                  <text x={x + 55} y={y + 22} textAnchor="middle"
                    fontSize="11" fontWeight="600" fill={color}>
                    {label}
                  </text>
                </g>
              ))}
            </svg>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-blue-600 py-16">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="text-3xl font-bold text-white">Ready to automate your commerce?</h2>
          <p className="mt-4 text-blue-100">Sign up in seconds. No credit card required.</p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link to="/signup" className="rounded-xl bg-white px-6 py-3 text-sm font-semibold text-blue-600 hover:bg-blue-50 transition-colors">
              Create Account
            </Link>
            <Link to="/login" className="rounded-xl border border-blue-400 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 transition-colors">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-100 bg-white py-8">
        <div className="mx-auto max-w-6xl px-6 flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-blue-600">
              <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="text-sm font-medium text-slate-700">Merchant Agent OS</span>
          </div>
          <p className="text-xs text-slate-400">Powered by Razorpay · Built with FastAPI & React</p>
          <div className="flex gap-4 text-xs text-slate-400">
            <Link to="/login" className="hover:text-slate-600">Sign In</Link>
            <Link to="/signup" className="hover:text-slate-600">Sign Up</Link>
            <Link to="/dashboard" className="hover:text-slate-600">Dashboard</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
