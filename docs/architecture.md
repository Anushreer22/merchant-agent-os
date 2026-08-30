# Architecture

## System Architecture

Merchant Agent OS is a three-tier application:

```
┌─────────────────────────────────────────────────────────┐
│  React Frontend (Vite + TypeScript)                      │
│  React Query for server state, Tailwind CSS for UI       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST /api/v1
┌────────────────────▼────────────────────────────────────┐
│  FastAPI Backend                                         │
│  ├── Auth (JWT + bcrypt)                                 │
│  ├── Policy Engine (deterministic rules)                 │
│  ├── AI Agents (OpenAI GPT-4o-mini)                      │
│  ├── Payment Service (Razorpay)                          │
│  ├── Webhook Handler (HMAC-verified)                     │
│  └── Audit Ledger (SHA-256 hash chain)                   │
└────────────────────┬────────────────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼────────────────────────────────────┐
│  PostgreSQL 16                                           │
│  Tables: users, products, catalog_versions, policies,   │
│  negotiations, orders, payment_links, webhook_events,   │
│  approvals, audit_events, buyers                        │
└─────────────────────────────────────────────────────────┘
```

---

## Agent Architecture

### Buyer Agent (`app/agents/buyer_agent.py`)
- Initialized with a `Buyer` DB record (budget, strategy, preferred categories)
- `make_offer(product, desired_discount)` — constructs a natural-language offer message and structured offer dict
- `check_budget(final_price)` — validates the final price against the buyer's budget
- `initiate_payment(negotiation_id, db)` — calls the payment service to create a Razorpay order

### Merchant Agent (`app/agents/merchant_agent.py`)
- Stateless; receives a buyer message and DB session
- Calls OpenAI to parse the buyer's intent (product, quantity, discount)
- Passes parsed intent to the Policy Engine
- Returns a structured response with decision, reason code, and counter-offer if applicable

### Orchestrator (`app/services/ai_commerce_service.py`)
Coordinates the full transaction loop:
1. Buyer Agent makes offer
2. Merchant Agent evaluates via Policy Engine
3. If REJECTED → return with counter-offer
4. If APPROVAL_REQUIRED → create Approval record, return pending
5. If ALLOWED → budget check → initiate payment

---

## Deterministic Policy Engine (`app/policy/engine.py`)

All decisions are rule-based, not AI-based. The active policy (stored in DB) defines:

| Rule | Description |
|---|---|
| `max_auto_discount` | Max discount auto-approved (default 15%) |
| `max_human_approved_discount` | Max discount with human approval (default 20%) |
| `margin_floor` | Minimum margin after discount (default 30%) |
| `human_approval_amount` | Transaction amount requiring approval (default ₹5,000) |
| `max_quantity_without_approval` | Max units without approval (default 20) |
| `max_retry_count` | Max negotiation retries (default 2) |

Decision flow: `ALLOWED` → `APPROVAL_REQUIRED` → `REJECTED`

---

## Payment Flow

```
POST /simulate/ai-commerce
        │
        ▼
  Policy: ALLOWED
        │
        ▼
  create_order_and_link()
        │
        ├── Razorpay order.create (amount in paise)
        ├── Razorpay payment_link.create (reference_id ≤ 40 chars)
        ├── Persist Order + PaymentLink to DB
        └── Append ORDER_CREATED audit event
```

Idempotency: if an Order already exists for a negotiation_id, the existing order+link is returned without calling Razorpay again.

---

## Webhook Processing (`app/payments/webhook_service.py`)

1. Receive raw body + `X-Razorpay-Signature` header
2. HMAC-SHA256 verify against `RAZORPAY_WEBHOOK_SECRET`
3. Idempotency check on `event_id`
4. Persist `WebhookEvent` record
5. Map event type → Order status (`payment.captured` → `paid`, `payment.failed` → `failed`)
6. Append audit event

For demo/testing, `POST /api/v1/simulate/webhook` bypasses signature verification and directly marks an order as paid.

---

## Audit Ledger (`app/audit/ledger.py`)

Every significant action appends an `AuditEvent` with:
- `payload_hash` — SHA-256 of the event payload
- `previous_hash` — hash of the preceding event (genesis = `"0" * 64`)
- `hash` — SHA-256 of `(previous_hash + payload_hash)`

This forms a hash chain. `GET /api/v1/audit/verify` walks the chain and confirms no event has been tampered with.

---

## Security Architecture

| Layer | Mechanism |
|---|---|
| Authentication | JWT (HS256), 60-minute expiry, bcrypt password hashing |
| Authorization | Role-based (`admin`, `merchant`, `buyer`) via `require_role()` |
| Rate Limiting | slowapi: 100/min global, 20/min payments, 10/min webhooks |
| Security Headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy: default-src 'self'` |
| CORS | Restricted to `localhost:5173` and `127.0.0.1:5173` |
| Webhook Integrity | HMAC-SHA256 signature verification |
| Audit Integrity | SHA-256 hash chain, verifiable via API |
| Secrets | All credentials via environment variables, never committed |
