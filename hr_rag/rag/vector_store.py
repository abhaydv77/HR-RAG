"""
Vector Store (ChromaDB)
=======================
Why ChromaDB for this project:
- Persistent by default (data survives restarts)
- Simple to run (no separate server needed for dev)
- Supports cosine similarity search out of the box
- Python-native API

Tradeoff: For production at scale, you'd want pgvector (if already
using PostgreSQL) or Pinecone/Weaviate. ChromaDB is perfect for
a demo/portfolio project.
"""

import os
import chromadb
from chromadb.config import Settings
from chromadb.errors import InvalidCollectionException
from typing import List, Dict

from hr_rag.config import CHROMA_DB_DIR

COLLECTION_NAME = "hr_policies"


def get_chroma_client():
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    return chromadb.PersistentClient(
        path=CHROMA_DB_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection(client=None):
    if client is None:
        client = get_chroma_client()
    try:
        return client.get_collection(COLLECTION_NAME)
    except InvalidCollectionException:
        return client.create_collection(COLLECTION_NAME)


def index_chunks(chunks: List[Dict[str, str]], embeddings: List[List[float]]):
    """Store chunked policy documents with their embeddings in ChromaDB."""
    collection = get_or_create_collection()
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [
        {
            "document_name": c["document_name"],
            "section_heading": c["section_heading"],
        }
        for c in chunks
    ]
    documents = [c["content"] for c in chunks]

    # Upsert — re-run seeding safely
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents,
    )


def search_chunks(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    """Search for the top_k most relevant chunks given a query embedding."""
    collection = get_or_create_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    retrieved = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            retrieved.append({
                "chunk_id": results["ids"][0][i],
                "document_name": results["metadatas"][0][i]["document_name"],
                "section_heading": results["metadatas"][0][i]["section_heading"],
                "content": results["documents"][0][i],
                "score": results["distances"][0][i] if results["distances"] else 0,
            })
    return retrieved
