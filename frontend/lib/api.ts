import type { AskResponse, LoginResponse } from "./types"

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000"

/** Thrown when the API responds with a non-OK status. */
export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

/** Thrown specifically when the token is missing/expired (HTTP 403). */
export class AuthExpiredError extends ApiError {
  constructor(message = "Not authenticated") {
    super(message, 403)
    this.name = "AuthExpiredError"
  }
}

async function parseDetail(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json()
    if (data && typeof data.detail === "string") return data.detail
  } catch {
    // ignore JSON parse errors
  }
  return fallback
}

export async function login(
  employeeId: string,
  password: string,
): Promise<LoginResponse> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ employee_id: employeeId, password }),
    })
  } catch {
    throw new ApiError(
      "Unable to reach the server. Please check your connection and try again.",
      0,
    )
  }

  if (!res.ok) {
    const detail = await parseDetail(
      res,
      res.status === 401 ? "Invalid employee ID or password." : "Login failed.",
    )
    throw new ApiError(detail, res.status)
  }

  return (await res.json()) as LoginResponse
}

export async function askQuestion(
  question: string,
  token: string,
): Promise<AskResponse> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}/chat/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ question }),
    })
  } catch {
    throw new ApiError(
      "Unable to reach the server. Please try again.",
      0,
    )
  }

  if (res.status === 403) {
    throw new AuthExpiredError(await parseDetail(res, "Not authenticated"))
  }

  if (!res.ok) {
    const detail = await parseDetail(
      res,
      "Something went wrong while generating an answer.",
    )
    throw new ApiError(detail, res.status)
  }

  return (await res.json()) as AskResponse
}
