# Merchant Agent OS + AI Buyer Simulator

**AI-to-AI Commerce, Safely Governed**

## Problem Statement

As AI agents begin transacting on behalf of humans, merchants need a secure, governed, and auditable way to let AI buyers and sellers negotiate without uncontrolled financial decisions. Traditional e-commerce APIs were not designed for autonomous agents: there is no budget enforcement, no deterministic policy layer, no human escalation path, and no tamper-evident record of what the agents agreed to.

Merchant Agent OS solves this by treating AI agents as first-class participants in commerce. Every discount request, negotiation outcome, and payment event passes through a deterministic policy engine. High-value deals require human approval. Razorpay test-mode payments provide a real settlement layer, and a hash-chained audit ledger ensures every action is verifiable.

## Key Features

- **Agent-readable product catalog** with versioned catalog entries and structured metadata
- **Deterministic policy engine** — the LLM never decides financial actions; rules are enforced in code
- **AI Merchant Agent** with LLM intent extraction and structured negotiation responses
- **AI Buyer Agent** with a budget firewall that blocks deals exceeding configured limits
- **Human approval queue** for high-value / high-discount transactions
- **Razorpay Test Mode** integration — Orders + Payment Links with real API flows
- **Webhook signature verification & idempotency** — HMAC-SHA256 validation, duplicate-event rejection
- **Hash-chained tamper-evident audit ledger** — every state change is recorded and linked
- **Role-based access control** — buyer, merchant, and admin roles with JWT authentication
- **Buyer trust scoring** — dynamic score based on successful and on-time transactions
- **PDF invoice generation** — automatic invoice creation after payment capture
- **Advanced analytics dashboard** — revenue time series, discount distribution, and success rate charts
- **One-click full demo flow** — trigger the entire AI-to-AI pipeline with a single API call
- **Demo reset** — restore demo data to a clean state with a single endpoint

## Architecture Overview

```mermaid
flowchart LR
    A[AI Buyer Agent] --> B[Discovery\nCatalog]
    B --> C[Negotiation\nOffer / Counter-offer]
    C --> D[Policy Engine\nDeterministic Rules]
    D -->|Within Policy| E[Payment Initiation\nRazorpay Order + Link]
    D -->|High Discount / Value| F[Human Approval\nQueue]
    F -->|Approved| E
    F -->|Rejected| G[Deal Terminated]
    E --> H[Razorpay\nPayment]
    H -->|webhook.captured| I[Webhook Processor\nHMAC + Idempotency]
    I --> J[Order → Paid\nTrust Score Updated\nPDF Invoice Generated]
    J --> K[Audit Ledger\nHash-chained Events]
    G --> K
    C --> K
```

1. The **AI Buyer Agent** discovers products and makes an initial offer.
2. The **Merchant Agent** evaluates the offer against the **deterministic policy engine**.
3. If the discount is within auto-approval limits, an order is created via **Razorpay**.
4. If the discount exceeds limits, the deal enters the **Human Approval Queue**.
5. Once payment is initiated, Razorpay processes it and sends a signed webhook.
6. The **Webhook Processor** verifies the HMAC signature, checks idempotency, updates the order status, refreshes the buyer trust score, and generates a PDF invoice.
7. Every state change is appended to the **Hash-chained Audit Ledger** for tamper-evident compliance.

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL 16 (via Docker) |
| **ORM** | SQLAlchemy 2.0 |
| **Payments** | Razorpay Test Mode (`razorpay` SDK) |
| **AI / LLM** | OpenAI GPT-4o-mini (optional, for merchant intent extraction) |
| **Auth** | JWT HS256 + bcrypt |
| **Rate Limiting** | slowapi |
| **PDF Generation** | ReportLab |
| **Frontend Framework** | React 19 + TypeScript |
| **Build Tool** | Vite |
| **Styling** | Tailwind CSS 4 |
| **Data Fetching** | React Query (TanStack Query v5) |
| **Charts** | Recharts |
| **Notifications** | react-hot-toast |
| **Testing (Backend)** | pytest |
| **DevOps** | Docker + Docker Compose |

## Directory Structure

