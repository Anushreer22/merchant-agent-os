import { Link } from "react-router-dom";

type StatCardProps = {
  title: string;
  value: string;
  subtitle: string;
  icon: string;
};

const StatCard = ({
  title,
  value,
  subtitle,
  icon,
}: StatCardProps) => (
  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
        <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
      </div>

      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-xl">
        {icon}
      </div>
    </div>
  </div>
);

const steps = [
  {
    number: "01",
    title: "Review",
    description: "See incoming AI negotiations and proposed deals.",
  },
  {
    number: "02",
    title: "Approve",
    description: "Human approval is required when policies demand it.",
  },
  {
    number: "03",
    title: "Settle",
    description: "Complete payment and record the transaction securely.",
  },
];

export default function MerchantDashboard() {
  return (
    <div className="space-y-8">
      {/* Welcome */}
      <section className="overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 p-7 text-white shadow-lg">
        <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold">
              MERCHANT AGENT
            </span>

            <h1 className="mt-4 text-2xl font-bold sm:text-3xl">
              Manage negotiations, approvals, and payments
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-blue-50">
              Keep your merchant agent autonomous while maintaining control
              over pricing, approval thresholds, and transaction settlement.
            </p>

            <Link
              to="/approvals"
              className="mt-6 inline-flex items-center rounded-xl bg-white px-5 py-3 text-sm font-semibold text-blue-700 transition hover:bg-blue-50"
            >
              Review Approvals →
            </Link>
          </div>

          <div className="hidden text-7xl lg:block">🏪</div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {steps.map((step) => (
            <div
              key={step.number}
              className="rounded-xl border border-white/10 bg-white/10 p-4 backdrop-blur"
            >
              <span className="text-xs font-bold text-blue-100">
                {step.number}
              </span>

              <h3 className="mt-2 font-semibold">{step.title}</h3>

              <p className="mt-1 text-xs leading-5 text-blue-50">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="grid gap-5 md:grid-cols-3">
        <StatCard
          title="Revenue"
          value="₹0"
          subtitle="Revenue generated"
          icon="💰"
        />

        <StatCard
          title="Pending Approvals"
          value="0"
          subtitle="Deals waiting for approval"
          icon="⏳"
        />

        <StatCard
          title="Margin Protected"
          value="₹0"
          subtitle="Value protected by policies"
          icon="🛡️"
        />
      </section>

      {/* Negotiations */}
      <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-3 border-b border-slate-100 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-bold text-slate-900">
              Recent Negotiations
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Monitor AI-to-AI deals and their current status.
            </p>
          </div>

          <Link
            to="/approvals"
            className="text-sm font-semibold text-blue-600 hover:text-blue-700"
          >
            View approvals →
          </Link>
        </div>

        <div className="flex min-h-[220px] flex-col items-center justify-center px-6 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 text-2xl">
            🤝
          </div>

          <h3 className="mt-4 font-semibold text-slate-900">
            No recent negotiations
          </h3>

          <p className="mt-1 max-w-md text-sm text-slate-500">
            Incoming buyer-agent negotiations will appear here.
          </p>
        </div>
      </section>
    </div>
  );
}