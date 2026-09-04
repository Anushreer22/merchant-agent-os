import { Link } from "react-router-dom";

type RoleCardProps = {
  role: "buyer" | "merchant" | "admin";
  title: string;
  description: string;
  icon: string;
  accent: string;
};

const RoleCard = ({
  role,
  title,
  description,
  icon,
  accent,
}: RoleCardProps) => {
  return (
    <div
      className={`group rounded-2xl border bg-white p-7 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-xl ${accent}`}
    >
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-xl bg-slate-100 text-3xl">
        {icon}
      </div>

      <h3 className="text-xl font-bold text-slate-900">{title}</h3>

      <p className="mt-3 min-h-[72px] text-sm leading-6 text-slate-600">
        {description}
      </p>

      <Link
        to={`/signup?role=${role}`}
        className="mt-6 inline-flex w-full items-center justify-center rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
      >
        Sign Up as {title}
      </Link>
    </div>
  );
};

const steps = [
  {
    icon: "🤖",
    title: "AI Buyer Discovers",
    description:
      "The buyer agent browses an agent-readable catalog to discover products and suitable offers.",
  },
  {
    icon: "⚙️",
    title: "Policy-Driven Negotiation",
    description:
      "Merchant agents negotiate while deterministic rules enforce limits and approval requirements.",
  },
  {
    icon: "🔐",
    title: "Secure Payment & Audit",
    description:
      "Razorpay payment links, webhook confirmation, and a hash-chained ledger provide secure settlement and auditability.",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900 to-blue-900">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-blue-500 blur-3xl" />
          <div className="absolute -bottom-20 left-20 h-72 w-72 rounded-full bg-cyan-500 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-6 py-20 lg:px-8 lg:py-28">
          <div className="grid items-center gap-14 lg:grid-cols-2">
            <div>
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm text-blue-100 backdrop-blur">
                <span>✦</span>
                Merchant Agent OS
              </div>

              <h1 className="max-w-3xl text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
                AI-to-AI Commerce,
                <span className="block text-blue-300">
                  Safely Governed
                </span>
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
                Enable autonomous AI negotiation without losing control.
                Merchant Agent OS combines intelligent buyer and merchant
                agents with deterministic policy enforcement, human approvals,
                secure payments, and a tamper-proof audit trail.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  to="/signup"
                  className="rounded-xl bg-white px-6 py-3.5 text-center font-semibold text-slate-900 shadow-lg transition hover:bg-slate-100"
                >
                  Get Started
                </Link>

                <Link
                  to="/login"
                  className="rounded-xl border border-white/20 bg-white/10 px-6 py-3.5 text-center font-semibold text-white backdrop-blur transition hover:bg-white/20"
                >
                  Live Demo
                </Link>
              </div>

              <div className="mt-8 flex flex-wrap gap-5 text-sm text-slate-300">
                <span>✓ Deterministic policies</span>
                <span>✓ Human approvals</span>
                <span>✓ Tamper-proof audit</span>
              </div>
            </div>

            {/* SVG visual */}
            <div className="relative mx-auto w-full max-w-xl">
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 shadow-2xl backdrop-blur-xl">
                <div className="rounded-2xl bg-slate-950/80 p-6">
                  <div className="mb-6 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium text-slate-400">
                        AUTONOMOUS COMMERCE
                      </p>
                      <p className="mt-1 text-lg font-bold text-white">
                        Negotiation in progress
                      </p>
                    </div>

                    <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                      LIVE
                    </span>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/20 text-xl">
                        🤖
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-white">
                          AI Buyer
                        </p>
                        <p className="text-xs text-slate-400">
                          Budget: ₹85,000
                        </p>
                      </div>
                      <span className="text-emerald-400">→</span>
                    </div>

                    <div className="mx-auto h-8 w-px bg-blue-400/40" />

                    <div className="flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-500/20 text-xl">
                        🏪
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-white">
                          Merchant Agent
                        </p>
                        <p className="text-xs text-slate-400">
                          Policy checks: passed
                        </p>
                      </div>
                      <span className="text-emerald-400">✓</span>
                    </div>

                    <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-4">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">🔐</span>
                        <div>
                          <p className="text-sm font-semibold text-white">
                            Transaction governed
                          </p>
                          <p className="text-xs text-slate-400">
                            Policy + approval + audit trail verified
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-semibold uppercase tracking-wider text-blue-600">
              Simple by design
            </p>

            <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              How It Works
            </h2>

            <p className="mt-4 text-slate-600">
              Autonomous commerce with controls built into every important
              step.
            </p>
          </div>

          <div className="mt-14 grid gap-8 md:grid-cols-3">
            {steps.map((step, index) => (
              <div
                key={step.title}
                className="relative rounded-2xl border border-slate-200 bg-slate-50 p-7"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white text-3xl shadow-sm">
                  {step.icon}
                </div>

                <div className="mt-6">
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                    Step {index + 1}
                  </span>

                  <h3 className="mt-2 text-xl font-bold text-slate-900">
                    {step.title}
                  </h3>

                  <p className="mt-3 leading-7 text-slate-600">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Role selection */}
      <section className="bg-slate-50 py-20">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center">
            <p className="text-sm font-semibold uppercase tracking-wider text-blue-600">
              Choose your workspace
            </p>

            <h2 className="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">
              Built for Every Side of Commerce
            </h2>

            <p className="mx-auto mt-4 max-w-2xl text-slate-600">
              Start with the role that matches how you participate in
              AI-powered commerce.
            </p>
          </div>

          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            <RoleCard
              role="buyer"
              title="AI Buyer"
              icon="🤖"
              accent="border-emerald-200 hover:border-emerald-400"
              description="Discover products, negotiate within budget, and complete purchases autonomously."
            />

            <RoleCard
              role="merchant"
              title="Merchant Agent"
              icon="🏪"
              accent="border-blue-200 hover:border-blue-400"
              description="Manage catalog, enforce policies, approve high-value deals, and grow revenue."
            />

            <RoleCard
              role="admin"
              title="Admin"
              icon="🛡️"
              accent="border-purple-200 hover:border-purple-400"
              description="Monitor everything, manage users, policies, and audit trail integrity."
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <p>© {new Date().getFullYear()} Merchant Agent OS</p>
          <p>AI commerce with governance built in.</p>
        </div>
      </footer>
    </div>
  );
}