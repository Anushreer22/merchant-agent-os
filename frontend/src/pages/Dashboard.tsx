import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import BuyerDashboard from '../components/dashboards/BuyerDashboard'
import MerchantDashboard from '../components/dashboards/MerchantDashboard'
import { AdminDashboard } from '../components/dashboards/AdminDashboard'

type UserRole = 'buyer' | 'merchant' | 'admin'

export function Dashboard() {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const role = user.role as UserRole

  switch (role) {
    case 'buyer':
      return <BuyerDashboard />

    case 'merchant':
      return <MerchantDashboard />

    case 'admin':
      return <AdminDashboard />

    default:
      return <Navigate to="/" replace />
  }
}