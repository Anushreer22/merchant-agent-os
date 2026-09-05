import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL ?? '/api/v1'

export const api = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Attach token from localStorage on every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('maos_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// Redirect to /login on 401
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401 && !window.location.pathname.startsWith('/login')) {
      localStorage.removeItem('maos_token')
      localStorage.removeItem('maos_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)
export const verifyAuditChain = () => api.get('/audit/verify').then(r => r.data)

export const fetchBuyerTrustScore = (buyerId: string) =>
  api.get(`/buyers/${buyerId}/trust-score`).then(r => r.data)

// ── Types ────────────────────────────────────────────────────────────────────

export interface Stats {
  total_negotiations: number
  allowed_negotiations: number
  rejected_negotiations: number
  pending_approvals: number
  total_orders: number
  paid_orders: number
  revenue_inr: number
  avg_discount_pct: number
  audit_events: number
}

export interface Product {
  product_id: string
  name: string
  description: string
  category: string
  base_price: number
  currency: string
  inventory: number
  margin_floor: number
  discount_rules: Record<string, unknown>
}

export interface CatalogResponse {
  version: string
  products: Product[]
}

export interface Policy {
  version: string
  rules: {
    max_auto_discount: number
    max_human_approved_discount: number
    margin_floor: number
    human_approval_amount: number
    max_quantity_without_approval: number
    max_retry_count: number
  }
  is_active: boolean
  created_at: string
}

export interface Negotiation {
  negotiation_id: string
  buyer_id: string
  product_id: string
  quantity: number
  requested_discount: number
  final_discount: number
  final_amount: number
  decision: string
  status: string
  policy_version: string
  reason_code: string
  requires_human_approval: boolean
  created_at: string
}

export interface Approval {
  approval_id: string
  negotiation_id: string
  buyer_id: string
  product_id: string
  quantity: number
  requested_discount: number
  proposed_discount: number
  final_price: number
  status: string
  policy_version: string
  reason_code: string
  human_user_id: string | null
  approval_reason: string | null
  created_at: string
  decided_at: string | null
}

export interface Order {
  order_id: string
  negotiation_id: string
  amount: number
  currency: string
  receipt: string
  status: string
  created_at: string
}

export interface PaymentLink {
  link_id: string
  order_id: string
  negotiation_id: string
  short_url: string
  status: string
  created_at: string
}

export interface AuditEvent {
  event_id: string
  timestamp: string
  actor: string
  action_type: string
  policy_version: string | null
  negotiation_id: string | null
  razorpay_entity_id: string | null
  payload_hash: string
  previous_hash: string
  hash: string
  created_at: string
}

export interface AuditVerify {
  valid: boolean
  events_checked: number
  first_invalid_event_id: string | null
}

export interface SimulateRequest {
  buyer_id: string
  product_id: string
  quantity: number
  desired_discount: number
}

export interface TranscriptStep {
  step: number
  actor: string
  action: string
  detail: Record<string, unknown>
}

export interface SimulateResult {
  status: string
  negotiation_id: string | null
  final_price: number | null
  currency: string | null
  payment: Record<string, unknown> | null
  transcript: TranscriptStep[]
}

// ── API calls ────────────────────────────────────────────────────────────────

export const fetchStats = () => api.get<Stats>('/stats').then(r => r.data)
export const fetchCatalog = () => api.get<CatalogResponse>('/catalog').then(r => r.data)
export const fetchPolicy = () => api.get<Policy>('/policy/').then(r => r.data)
export const fetchNegotiations = () => api.get<Negotiation[]>('/negotiations/').then(r => r.data)
export const fetchApprovals = () => api.get<Approval[]>('/approvals/').then(r => r.data)
export const fetchOrders = () => api.get<Order[]>('/payments/orders').then(r => r.data)
export const fetchPaymentLinks = () => api.get<PaymentLink[]>('/payments/links').then(r => r.data)
export const fetchAudit = () => api.get<AuditEvent[]>('/audit/').then(r => r.data)
export const fetchAuditVerify = () => api.get<AuditVerify>('/audit/verify').then(r => r.data)

export const decideApproval = (id: string, decision: string) =>
  api.post(`/approvals/${id}/decide`, { decision, human_user_id: 'DASHBOARD_USER' }).then(r => r.data)

export const runSimulation = (body: SimulateRequest) =>
  api.post<SimulateResult>('/simulate/ai-commerce', body).then(r => r.data)

export const simulateWebhook = (order_id: string) =>
  api.post('/simulate/webhook', { order_id }).then(r => r.data)

export const runFullDemo = () =>
  api.post('/demo/full-flow').then(r => r.data)
