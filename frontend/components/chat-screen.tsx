"use client"

import { LogOut, SendHorizontal, ShieldCheck, Sparkles } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { useAuth } from "@/components/auth-context"
import {
  ChatMessageBubble,
  TypingIndicator,
} from "@/components/chat-message-bubble"
import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { askQuestion, AuthExpiredError } from "@/lib/api"
import type { ChatMessage } from "@/lib/types"

const SUGGESTIONS = [
  "How many paid leave days do I get per year?",
  "What does the health insurance plan cover?",
  "How do I request parental leave?",
]

function createId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function ChatScreen() {
  const { user, token, signOut } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [messages, loading])

  async function send(question: string) {
    const trimmed = question.trim()
    if (!trimmed || loading || !token) return

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: trimmed,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const res = await askQuestion(trimmed, token)
      const looksLikeError = /^(error|sorry, an error|an error occurred)/i.test(
        res.answer.trim(),
      )
      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: "assistant",
          content: res.answer,
          isError: looksLikeError,
          sources: res.chunks_retrieved,
          timing: res.timing,
        },
      ])
    } catch (err) {
      if (err instanceof AuthExpiredError) {
        // Token expired/invalid -> back to login.
        signOut()
        return
      }
      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: "assistant",
          isError: true,
          content:
            err instanceof Error
              ? err.message
              : "Something went wrong. Please try again.",
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      void send(input)
    }
  }

  return (
    <div className="flex h-dvh flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between gap-3 border-b border-border bg-background/95 px-4 py-3 backdrop-blur">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="size-5" />
          </span>
          <div className="min-w-0">
            <h1 className="truncate text-sm font-semibold leading-tight text-foreground">
              HR Assistant
            </h1>
            <p className="truncate text-xs leading-tight text-muted-foreground">
              Policies, leave &amp; benefits
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden items-center gap-2 sm:flex">
            {user?.role === "admin" && (
              <span className="rounded-full bg-primary/15 px-2 py-0.5 text-xs font-medium text-primary">
                Admin
              </span>
            )}
            <div className="text-right">
              <p className="text-sm font-medium leading-tight text-foreground">
                {user?.name}
              </p>
              <p className="text-xs leading-tight text-muted-foreground">
                {user?.employeeId}
              </p>
            </div>
          </div>
          <ThemeToggle />
          <Button
            variant="ghost"
            size="icon"
            onClick={signOut}
            aria-label="Sign out"
            title="Sign out"
          >
            <LogOut className="size-5" />
          </Button>
        </div>
      </header>

      {/* Mobile identity row */}
      <div className="flex items-center gap-2 border-b border-border px-4 py-2 sm:hidden">
        {user?.role === "admin" && (
          <span className="rounded-full bg-primary/15 px-2 py-0.5 text-xs font-medium text-primary">
            Admin
          </span>
        )}
        <p className="text-xs text-muted-foreground">
          Signed in as{" "}
          <span className="font-medium text-foreground">{user?.name}</span> ·{" "}
          {user?.employeeId}
        </p>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-2xl flex-col gap-4 px-4 py-6">
          {messages.length === 0 && !loading ? (
            <div className="flex flex-col items-center py-10 text-center">
              <span className="mb-4 flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Sparkles className="size-6" />
              </span>
              <h2 className="text-balance text-lg font-semibold text-foreground">
                Hi {user?.name?.split(" ")[0]}, how can I help?
              </h2>
              <p className="mt-1 max-w-sm text-pretty text-sm leading-relaxed text-muted-foreground">
                Ask anything about HR policies. Answers are backed by your
                company&apos;s official policy documents.
              </p>
              <div className="mt-6 flex w-full max-w-md flex-col gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => void send(s)}
                    className="rounded-lg border border-border bg-card px-3.5 py-2.5 text-left text-sm text-card-foreground transition-colors hover:border-ring hover:bg-accent"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((m) => (
                <ChatMessageBubble key={m.id} message={m} />
              ))}
              {loading && <TypingIndicator />}
            </>
          )}
        </div>
      </div>

      {/* Composer */}
      <div className="border-t border-border bg-background px-4 py-3">
        <div className="mx-auto w-full max-w-2xl">
          <div className="flex items-end gap-2 rounded-2xl border border-input bg-card p-2 focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/30">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder="Ask about leave, benefits, policies…"
              className="max-h-32 min-h-9 flex-1 resize-none bg-transparent px-2 py-1.5 text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground"
            />
            <Button
              size="icon"
              onClick={() => void send(input)}
              disabled={loading || !input.trim()}
              aria-label="Send message"
              className="size-9 shrink-0 rounded-xl"
            >
              <SendHorizontal className="size-4" />
            </Button>
          </div>
          <p className="mt-1.5 px-1 text-center text-[11px] text-muted-foreground">
            Press Enter to send · Shift+Enter for a new line
          </p>
        </div>
      </div>
    </div>
  )
}
