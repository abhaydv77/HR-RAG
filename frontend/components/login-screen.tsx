"use client"

import { AlertCircle, Loader2, Lock, ShieldCheck } from "lucide-react"
import { useState } from "react"
import { useAuth } from "@/components/auth-context"
import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { login } from "@/lib/api"

export function LoginScreen() {
  const { signIn } = useAuth()
  const [employeeId, setEmployeeId] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!employeeId.trim() || !password) return
    setError(null)
    setLoading(true)
    try {
      const res = await login(employeeId.trim(), password)
      signIn(res)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Login failed. Please try again.",
      )
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col bg-background">
      <header className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="size-5" />
          </span>
          <span className="text-sm font-semibold text-foreground">
            HR Assistant
          </span>
        </div>
        <ThemeToggle />
      </header>

      <div className="flex flex-1 items-center justify-center px-4 py-8">
        <div className="w-full max-w-sm">
          <div className="mb-8 text-center">
            <span className="mx-auto mb-4 flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
              <ShieldCheck className="size-7" />
            </span>
            <h1 className="text-balance text-2xl font-semibold tracking-tight text-foreground">
              Sign in to HR Assistant
            </h1>
            <p className="mt-2 text-pretty text-sm leading-relaxed text-muted-foreground">
              Ask questions about company HR policies, leave, and benefits.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="rounded-xl border border-border bg-card p-6 shadow-sm"
            noValidate
          >
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label
                  htmlFor="employee_id"
                  className="text-sm font-medium text-foreground"
                >
                  Employee ID
                </label>
                <input
                  id="employee_id"
                  name="employee_id"
                  type="text"
                  autoComplete="username"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  disabled={loading}
                  placeholder="e.g. EMP-1024"
                  className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40 disabled:opacity-60"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label
                  htmlFor="password"
                  className="text-sm font-medium text-foreground"
                >
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  placeholder="Enter your password"
                  className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/40 disabled:opacity-60"
                />
              </div>

              {error && (
                <div
                  role="alert"
                  className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
                >
                  <AlertCircle className="mt-0.5 size-4 shrink-0" />
                  <span className="leading-relaxed">{error}</span>
                </div>
              )}

              <Button
                type="submit"
                disabled={loading || !employeeId.trim() || !password}
                className="mt-1 w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    <Lock className="size-4" />
                    Sign in
                  </>
                )}
              </Button>
            </div>
          </form>

          <p className="mt-6 text-center text-xs leading-relaxed text-muted-foreground">
            Internal use only. Your session is held in memory and ends when you
            close or refresh this tab.
          </p>
        </div>
      </div>
    </main>
  )
}
