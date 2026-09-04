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
}: StatCardProps) => {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
          <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
        </div>

        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-xl">
          {icon}
        </div>
      </div>
    </div>
  );
};

const steps = [
  {
    number: "01",
    title: "Discover",
    description: "Browse products from the agent-readable catalog.",
  },
  {
    number: "02",
    title: "Negotiate",
    description: "Let your AI agent negotiate within your approved budget.",
  },
  {
    number: "03",
    title: "Purchase",
    description: "Review the final deal and complete secure payment.",
  },
];

export default function BuyerDashboard() {
  return (
    <div className="space-y-8">
      {/* Welcome */}
      <section className="overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 p-7 text-white shadow-lg">
        <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold">
              AI BUYER
            </span>

            <h1 className="mt-4 text-2xl font-bold sm:text-3xl">
              Here&apos;s how to make a purchase
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-emerald-50">
              Your AI agent can discover products, negotiate within your
              budget, and help complete purchases while your policies keep
              transactions under control.
            </p>

            <Link
              to="/buyer-simulator"
              className="mt-6 inline-flex items-center rounded-xl bg-white px-5 py-3 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-50"
            >
              Open Buyer Simulator →
            </Link>
          </div>

          <div className="hidden text-7xl lg:block">🤖</div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {steps.map((step) => (
            <div
              key={step.number}
              className="rounded-xl border border-white/10 bg-white/10 p-4 backdrop-blur"
            >
              <span className="text-xs font-bold text-emerald-100">
                {step.number}
              </span>

              <h3 className="mt-2 font-semibold">{step.title}</h3>

              <p className="mt-1 text-xs leading-5 text-emerald-50">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="grid gap-5 sm:grid-cols-2">
        <StatCard
          title="Budget"
          value="₹85,000"
          subtitle="Max single transaction: ₹85,000"
          icon="💰"
        />

        <StatCard
          title="Trust Score"
          value="—"
          subtitle="Trust score will appear when available"
          icon="🛡️"
        />
      </section>

      {/* Purchases */}
      <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-6 py-5">
          <h2 className="font-bold text-slate-900">Recent Purchases</h2>
          <p className="mt-1 text-sm text-slate-500">
            Your latest completed transactions.
          </p>
        </div>

        <div className="flex min-h-[220px] flex-col items-center justify-center px-6 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-2xl">
            🛍️
          </div>

          <h3 className="mt-4 font-semibold text-slate-900">
            No recent purchases.
          </h3>

          <p className="mt-1 max-w-md text-sm text-slate-500">
            Start a transaction through the Buyer Simulator and your completed
            purchases will appear here.
          </p>
        </div>
      </section>
    </div>
  );
}