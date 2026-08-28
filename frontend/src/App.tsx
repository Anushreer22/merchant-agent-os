import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Catalog } from './pages/Catalog'
import { BuyerSimulator } from './pages/BuyerSimulator'
import { Negotiations } from './pages/Negotiations'
import { Approvals } from './pages/Approvals'
import { Orders } from './pages/Orders'
import { Payments } from './pages/Payments'
import { Audit } from './pages/Audit'
import { Policies } from './pages/Policies'
import { Settings } from './pages/Settings'

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
})

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="catalog" element={<Catalog />} />
            <Route path="buyer-simulator" element={<BuyerSimulator />} />
            <Route path="negotiations" element={<Negotiations />} />
            <Route path="approvals" element={<Approvals />} />
            <Route path="orders" element={<Orders />} />
            <Route path="payments" element={<Payments />} />
            <Route path="audit" element={<Audit />} />
            <Route path="policies" element={<Policies />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
