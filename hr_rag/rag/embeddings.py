"""
Embedding Generation
====================
Uses sentence-transformers locally with all-MiniLM-L6-v2.
This runs fully offline — no API calls, no cost, no network needed.
Model is loaded once (lazy) and cached in memory.

We generate embeddings for chunks at index time and for queries at search time.
"""

from typing import List

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of text strings using a local model."""
    if not texts:
        return []
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Generate embedding for a single query string."""
    result = embed_texts([query])
    return result[0]