```
merchant-agent-os/
├── backend/
│   ├── app/
│   │   ├── agents/              # AI Merchant + Buyer agents
│   │   ├── api/                 # 23 FastAPI routers
│   │   ├── audit/               # Hash-chain ledger + hashing utilities
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── payments/            # Razorpay client, payment service, webhook service
│   │   ├── policy/              # Deterministic policy engine
│   │   ├── schemas/             # Pydantic response schemas
│   │   ├── scripts/             # seed_catalog.py (demo data)
│   │   ├── services/            # Business logic (negotiation, approval, trust, invoice, seed)
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Pydantic settings
│   │   └── database.py          # SQLAlchemy engine + session
│   ├── tests/                   # 12 pytest modules (160+ tests)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env / .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, BuyerSimulator, Approvals, Audit, etc.
│   │   ├── components/          # UI primitives, dashboards, layout
│   │   ├── context/             # AuthContext
│   │   ├── api/                 # Axios client + typed API helpers
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   └── architecture.md          # Detailed system design
├── docker-compose.yml
├── README.md
└── LICENSE
```

## Setup Instructions

### Prerequisites

- **Docker** & Docker Compose (for PostgreSQL)
- **Python** 3.11+
- **Node.js** 20+ and npm

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/merchant-agent-os.git
cd merchant-agent-os
```

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

This starts PostgreSQL 16 on port `5435` with:
- User: `merchant`
- Password: `merchant123`
- Database: `merchant_agent_os`

### 3. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # macOS / Linux
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
DATABASE_URL=postgresql://merchant:merchant123@localhost:5435/merchant_agent_os
SECRET_KEY=dev-secret-key-change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Razorpay (Test Mode)
RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# OpenAI (optional)
OPENAI_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4o-mini
```

Initialize the database and seed demo data:

```bash
python -m app.scripts.seed_catalog
```

Start the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API docs are available at `http://localhost:8000/docs`.

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `SECRET_KEY` | Yes | `dev-secret-key-change-me` | JWT signing secret |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token expiry |
| `RAZORPAY_KEY_ID` | No | `""` | Razorpay test key ID |
| `RAZORPAY_KEY_SECRET` | No | `""` | Razorpay test key secret |
| `RAZORPAY_WEBHOOK_SECRET` | No | `""` | Webhook signature secret |
| `OPENAI_API_KEY` | No | `""` | OpenAI API key (optional) |
| `LLM_MODEL` | No | `gpt-4o-mini` | Model for merchant agent |
| `PAYMENT_RETRY_LIMIT` | No | `2` | Payment retry attempts |
| `PAYMENT_RETRY_DELAY_SECONDS` | No | `1` | Delay between retries |

## API Endpoints

| Method | Path | Description | Required Role |
|---|---|---|---|
| `POST` | `/api/v1/auth/signup` | Create a new user | Public |
| `POST` | `/api/v1/auth/login` | Obtain JWT token | Public |
| `GET` | `/api/v1/auth/me` | Get current user | Authenticated |
| `GET` | `/api/v1/catalog/` | Get active product catalog | Authenticated |
| `GET` | `/api/v1/policy/` | Get active pricing policy | Authenticated |
| `POST` | `/api/v1/negotiations/` | Create a negotiation | Authenticated |
| `GET` | `/api/v1/negotiations/` | List negotiations | Authenticated |
| `POST` | `/api/v1/payments/initiate` | Create Razorpay order + link | buyer, merchant, admin |
| `GET` | `/api/v1/payments/orders` | List orders | merchant, admin |
| `GET` | `/api/v1/payments/links` | List payment links | merchant, admin |
| `POST` | `/api/v1/webhooks/` | Process Razorpay webhook | Public (HMAC verified) |
| `POST` | `/api/v1/approvals/` | Create approval request | merchant, admin |
| `POST` | `/api/v1/approvals/{id}/decide` | Approve / reject | merchant, admin |
| `GET` | `/api/v1/approvals/` | List pending approvals | merchant, admin |
| `GET` | `/api/v1/buyers/` | List buyers | Authenticated |
| `GET` | `/api/v1/buyers/{id}/trust-score` | Get buyer trust score | Authenticated |
| `POST` | `/api/v1/simulate/ai-commerce` | Run AI commerce simulation | Authenticated |
| `POST` | `/api/v1/simulate/webhook` | Simulate payment webhook | Authenticated |
| `GET` | `/api/v1/stats` | Platform statistics | Authenticated |
| `GET` | `/api/v1/stats/advanced` | Advanced stats (CSV export) | merchant, admin |
| `GET` | `/api/v1/stats/analytics` | Analytics charts data | Authenticated |
| `GET` | `/api/v1/audit/` | List audit events | Authenticated |
| `GET` | `/api/v1/audit/verify` | Verify audit chain integrity | Authenticated |
| `POST` | `/api/v1/demo/full-flow` | Run full demo pipeline | Authenticated |
| `POST` | `/api/v1/demo/reset` | Reset demo data | admin |
| `GET` | `/api/v1/orders/{order_id}/invoice` | Download PDF invoice | Authenticated |
| `GET` | `/api/v1/health` | Health check | Public |
| `GET` | `/api/v1/trust/` | Trust service endpoints | Authenticated |
| `GET` | `/api/v1/orders` | Invoice / order endpoints | Authenticated |
| `GET` | `/api/v1/currency/` | Currency / exchange rates | Authenticated |
| `GET` | `/api/v1/merchants/` | Merchant endpoints | Authenticated |
| `GET` | `/ws` | WebSocket endpoint | Authenticated |

