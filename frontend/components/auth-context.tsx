"use client"

import { createContext, useContext, useMemo, useState } from "react"
import type { AuthUser, LoginResponse } from "@/lib/types"

interface AuthState {
  token: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  signIn: (data: LoginResponse) => void
  signOut: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<AuthUser | null>(null)

  const signIn = (data: LoginResponse) => {
    setToken(data.access_token)
    setUser({
      employeeId: data.employee_id,
      name: data.name,
      role: data.role,
    })
  }

  const signOut = () => {
    setToken(null)
    setUser(null)
  }

  const value = useMemo<AuthState>(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      signIn,
      signOut,
    }),
    [token, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return ctx
}
