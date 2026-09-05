import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { runFullDemo } from '../api/client'
import BuyerDashboard from '../components/dashboards/BuyerDashboard'
import MerchantDashboard from '../components/dashboards/MerchantDashboard'
import { AdminDashboard } from '../components/dashboards/AdminDashboard'

type UserRole = 'buyer' | 'merchant' | 'admin'

export function Dashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const queryClient = useQueryClient()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const handleRunFullDemo = async () => {
    setLoading(true)
    try {
      await runFullDemo()
      toast.success('Full demo flow completed successfully')
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Demo flow failed')
    } finally {
      setLoading(false)
    }
  }

  const role = user.role as UserRole

  let content
  switch (role) {
    case 'buyer':
      content = <BuyerDashboard />
      break
    case 'merchant':
      content = <MerchantDashboard />
      break
    case 'admin':
      content = <AdminDashboard />
      break
    default:
      content = <Navigate to="/" replace />
  }

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <button
          type="button"
          onClick={handleRunFullDemo}
          disabled={loading}
          className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Running Demo Flow...' : 'Run Full Demo Flow'}
        </button>
      </div>
      {content}
    </div>
  )
}