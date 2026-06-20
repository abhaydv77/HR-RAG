"use client"

import { AuthProvider, useAuth } from "@/components/auth-context"
import { ChatScreen } from "@/components/chat-screen"
import { LoginScreen } from "@/components/login-screen"

function AppShell() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <ChatScreen /> : <LoginScreen />
}

export default function Page() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  )
}
