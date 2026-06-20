# Runbook — HR Policy RAG Bot

## Prerequisites

- Python 3.10+
- Network access to `pypi.org` and `openrouter.ai`

---

## 1. Install Dependencies

Create a virtual environment and install all packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### If installation fails

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `chromadb` fails to build | Missing Rust compiler (`cargo`) | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` then retry |
| `cryptography` build error | Missing OpenSSL headers | `brew install openssl` (macOS) or `apt install libssl-dev` (Linux) |
| DNS errors / `nodename nor servname provided` | Network/DNS issue | Try `pip install --index-url https://pypi.org/simple/` or switch DNS to `8.8.8.8` |
| Timeout downloading large packages | Slow connection | Use `pip install --timeout 120 -r requirements.txt` |

After any fix, verify with:

```bash
python3 -c "
import fastapi, sqlalchemy, jwt, dotenv, httpx, chromadb, openai
print('All dependencies loaded successfully')
"
```

---

## 2. Seed the Database

### One-time setup

1. Ensure `.env` exists with required values (copy from `.env.example`):

```bash
cp .env.example .env
```

2. Generate a JWT secret:

```bash
openssl rand -hex 32
```

Paste the output into `JWT_SECRET` in `.env`.

3. Add your Groq API key to `.env`:

```
GROQ_API_KEY=gsk_your-groq-api-key-here
```

### Run the seed script

```bash
source .venv/bin/activate
python seed.py
```

### What the seed script does

| Step | Action | Output |
|------|--------|--------|
| 1 | Drops and recreates all SQLite tables | `hr_rag.db` created/overwritten |
| 2 | Inserts 1 admin + 14 dummy employees | All passwords hashed with bcrypt |
| 3 | Reads all `.md` files from `policies/` | Chunks by heading/section |
| 4 | Generates embeddings via OpenRouter API | ~30–60 embeddings API call |
| 5 | Indexes chunks + embeddings into ChromaDB | `chroma_db/` directory created |

### Expected output

```
2025-01-01 12:00:00 [seed] INFO: Dropping and recreating all tables...
2025-01-01 12:00:00 [seed] INFO: Seeded 15 employees (1 admin + 14 regular)
2025-01-01 12:00:00 [seed] INFO: Chunking policy documents from './policies'...
2025-01-01 12:00:00 [seed] INFO: Generated 34 chunks
2025-01-01 12:00:00 [seed] INFO: Generating embeddings for 34 chunks...
2025-01-01 12:00:00 [seed] INFO: Generated 34 embeddings
2025-01-01 12:00:00 [seed] INFO: Indexing into ChromaDB...
2025-01-01 12:00:00 [seed] INFO: Seeding complete!
```

### If seed fails

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named '...'` | Dependencies not installed — run `pip install -r requirements.txt` |
| `OpenAIError: 401` | Invalid `GROQ_API_KEY` in `.env` |
| `FileNotFoundError: ./policies` | Run from project root (`/Volumes/mac/HR-RAG`) |
| `sqlalchemy.exc.OperationalError` | Delete `hr_rag.db` and retry |

Safe to re-run: `python seed.py` drops all tables and re-indexes ChromaDB every time.

---

## 3. Start the FastAPI Server

```bash
source .venv/bin/activate
uvicorn hr_rag.main:app --reload --host 0.0.0.0 --port 8000
```

| Flag | Purpose |
|------|---------|
| `--reload` | Auto-restart on file changes (development) |
| `--host 0.0.0.0` | Listen on all network interfaces |
| `--port 8000` | Port (change if 8000 is in use) |

### Verify server started

Open [http://localhost:8000/docs](http://localhost:8000/docs) — you should see the Swagger UI with three tag groups: `auth`, `chat`, `admin`.

Or via CLI:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## 4. Verify Authentication

### 4a. Login as an employee

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "EMP001", "password": "pass123"}' | python3 -m json.tool
```

**Expected response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "employee_id": "EMP001",
  "name": "Alice Johnson",
  "role": "employee"
}
```

**Save the token** for subsequent requests:

```bash
TOKEN="<paste-access_token-value>"
```

### 4b. Verify identity comes from the token, not from request body

```bash
curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected response** — returns Alice's data (EMP001), regardless of token content:

