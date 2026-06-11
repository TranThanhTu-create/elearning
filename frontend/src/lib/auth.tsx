'use client'

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react'
import { api, setTokens, clearTokens } from './api'
import type { User, LoginResponse } from '@/types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (identifier: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  isAdmin: boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = useCallback(async () => {
    try {
      const { data } = await api.get<User>('/auth/me')
      setUser(data)
    } catch {
      setUser(null)
    }
  }, [])

  useEffect(() => {
    fetchMe().finally(() => setLoading(false))
  }, [fetchMe])

  const login = async (identifier: string, password: string) => {
    const { data } = await api.post<LoginResponse>('/auth/login', {
      login: identifier,
      password,
    })
    setTokens(data.access_token, data.refresh_token)
    setUser(data.user)
  }

  const logout = () => {
    clearTokens()
    setUser(null)
    window.location.href = '/login'
  }

  const refreshUser = async () => {
    await fetchMe()
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
