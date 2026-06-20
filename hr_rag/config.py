import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
# Embeddings are generated locally by sentence-transformers (all-MiniLM-L6-v2).
# No API key needed — free, offline, zero cost per call.
# See rag/embeddings.py for the model name and loading logic.

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
POLICIES_DIR = os.getenv("POLICIES_DIR", "./policies")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hr_rag.db")

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL", "https://api.groq.com/openai/v1"
)