> Note: Full OpenAPI schema with request/response schemas is available at `/docs` when the backend is running.

## Testing

### Backend

```bash
cd backend
.venv\Scripts\activate   # Windows
source .venv/bin/activate # macOS / Linux
python -m pytest tests/ -q
```

The suite includes **160+ tests** covering:
- AI commerce orchestrator flows (allowed, rejected, approval-required, budget-exceeded)
- Negotiation service logic
- Approval service workflows
- Payment service idempotency
- Webhook signature verification and processing
- Policy engine rules
- Buyer API endpoints
- Audit chain validation
- X402 payment protocol
- Failure simulation service

### Frontend

```bash
cd frontend
npm run build
```

This runs TypeScript type-checking (`tsc -b`) followed by Vite production build. There should be no TypeScript errors.

## Demo Guide

Follow these steps to run the 5-minute demo of the full AI-to-AI commerce flow.

### Step 1 — Create Accounts

Create a buyer and a merchant account via the signup page or API:

```bash
# Buyer
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@demo.com","password":"demo123","full_name":"Demo Buyer","role":"buyer"}'

# Merchant
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"merchant@demo.com","password":"demo123","full_name":"Demo Merchant","role":"merchant"}'
```

Save the returned `access_token` and `token_type`.

### Step 2 — Discover Products

```bash
curl http://localhost:8000/api/v1/catalog/
```

You will see 5 seeded products including `SUB_PRO_001` (Pro Annual Subscription, base price ₹10,000).

### Step 3 — Run the One-Click Full Demo

The fastest way to see the entire pipeline is to use the **"Run Full Demo Flow"** button on the Dashboard (admin/merchant role), or call the API directly:

```bash
curl -X POST http://localhost:8000/api/v1/demo/full-flow \
  -H "Authorization: Bearer <your_access_token>"
```

This endpoint:
1. Loads `BUYER_DEFAULT_001` and `SUB_PRO_001`
2. Runs `AICommerceOrchestrator` with `desired_discount=0.18`
3. Auto-approves the resulting approval via `decide_approval`
4. Creates a Razorpay order + payment link
5. Simulates a `payment.captured` webhook (with valid HMAC signature)
6. Updates the buyer trust score
7. Returns a summary JSON

**Sample response:**

```json
{
  "status": "success",
  "negotiation_id": "neg-xxx",
  "approval_id": "APR-xxx",
  "order_id": "order_xxx",
  "payment_link": "plink_xxx",
  "final_status": "paid",
  "message": "Full demo flow completed successfully"
}
```

### Step 4 — Verify the Audit Trail

```bash
curl http://localhost:8000/api/v1/audit/verify \
  -H "Authorization: Bearer <your_access_token>"
```

The audit chain should return `"valid": true`.

### Step 5 — Explore the Dashboard

Open `http://localhost:5173`, log in, and explore:
- **Stat cards** showing platform metrics
- **Analytics charts** — revenue over time, discount distribution, and success rate
- **Approvals page** — see the auto-approved deal
- **Orders / Payments** — see the paid order and download the PDF invoice

## What Broke & How I Fixed It

### Razorpay `reference_id` Length Limit

**Problem:** When creating Razorpay orders, the `receipt` field was being used as the `reference_id` for payment links. Razorpay enforces a maximum `reference_id` length of 40 characters. Our initial implementation used the full `negotiation_id` (which can exceed 40 chars), causing `payment_link.create()` to fail with a `422 Unprocessable Entity`.

**Fix:** We truncated the receipt to 35 characters when generating it:

```python
receipt = f"rcpt_{negotiation.negotiation_id[:35]}"
```

This ensures the `reference_id` passed to Razorpay stays within the 40-character limit while remaining unique and traceable back to the negotiation.

### Webhook Signature Canonicalization Mismatch

**Problem:** The webhook signature verification was failing intermittently because the canonical JSON used for HMAC computation in the test/demo path did not match Razorpay's exact serialization (whitespace, key ordering).

**Fix:** We standardized on `json.dumps(payload, separators=(",", ":"))` for both signature generation and verification, ensuring byte-for-byte consistency.

## License

MIT — see the [LICENSE](LICENSE) file for details.
