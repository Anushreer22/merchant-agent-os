import { Link } from 'react-router-dom'

type RoleCardProps = {
  role: 'buyer' | 'merchant' | 'admin'
  icon: string
  title: string
  description: string
  accent: string
  accentLight: string
  features: string[]
}

const ROLE_CARDS: RoleCardProps[] = [
  {
    role: 'buyer',
    icon: '🤖',
    title: 'AI Buyer',
    description:
      'Discover products, negotiate within your budget, and complete purchases autonomously.',
    accent: 'hover:border-emerald-400 hover:shadow-emerald-100',
    accentLight: 'bg-emerald-50 text-emerald-700',
    features: [
      'AI-powered discovery',
      'Budget-controlled negotiation',
      'Secure purchasing',
    ],
  },
  {
    role: 'merchant',
    icon: '🏪',
    title: 'Merchant Agent',
    description:
      'Manage catalog, enforce policies, approve high-value deals, and grow revenue.',
    accent: 'hover:border-blue-400 hover:shadow-blue-100',
    accentLight: 'bg-blue-50 text-blue-700',
    features: [
      'Smart negotiations',
      'Policy enforcement',
      'Approval management',
    ],
  },
  {
    role: 'admin',
    icon: '🛡️',
    title: 'Admin',
    description:
      'Monitor everything, manage users and policies, and verify audit trail integrity.',
    accent: 'hover:border-purple-400 hover:shadow-purple-100',
    accentLight: 'bg-purple-50 text-purple-700',
    features: [
      'Platform monitoring',
      'Policy management',
      'Audit verification',
    ],
  },
]

const FEATURES = [
  {
    icon: '⚡',
    title: 'Autonomous Negotiation',
    description:
      'AI agents negotiate offers in real time without requiring humans to handle every interaction.',
  },
  {
    icon: '🔒',
    title: 'Deterministic Governance',
    description:
      'Hard policy rules ensure agents never exceed approved transaction limits.',
  },
  {
    icon: '👤',
    title: 'Human-in-the-Loop',
    description:
      'High-value or sensitive transactions can be routed to humans for approval.',
  },
  {
    icon: '⛓️',
    title: 'Tamper-Proof Audit',
    description:
      'Hash-chained records create an auditable history of important platform actions.',
  },
]

const HOW_IT_WORKS = [
  {
    number: '01',
    icon: '🔎',
    title: 'Discover',
    description:
      'The AI buyer discovers products from an agent-readable merchant catalog.',
  },
  {
    number: '02',
    icon: '🤝',
    title: 'Negotiate',
    description:
      'Buyer and merchant agents negotiate while deterministic policies enforce limits.',
  },
  {
    number: '03',
    icon: '✅',
    title: 'Approve',
    description:
      'Deals outside automatic approval rules are sent to a human decision maker.',
  },
  {
    number: '04',
    icon: '💳',
    title: 'Pay & Audit',
    description:
      'Payment is processed securely and the transaction is recorded in the audit ledger.',
  },
]

