import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'

import { Home } from './pages/Home'
import { Login } from './pages/Login'
import Signup from './pages/Signup'
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
import { Help } from './pages/Help'

const qc = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* ============================================
                PUBLIC ROUTES
            ============================================ */}

            <Route path="/" element={<Home />} />

            <Route path="/login" element={<Login />} />

            <Route path="/signup" element={<Signup />} />

            {/* ============================================
                AUTHENTICATED ROUTES
            ============================================ */}

            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>

                {/* --------------------------------------------
                    ALL AUTHENTICATED ROLES
                -------------------------------------------- */}

                {/* Dashboard decides which dashboard to show:
                    buyer     -> BuyerDashboard
                    merchant  -> MerchantDashboard
                    admin     -> AdminDashboard
                */}
                <Route
                  path="/dashboard"
                  element={<Dashboard />}
                />

                <Route
                  path="/catalog"
                  element={<Catalog />}
                />

                <Route
                  path="/orders"
                  element={<Orders />}
                />

                <Route
                  path="/help"
                  element={<Help />}
                />

                {/* --------------------------------------------
                    BUYER + ADMIN
                -------------------------------------------- */}

                <Route
                  element={
                    <ProtectedRoute
                      allowedRoles={['buyer', 'admin']}
                    />
                  }
                >
                  <Route
                    path="/buyer-simulator"
                    element={<BuyerSimulator />}
                  />
                </Route>

                {/* --------------------------------------------
                    MERCHANT + ADMIN
                -------------------------------------------- */}

                <Route
                  element={
                    <ProtectedRoute
                      allowedRoles={['merchant', 'admin']}
                    />
                  }
                >
                  <Route
                    path="/negotiations"
                    element={<Negotiations />}
                  />

                  <Route
                    path="/approvals"
                    element={<Approvals />}
                  />

                  <Route
                    path="/payments"
                    element={<Payments />}
                  />

                  <Route
                    path="/audit"
                    element={<Audit />}
                  />

                  <Route
                    path="/policies"
                    element={<Policies />}
                  />
                </Route>

                {/* --------------------------------------------
                    ADMIN ONLY
                -------------------------------------------- */}

                <Route
                  element={
                    <ProtectedRoute
                      allowedRoles={['admin']}
                    />
                  }
                >
                  <Route
                    path="/settings"
                    element={<Settings />}
                  />
                </Route>

              </Route>
            </Route>

            {/* ============================================
                FALLBACK
            ============================================ */}

            <Route
              path="*"
              element={<Navigate to="/" replace />}
            />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}