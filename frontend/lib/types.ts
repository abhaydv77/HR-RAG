export type Role = "admin" | "employee"

export interface LoginResponse {
  access_token: string
  token_type: "bearer"
  employee_id: string
  name: string
  role: Role
}

export interface AuthUser {
  employeeId: string
  name: string
  role: Role
}

export interface RetrievedChunk {
  document: string
  section: string
  score: number
}

export interface ChatTiming {
  retrieval: number
  llm_call: number
}

export interface AskResponse {
  answer: string
  chunks_retrieved: RetrievedChunk[]
  timing: ChatTiming
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  /** Marks an assistant message as an error bubble. */
  isError?: boolean
  sources?: RetrievedChunk[]
  timing?: ChatTiming
}
