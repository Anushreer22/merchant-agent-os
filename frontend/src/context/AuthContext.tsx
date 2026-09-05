import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { toast } from 'react-hot-toast'
import { api } from '../api/client'

export interface AuthUser {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'merchant' | 'buyer'
  merchant_id: string | null
}

interface AuthState {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, full_name: string, role: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

const TOKEN_KEY = 'maos_token'
const USER_KEY = 'maos_user'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<AuthUser | null>(() => {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  })

  const _persist = (u: AuthUser, t: string) => {
    localStorage.setItem(TOKEN_KEY, t)
    localStorage.setItem(USER_KEY, JSON.stringify(u))
    setToken(t)
    setUser(u)
  }

  const login = useCallback(async (email: string, password: string) => {
    try {
      const { data } = await api.post('/auth/login', { email, password })
      _persist(data, data.access_token)
      toast.success('Logged in successfully')
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Unable to login.'
      toast.error(message)
      throw new Error(message)
    }
  }, [])

  const signup = useCallback(async (email: string, password: string, full_name: string, role: string) => {
    try {
      const { data } = await api.post('/auth/signup', { email, password, full_name, role })
      _persist(data, data.access_token)
      toast.success('Account created successfully')
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Unable to create your account.'
      toast.error(message)
      throw new Error(message)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
