"use client"

import {
  AlertTriangle,
  ChevronDown,
  FileText,
  Sparkles,
  User,
} from "lucide-react"
import { useState } from "react"
import type { ChatMessage } from "@/lib/types"
import { cn } from "@/lib/utils"

function SourcesSection({
  sources,
  timing,
}: {
  sources: NonNullable<ChatMessage["sources"]>
  timing?: ChatMessage["timing"]
}) {
  const [open, setOpen] = useState(false)
  if (sources.length === 0) return null

  return (
    <div className="mt-2 border-t border-border/60 pt-2">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center gap-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <FileText className="size-3.5" />
        <span>
          {sources.length} source{sources.length > 1 ? "s" : ""}
        </span>
        <ChevronDown
          className={cn(
            "size-3.5 transition-transform",
            open && "rotate-180",
          )}
        />
      </button>

      {open && (
        <ul className="mt-2 flex flex-col gap-1.5">
          {sources.map((chunk, i) => (
            <li
              key={`${chunk.document}-${chunk.section}-${i}`}
              className="flex items-start justify-between gap-3 rounded-md bg-background/60 px-2.5 py-1.5 text-xs"
            >
              <div className="min-w-0">
                <p className="truncate font-medium text-foreground">
                  {chunk.document}
                </p>
                <p className="truncate text-muted-foreground">
                  {chunk.section}
                </p>
              </div>
              <span className="shrink-0 rounded bg-accent px-1.5 py-0.5 font-mono text-[10px] text-accent-foreground">
                {chunk.score.toFixed(2)}
              </span>
            </li>
          ))}
          {timing && (
            <li className="px-2.5 pt-0.5 text-[10px] text-muted-foreground">
              retrieval {timing.retrieval.toFixed(2)}s · llm{" "}
              {timing.llm_call.toFixed(2)}s
            </li>
          )}
        </ul>
      )}
    </div>
  )
}

export function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user"
  const isError = message.isError

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-2.5">
        <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-primary px-3.5 py-2.5 text-sm leading-relaxed text-primary-foreground">
          {message.content}
        </div>
        <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground">
          <User className="size-4" />
        </span>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-2.5">
      <span
        className={cn(
          "mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full",
          isError
            ? "bg-destructive/15 text-destructive"
            : "bg-primary text-primary-foreground",
        )}
      >
        {isError ? (
          <AlertTriangle className="size-4" />
        ) : (
          <Sparkles className="size-4" />
        )}
      </span>
      <div
        className={cn(
          "max-w-[80%] rounded-2xl rounded-tl-sm border px-3.5 py-2.5 text-sm leading-relaxed",
          isError
            ? "border-destructive/30 bg-destructive/10 text-destructive"
            : "border-border bg-card text-card-foreground",
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isError && message.sources && (
          <SourcesSection sources={message.sources} timing={message.timing} />
        )}
      </div>
    </div>
  )
}

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-2.5">
      <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
        <Sparkles className="size-4" />
      </span>
      <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm border border-border bg-card px-4 py-3">
        <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.3s]" />
        <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.15s]" />
        <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60" />
        <span className="sr-only">HR Assistant is typing</span>
      </div>
    </div>
  )
}