```json
{
  "employee_id": "EMP001",
  "name": "Alice Johnson",
  "department": "Engineering",
  "leave_balance_sick": 8.0,
  ...
}
```

### 4c. Verify bad credentials are rejected

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "EMP001", "password": "wrong"}' | python3 -m json.tool
```

**Expected:** `401 Unauthorized` with `"detail": "Invalid employee ID or password"`

### 4d. Verify expired/invalid token is rejected

```bash
curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer invalid-token" | python3 -m json.tool
```

**Expected:** `401 Unauthorized` with `"detail": "Invalid or expired token"`

### 4e. Verify admin endpoints reject non-admin tokens

```bash
curl -s http://localhost:8000/admin/employees \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Expected:** `403 Forbidden` with `"detail": "Admin access required"`

### 4f. Login as admin

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "ADM001", "password": "admin123"}' | python3 -m json.tool
```

Save the admin token:

```bash
ADMIN_TOKEN="<paste-admin-token>"
```

### 4g. Admin: list all employees

```bash
curl -s http://localhost:8000/admin/employees \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
```

### 4h. Admin: create a new employee

```bash
curl -s -X POST http://localhost:8000/admin/employees \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP020",
    "name": "Test User",
    "email": "test@techcorp.com",
    "department": "Engineering",
    "password": "temp123",
    "role": "employee"
  }' | python3 -m json.tool
```

**Expected:** `201 Created` with the new employee's data.

---

## 5. Verify RAG Pipeline

### 5a. Ask a policy question (requires token from step 4a)

```bash
curl -s -X POST http://localhost:8000/chat/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "How much sick leave do I have remaining?"}' | python3 -m json.tool
```

**Expected response** — the LLM should answer with the employee's specific sick leave balance (8.0 days for EMP001):

```json
{
  "answer": "You have 8.0 sick leave days remaining. ...",
  "chunks_retrieved": [
    {
      "document": "leave_policy",
      "section": "Sick Leave",
      "score": 0.42
    }
  ],
  "timing": {
    "retrieval": 0.15,
    "llm_call": 1.23
  }
}
```

### 5b. Verify personalization (different employee, different answer)

Login as a different employee and ask the same question — you should get their leave balance, not Alice's:

```bash
TOKEN2=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "EMP006", "password": "pass123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -X POST http://localhost:8000/chat/ask \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"question": "How much sick leave do I have?"}' | python3 -m json.tool
```

**Expected:** Frank Okafor (EMP006) has only 1.0 sick leave day remaining — answer should differ from Alice's.

### 5c. Verify RAG retrieves policy details (not just leave balance)

```bash
curl -s -X POST http://localhost:8000/chat/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the notice period for resigning?"}' | python3 -m json.tool
```

**Expected:** Answer should cite the 60-day notice period from the resignation policy, with the policy document name and section.

### 5d. Verify graceful handling of out-of-scope questions

```bash
curl -s -X POST http://localhost:8000/chat/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather today?"}' | python3 -m json.tool
```

**Expected:** "I don't have enough information to answer that. Please contact HR." (or similar — the LLM should not hallucinate).

### 5e. Check logs for RAG timing

While asking questions, watch the server console. You should see:

```
2025-01-01 12:00:00 [hr_rag.pipeline] INFO: Retrieval: employee=EMP001, question=How much sick leave do I have?, chunks=5, time=0.152s
2025-01-01 12:00:00 [hr_rag.pipeline] INFO: LLM call: employee=EMP001, model=openai/gpt-4o-mini, time=1.234s
```

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| Server won't start | Is port 8000 free? `lsof -i :8000` |
| Login returns 401 | Did you run `python seed.py`? Is the employee_id correct? |
| Chat returns "insufficient balance" | Are you using a different employee's token? |
| Chat returns generic "error" | Is `GROQ_API_KEY` set and valid? Check server logs. |
| Seed fails on ChromaDB | Delete `chroma_db/` directory and retry |
| Wrong answer / hallucination | Are policy documents detailed enough? Check `policies/` directory. |
| `/auth/me` returns someone else's data | **This should never happen.** If it does, the auth system is broken — verify `get_current_user` extracts identity from the token, not from request parameters. |
