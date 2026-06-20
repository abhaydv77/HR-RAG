# HR Policy RAG Bot

A Retrieval-Augmented Generation (RAG) chatbot backend for HR policy questions. Employees can ask about company policies and get answers personalized with their own HR data (leave balances, etc.).

## Tech Stack

- **FastAPI** — Python web framework
- **SQLite + SQLAlchemy** — Relational database for employee data
- **ChromaDB** — Vector store for policy document embeddings
- **OpenRouter API** — LLM and embedding API (OpenAI-compatible)

## Project Structure

```
hr_rag/
├── main.py              # FastAPI app entry point
├── config.py            # Environment config
├── db/
│   ├── database.py      # SQLAlchemy engine and session
│   └── models.py        # ORM models (Employee, PolicyChunk)
├── routes/
│   ├── auth.py          # /auth/login, /auth/me
│   ├── chat.py          # /chat/ask
│   └── admin.py         # /admin/employees (admin-only)
├── services/
│   ├── auth_service.py  # JWT, password hashing, token verification
│   └── employee_service.py  # Employee data access
├── rag/
│   ├── chunker.py       # Policy document → semantic chunks
│   ├── embeddings.py    # Embedding generation via OpenRouter
│   ├── vector_store.py  # ChromaDB wrapper (index + search)
│   └── pipeline.py      # Full RAG pipeline orchestration
seed.py                  # Database and vector store seeder
policies/                # HR policy markdown documents
├── leave_policy.md
├── wfh_policy.md
├── expense_policy.md
├── code_of_conduct.md
└── resignation_policy.md
```

## How to Run

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your secrets:

```bash
cp .env.example .env
```

Required:
- `JWT_SECRET` — any random string (run `openssl rand -hex 32`)
- `GROQ_API_KEY` — sign up at https://console.groq.com/keys

### 3. Seed the database

```bash
python seed.py
```

This creates: SQLite database with 1 admin + 14 dummy employees, and indexes policy documents into ChromaDB.

### 4. Run the server

```bash
uvicorn hr_rag.main:app --reload
```

Server starts at http://localhost:8000. API docs at http://localhost:8000/docs.

## API Endpoints

### Authentication
- `POST /auth/login` — Login with employee_id + password, get JWT token
- `GET /auth/me` — Get your own profile (requires token)

### Chat
- `POST /chat/ask` — Ask an HR policy question (requires token). Returns answer + retrieved chunks + timing

### Admin (requires admin role)
- `POST /admin/employees` — Add a new employee
- `GET /admin/employees` — List all employees

## Dummy Credentials

| Employee ID | Password  | Name             | Department   | Role    |
|-------------|-----------|------------------|-------------|---------|
| ADM001      | admin123  | Sarah Chen       | HR           | admin   |
| EMP001      | pass123   | Alice Johnson    | Engineering  | employee|
| EMP002      | pass123   | Bob Martinez     | Engineering  | employee|
| ...         | pass123   | ...              | ...          | ...     |

## Design Notes

### Auth / Identity
Identity is extracted from the JWT token, never from request body parameters. This prevents impersonation — a user cannot claim to be another employee by changing a field in their request.

### RAG Pipeline
Two data sources feed into each answer:
1. Policy chunks retrieved semantically from ChromaDB (via embeddings)
2. Employee's personal data fetched from SQLite using their verified employee ID

Both are combined into a single prompt sent to the LLM.

### Why ChromaDB?
Persistent, no separate server needed, Python-native. Perfect for dev/demo. Swap for pgvector or Pinecone for production.
