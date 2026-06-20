# HR Policy RAG Bot — TODO

Prioritized by impact. P0 = must-fix before demo, P1 = important quality improvements, P2 = nice to have.

---

## P0 — Blocking Issues

| # | Task | Why It Matters | Effort | Dependencies |
|---|------|---------------|--------|-------------|
| 1 | **Fix DNS/network for `pip install`** | Cannot install dependencies (`chromadb`, `openai`, `sqlalchemy`). The server and seed script cannot run without them. | ~15min (try different DNS, proxy settings, or `--index-url`) | None |
| 2 | **Add startup validation for required env vars** | If `JWT_SECRET` or `OPENROUTER_API_KEY` are unset, the app either uses a well-known secret (JWT forgery) or crashes with a cryptic OpenAI error. A clear startup error in `main.py` prevents misconfiguration. | ~10min | #1 (need to test) |
| 3 | **Run `python seed.py` end-to-end** | The seed script is the only way to create the database and populate the vector store. Until it runs successfully, no data exists to test against. | ~5min | #1 |
| 4 | **Run `uvicorn` and verify all endpoints respond** | Confirm routes load, auth works (login + JWT), admin endpoints enforce role, chat endpoint returns a valid response. | ~15min | #3 |

---

## P1 — Quality & Correctness

| # | Task | Why It Matters | Effort | Dependencies |
|---|------|---------------|--------|-------------|
| 5 | **Remove unused `EmailStr` import** | `routes/admin.py` imports `EmailStr` from pydantic but uses plain `str` for the email field. At best a lint warning; at worst a confusing signal to future readers. | ~1min | None |
| 6 | **Document `DATABASE_URL` in `.env.example`** | `config.py` reads `DATABASE_URL` with a default (`sqlite:///./hr_rag.db`), but the `.env.example` doesn't mention it. Users can't discover they can swap to PostgreSQL without reading source. | ~1min | None |
| 7 | **Write a basic smoke test** | No tests exist. A minimal test (seed → login → ask question) would catch regressions and serve as documentation for how the API works. | ~30min | #3 |
| 8 | **Add `.gitignore`** | The repo will generate `hr_rag.db`, `chroma_db/`, `__pycache__/`, and `.venv/`. Without a `.gitignore`, these can end up committed. | ~2min | None |

---

## P2 — Polish & Edge Cases

| # | Task | Why It Matters | Effort | Dependencies |
|---|------|---------------|--------|-------------|
| 9 | **Move `create_all` to FastAPI lifespan** | `main.py` calls `Base.metadata.create_all` at import time. This works for SQLite but is not the recommended FastAPI pattern and can cause issues with async engines or connection pooling. | ~10min | #1 |
| 10 | **Add query validation to `/chat/ask`** | The endpoint accepts arbitrary strings. Empty questions, excessively long questions (>4K tokens), or offensive content should be caught early rather than forwarded to the LLM. | ~15min | #1 |
| 11 | **Log auth failures (failed login attempts)** | Currently auth failures return 401 but are not logged. For a real HR system, tracking failed login attempts is important for security auditing. | ~10min | None |
| 12 | **Add rate-limiting to `/auth/login`** | No rate limiting means an attacker can brute-force passwords. For production this is critical; for a demo project it's a "nice to have" if you want to demonstrate security awareness. | ~20min (requires `slowapi` or similar) | None |
| 13 | **Add `policies/` directory existence check to server startup** | If `seed.py` hasn't been run or the `policies/` dir is missing, the vector store is empty and chat answers will be unhelpful. A startup warning would help. | ~5min | None |
| 14 | **Replace well-known `JWT_SECRET` default with an explicit error** | `config.py` falls back to `"dev-secret-change-in-production"`. If someone deploys without setting this, their JWT tokens are forgeable. Raising a `ValueError` when the default is detected is safer. | ~5min | None |

---

## Task Dependency Graph

```
#1 (pip install) ─┬─ #3 (seed) ── #4 (smoke test)
                  │
                  └─ #2 (startup validation) ── #9 (lifespan)
                  └─ #13 (policies check)

#5 (unused import) ─── no deps
#6 (env.example)  ─── no deps
#7 (tests)        ─── requires #3
#8 (.gitignore)   ─── no deps
#10 (validation)  ─── requires #1
#11 (auth logging)─── no deps
#12 (rate limit)  ─── requires #1
#14 (jwt default) ─── no deps
```

**First actionable step:** Fix network connectivity, install deps, then run `python seed.py`.