export function Home() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-slate-50 text-slate-900">
      {/* =========================================================
          NAVBAR
      ========================================================== */}
      <header className="absolute left-0 right-0 top-0 z-50">
        <div className="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">
          <nav className="flex h-20 items-center justify-between">
            <Link to="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-xl ring-1 ring-white/20 backdrop-blur">
                🤖
              </div>

              <div>
                <p className="text-sm font-bold tracking-wide text-white">
                  MERCHANT AGENT
                </p>
                <p className="text-[10px] font-medium tracking-[0.25em] text-blue-300">
                  OS
                </p>
              </div>
            </Link>

            <div className="hidden items-center gap-8 md:flex">
              <a
                href="#how-it-works"
                className="text-sm font-medium text-slate-300 transition hover:text-white"
              >
                How it works
              </a>

              <a
                href="#features"
                className="text-sm font-medium text-slate-300 transition hover:text-white"
              >
                Features
              </a>

              <a
                href="#roles"
                className="text-sm font-medium text-slate-300 transition hover:text-white"
              >
                Roles
              </a>
            </div>

            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="hidden rounded-lg px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10 sm:block"
              >
                Sign in
              </Link>

              <Link
                to="/signup"
                className="rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 shadow-lg transition hover:bg-slate-100"
              >
                Get Started
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* =========================================================
          HERO
      ========================================================== */}
      <section className="relative min-h-[760px] overflow-hidden bg-slate-950">
        {/* Background effects */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_25%,rgba(37,99,235,0.28),transparent_32%),radial-gradient(circle_at_15%_80%,rgba(14,165,233,0.16),transparent_28%)]" />

        <div className="absolute right-[8%] top-32 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl" />

        <div className="absolute bottom-0 left-[25%] h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

        {/* Grid */}
        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
        />

        <div className="relative mx-auto max-w-7xl px-5 pb-20 pt-32 sm:px-6 lg:px-8 lg:pb-28 lg:pt-40">
          <div className="grid items-center gap-16 lg:grid-cols-[1.05fr_0.95fr]">
            {/* Hero copy */}
            <div>
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-400/10 px-4 py-2 text-xs font-semibold text-blue-200">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
                </span>

                AI COMMERCE INFRASTRUCTURE
              </div>

              <h1 className="max-w-4xl text-5xl font-black leading-[1.05] tracking-tight text-white sm:text-6xl lg:text-7xl">
                AI-to-AI Commerce,
                <span className="mt-2 block bg-gradient-to-r from-blue-400 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
                  Safely Governed.
                </span>
              </h1>

              <p className="mt-7 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg sm:leading-8">
                Let AI agents discover, negotiate, and transact on behalf of
                buyers and merchants — while deterministic policies, human
                approvals, secure payments, and tamper-proof audits keep every
                transaction under control.
              </p>

              <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                <Link
                  to="/signup"
                  className="group inline-flex items-center justify-center gap-2 rounded-xl bg-white px-6 py-3.5 text-sm font-bold text-slate-950 shadow-xl transition hover:-translate-y-0.5 hover:bg-slate-100"
                >
                  Start Building
                  <span className="transition-transform group-hover:translate-x-1">
                    →
                  </span>
                </Link>

                <Link
                  to="/login"
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/15 bg-white/5 px-6 py-3.5 text-sm font-bold text-white backdrop-blur transition hover:bg-white/10"
                >
                  <span>▶</span>
                  Explore Live Demo
                </Link>
              </div>

              {/* Trust points */}
              <div className="mt-9 flex flex-wrap gap-x-6 gap-y-3 text-xs text-slate-400">
                <span className="flex items-center gap-2">
                  <span className="text-emerald-400">✓</span>
                  Policy controlled
                </span>

                <span className="flex items-center gap-2">
                  <span className="text-emerald-400">✓</span>
                  Human approval
                </span>

                <span className="flex items-center gap-2">
                  <span className="text-emerald-400">✓</span>
                  Auditable transactions
                </span>
              </div>
            </div>

            {/* Hero visualization */}
            <div className="relative mx-auto w-full max-w-xl">
              {/* Glow */}
              <div className="absolute inset-10 rounded-full bg-blue-500/20 blur-3xl" />

              <div className="relative rounded-[28px] border border-white/10 bg-white/[0.06] p-3 shadow-2xl backdrop-blur-xl">
                <div className="rounded-[22px] border border-white/10 bg-slate-950/90 p-5 sm:p-6">
                  {/* Window header */}
                  <div className="mb-6 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
                      <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/70" />
                      <span className="h-2.5 w-2.5 rounded-full bg-green-400/70" />
                    </div>

                    <span className="text-[10px] font-semibold tracking-[0.2em] text-slate-500">
                      AGENT TRANSACTION
                    </span>
                  </div>

                  {/* Transaction */}
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-[10px] uppercase tracking-wider text-slate-500">
                          Negotiation
                        </p>

                        <p className="mt-1 text-sm font-bold text-white">
                          MacBook Pro M4
                        </p>
                      </div>

                      <span className="rounded-full bg-blue-400/10 px-3 py-1 text-[10px] font-bold text-blue-300">
                        IN PROGRESS
                      </span>
                    </div>

                    <div className="my-6 h-px bg-white/10" />

                    {/* Buyer */}
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-400/10 text-xl">
                        🤖
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-semibold text-white">
                            AI Buyer
                          </p>
                          <span className="text-xs text-emerald-300">
                            ₹85,000 budget
                          </span>
                        </div>

                        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">
                          <div className="h-full w-[72%] rounded-full bg-gradient-to-r from-emerald-400 to-cyan-400" />
                        </div>
                      </div>
                    </div>

                    {/* Connection */}
                    <div className="relative my-4 ml-5 h-9 border-l border-dashed border-blue-400/40">
                      <span className="absolute -left-1.5 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-blue-400 shadow-lg shadow-blue-400/50" />
                    </div>

                    {/* Merchant */}
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-400/10 text-xl">
                        🏪
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-semibold text-white">
                            Merchant Agent
                          </p>

                          <span className="text-xs text-blue-300">
                            Policy checked
                          </span>
                        </div>

                        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">
                          <div className="h-full w-[88%] rounded-full bg-gradient-to-r from-blue-400 to-indigo-400" />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Status */}
                  <div className="mt-4 grid grid-cols-3 gap-3">
                    <div className="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                      <p className="text-[9px] uppercase text-slate-500">
                        Policy
                      </p>
                      <p className="mt-1 text-xs font-bold text-emerald-300">
                        ✓ Passed
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                      <p className="text-[9px] uppercase text-slate-500">
                        Approval
                      </p>
                      <p className="mt-1 text-xs font-bold text-blue-300">
                        Auto
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                      <p className="text-[9px] uppercase text-slate-500">
                        Audit
                      </p>
                      <p className="mt-1 text-xs font-bold text-purple-300">
                        ✓ Logged
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating badge */}
              <div className="absolute -bottom-5 -left-5 hidden rounded-2xl border border-white/10 bg-slate-900/90 p-4 shadow-xl backdrop-blur sm:block">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-400/10 text-sm">
                    🔐
                  </div>

                  <div>
                    <p className="text-xs font-semibold text-white">
                      Transaction secured
                    </p>
                    <p className="mt-0.5 text-[10px] text-slate-500">
                      Audit hash recorded
                    </p>
                  </div>
                </div>
              </div>

              <div className="absolute -right-4 top-16 hidden rounded-2xl border border-white/10 bg-slate-900/90 p-3 shadow-xl backdrop-blur sm:block">
                <p className="text-[9px] uppercase tracking-wider text-slate-500">
                  AI Status
                </p>

                <p className="mt-1 text-xs font-bold text-emerald-300">
                  ● Agents Online
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          TRUST STRIP
      ========================================================== */}
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto grid max-w-7xl grid-cols-2 divide-x divide-slate-200 sm:grid-cols-4">
          {[
            ['24/7', 'Autonomous operation'],
            ['100%', 'Policy governed'],
            ['3', 'Platform roles'],
            ['∞', 'Audit history'],
          ].map(([value, label]) => (
            <div
              key={label}
              className="px-4 py-7 text-center sm:px-6"
            >
              <p className="text-2xl font-black text-slate-900 sm:text-3xl">
                {value}
              </p>

              <p className="mt-1 text-[10px] font-medium uppercase tracking-wider text-slate-400 sm:text-xs">
                {label}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* =========================================================
          HOW IT WORKS
      ========================================================== */}
      <section
        id="how-it-works"
        className="bg-white py-24"
      >
        <div className="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-600">
              The transaction lifecycle
            </span>

            <h2 className="mt-3 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
              Commerce, from intent to audit.
            </h2>

            <p className="mt-4 text-base leading-7 text-slate-500">
              Every transaction follows a governed path so AI can move fast
              without compromising control.
            </p>
          </div>

          <div className="relative mt-16">
            {/* Connecting line */}
            <div className="absolute left-[12.5%] right-[12.5%] top-10 hidden h-px bg-gradient-to-r from-emerald-200 via-blue-200 to-purple-200 lg:block" />

            <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
              {HOW_IT_WORKS.map((item) => (
                <div
                  key={item.number}
                  className="relative text-center"
                >
                  <div className="relative mx-auto flex h-20 w-20 items-center justify-center rounded-2xl border border-slate-200 bg-white text-3xl shadow-sm">
                    {item.icon}

                    <span className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-slate-900 text-[9px] font-bold text-white">
                      {item.number}
                    </span>
                  </div>

                  <h3 className="mt-6 text-base font-bold text-slate-900">
                    {item.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          FEATURES
      ========================================================== */}
      <section
        id="features"
        className="bg-slate-950 py-24 text-white"
      >
        <div className="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">
          <div className="grid gap-14 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
            <div>
              <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">
                Built for trustworthy autonomy
              </span>

              <h2 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">
                Give AI agents freedom
                <span className="block text-slate-500">
                  without giving up control.
                </span>
              </h2>

              <p className="mt-5 max-w-lg text-sm leading-7 text-slate-400">
                Merchant Agent OS puts governance directly into the commerce
                workflow. Agents can move quickly, while your rules remain
                deterministic and auditable.
              </p>

              <Link
                to="/signup"
                className="mt-8 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-500"
              >
                Build with Merchant Agent OS
                <span>→</span>
              </Link>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              {FEATURES.map((feature) => (
                <div
                  key={feature.title}
                  className="group rounded-2xl border border-white/10 bg-white/[0.04] p-6 transition hover:border-blue-400/30 hover:bg-white/[0.07]"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/[0.07] text-2xl">
                    {feature.icon}
                  </div>

                  <h3 className="mt-5 font-bold text-white">
                    {feature.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================
          ROLES
      ========================================================== */}
      <section
        id="roles"
        className="bg-slate-50 py-24"
      >
        <div className="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-600">
              One platform. Three perspectives.
            </span>

            <h2 className="mt-3 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
              Choose your role.
            </h2>

            <p className="mt-4 text-sm leading-6 text-slate-500">
              Every participant gets the tools they need to operate safely in
              an AI-native commerce environment.
            </p>
          </div>

          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {ROLE_CARDS.map((role) => (
              <div
                key={role.role}
                className={`group relative overflow-hidden rounded-3xl border border-slate-200 bg-white p-7 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${role.accent}`}
              >
                <div className="flex items-start justify-between">
                  <div
                    className={`flex h-14 w-14 items-center justify-center rounded-2xl text-2xl ${role.accentLight}`}
                  >
                    {role.icon}
                  </div>

                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    {role.role}
                  </span>
                </div>

                <h3 className="mt-6 text-xl font-black text-slate-900">
                  {role.title}
                </h3>

                <p className="mt-3 min-h-[72px] text-sm leading-6 text-slate-500">
                  {role.description}
                </p>

                <div className="mt-6 space-y-3">
                  {role.features.map((feature) => (
                    <div
                      key={feature}
                      className="flex items-center gap-3 text-sm text-slate-600"
                    >
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-100 text-[10px] text-emerald-600">
                        ✓
                      </span>

                      {feature}
                    </div>
                  ))}
                </div>

                <Link
                  to={`/signup?role=${role.role}`}
                  className="mt-7 flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-bold text-white transition group-hover:bg-slate-800"
                >
                  Sign Up as {role.title}
                  <span>→</span>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* =========================================================
          FINAL CTA
      ========================================================== */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-700 via-indigo-700 to-slate-900 py-24">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute left-1/4 top-0 h-72 w-72 rounded-full bg-cyan-400 blur-3xl" />
          <div className="absolute bottom-0 right-1/4 h-72 w-72 rounded-full bg-purple-500 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-4xl px-5 text-center sm:px-6">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-white/20 bg-white/10 text-3xl backdrop-blur">
            🚀
          </div>

          <h2 className="mt-7 text-3xl font-black tracking-tight text-white sm:text-5xl">
            Ready for the next generation of commerce?
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-sm leading-7 text-blue-100 sm:text-base">
            Put autonomous AI agents to work while keeping every important
            decision governed, secure, and auditable.
          </p>

          <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
            <Link
              to="/signup"
              className="rounded-xl bg-white px-7 py-3.5 text-sm font-bold text-blue-700 shadow-xl transition hover:bg-blue-50"
            >
              Get Started Free →
            </Link>

            <Link
              to="/login"
              className="rounded-xl border border-white/20 bg-white/10 px-7 py-3.5 text-sm font-bold text-white backdrop-blur transition hover:bg-white/20"
            >
              View Demo
            </Link>
          </div>
        </div>
      </section>

      {/* =========================================================
          FOOTER
      ========================================================== */}
      <footer className="bg-slate-950 text-slate-400">
        <div className="mx-auto max-w-7xl px-5 py-10 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-8 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/10 text-lg">
                🤖
              </div>

              <div>
                <p className="text-sm font-bold text-white">
                  Merchant Agent OS
                </p>

                <p className="text-xs text-slate-500">
                  Governed AI commerce infrastructure
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-6 text-xs">
              <a
                href="#how-it-works"
                className="transition hover:text-white"
              >
                How it works
              </a>

              <a
                href="#features"
                className="transition hover:text-white"
              >
                Features
              </a>

              <a
                href="#roles"
                className="transition hover:text-white"
              >
                Roles
              </a>

              <Link
                to="/login"
                className="transition hover:text-white"
              >
                Login
              </Link>
            </div>
          </div>

          <div className="mt-8 border-t border-white/10 pt-6 text-xs text-slate-600">
            © {new Date().getFullYear()} Merchant Agent OS. AI commerce with
            governance built in.
          </div>
        </div>
      </footer>
    </div>
  )
}