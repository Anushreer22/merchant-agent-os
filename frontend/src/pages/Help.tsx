import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Card, PageHeader } from '../components/ui'

interface Section {
  q: string
  a: string
}

interface Group {
  title: string
  color: string
  sections: Section[]
}

const BUYER_GUIDE: Section[] = [
  {
    q: '1. How do I make a purchase?',
    a: 'Go to Buyer Simulator in the sidebar. Enter your Buyer ID (e.g. BUYER_DEFAULT_001), choose a Product ID from the Catalog, set a quantity and desired discount, then click "Start Purchase". The AI agents will negotiate on your behalf.',
  },
  {
    q: '2. What happens after I submit?',
    a: 'The Merchant Agent evaluates your offer against the active policy. You will see one of three outcomes: ALLOWED (payment initiated), APPROVAL_REQUIRED (a merchant must approve first), or REJECTED (offer too high — a counter-offer is shown).',
  },
  {
    q: '3. Where can I see my orders?',
    a: 'Navigate to Orders in the sidebar. All Razorpay orders created from your negotiations appear here. You can also click "Simulate Webhook" to mark an order as paid for demo purposes.',
  },
  {
    q: '4. What does the discount slider do?',
    a: 'It sets the discount percentage you are requesting (0–30%). The policy engine allows up to 15% automatically. Discounts between 15–20% require human approval. Above 20% will be rejected.',
  },
]

const MERCHANT_GUIDE: Section[] = [
  {
    q: '1. How do I review pending approvals?',
    a: 'Go to Approvals. Any negotiation that exceeded the auto-approval threshold appears here with PENDING status. Click Approve to allow the buyer to proceed to payment, or Reject to decline.',
  },
  {
    q: '2. What is the Audit Ledger?',
    a: 'Every action (negotiation, payment, approval) is recorded in a tamper-evident SHA-256 hash chain. Go to Audit Ledger and click "Verify Chain" to confirm no records have been altered.',
  },
  {
    q: '3. How do I view active policy rules?',
    a: 'Go to Policies. The active policy shows all discount limits, margin floors, and approval thresholds currently in effect.',
  },
  {
    q: '4. Where do I see payment links?',
    a: 'Go to Payments. All Razorpay payment links generated from approved negotiations are listed here with their status and short URLs.',
  },
]

const ADMIN_GUIDE: Section[] = [
  {
    q: '1. What can admins do that merchants cannot?',
    a: 'Admins have access to all pages including Settings. Admins can also create new Buyer records via the API and have full visibility across all negotiations, orders, and audit events.',
  },
  {
    q: '2. How do I reset or change the policy?',
    a: 'Currently policy changes require a database update or API call. The Policies page shows the active policy. To change rules, update the policy record via the admin API or database directly.',
  },
  {
    q: '3. How do I monitor the platform health?',
    a: 'The Dashboard shows real-time stats: total negotiations, pending approvals, revenue, and audit event count. The Platform Overview card shows the status of each system component.',
  },
  {
    q: '4. How do I simulate a full end-to-end demo?',
    a: 'Use the Buyer Simulator to run a transaction. If it results in payment_pending, go to Orders and click "Simulate Webhook" to mark it as paid. Then check the Audit Ledger to see all recorded events.',
  },
]

const GROUPS: Group[] = [
  { title: 'For Buyers', color: 'border-emerald-400 bg-emerald-50', sections: BUYER_GUIDE },
  { title: 'For Merchants', color: 'border-blue-400 bg-blue-50', sections: MERCHANT_GUIDE },
  { title: 'For Admins', color: 'border-purple-400 bg-purple-50', sections: ADMIN_GUIDE },
]

const ROLE_GROUP: Record<string, string> = {
  buyer: 'For Buyers',
  merchant: 'For Merchants',
  admin: 'For Admins',
}

function Accordion({ sections }: { sections: Section[] }) {
  const [open, setOpen] = useState<number | null>(0)
  return (
    <div className="space-y-2">
      {sections.map((s, i) => (
        <div key={i} className="rounded-lg border border-slate-200 bg-white overflow-hidden">
          <button
            onClick={() => setOpen(open === i ? null : i)}
            className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-slate-800 hover:bg-slate-50 transition-colors"
          >
            <span>{s.q}</span>
            <svg
              className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${open === i ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {open === i && (
            <div className="border-t border-slate-100 px-4 py-3 text-sm text-slate-600 leading-relaxed">
              {s.a}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export function Help() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const role = user?.role ?? 'buyer'
  const myGroup = ROLE_GROUP[role]

  return (
    <div>
      <PageHeader title="Help & Guide" subtitle="Step-by-step instructions for each role" />

      {/* Quick-start CTA for current role */}
      <Card className="mb-6 p-5 border-l-4 border-blue-500">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-600 mb-1">Quick Start for {myGroup.replace('For ', '')}</p>
        <p className="text-sm text-slate-700 mb-3">
          {role === 'buyer' && 'Head to the Buyer Simulator to run your first AI-negotiated purchase.'}
          {role === 'merchant' && 'Check the Approvals queue for any pending deals that need your decision.'}
          {role === 'admin' && 'View the Dashboard for a full platform overview, then explore any section.'}
        </p>
        <button
          onClick={() => navigate(role === 'buyer' ? '/buyer-simulator' : role === 'merchant' ? '/approvals' : '/dashboard')}
          className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700 transition-colors"
        >
          {role === 'buyer' ? 'Go to Buyer Simulator →' : role === 'merchant' ? 'Go to Approvals →' : 'Go to Dashboard →'}
        </button>
      </Card>

      <div className="space-y-6">
        {GROUPS.map(g => (
          <div key={g.title}>
            <div className={`mb-3 inline-flex items-center rounded-full border-l-4 px-3 py-1 text-xs font-semibold ${g.color} ${g.title === myGroup ? 'ring-2 ring-offset-1 ring-blue-300' : ''}`}>
              {g.title} {g.title === myGroup && '← Your role'}
            </div>
            <Accordion sections={g.sections} />
          </div>
        ))}
      </div>
    </div>
  )
}
