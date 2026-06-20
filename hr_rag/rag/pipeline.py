"""
RAG Pipeline
============
Orchestrates the full Retrieval-Augmented Generation flow:

1. Receive a question + verified employee_id
2. Fetch employee's personal data from SQL (only THEIR data)
3. Embed the question and retrieve relevant policy chunks from ChromaDB
4. Build a prompt combining: system instructions + policy chunks + personal data + question
5. Call the LLM and return the answer
6. Log timing for each step
"""

import time
import logging
from typing import List, Dict

from openai import OpenAI

from hr_rag.config import GROQ_API_KEY, LLM_MODEL, LLM_BASE_URL
from hr_rag.rag.embeddings import embed_query
from hr_rag.rag.vector_store import search_chunks

logger = logging.getLogger("hr_rag.pipeline")

_client = None


def _get_llm_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url=LLM_BASE_URL,
        )
    return _client


def build_prompt(
    question: str,
    policy_chunks: List[Dict],
    personal_context: str,
) -> str:
    """Build the full prompt with system instructions, context, and question."""
    system = """You are an HR policy assistant for TechCorp Inc. Your job is to answer employee questions about company policies and their personal HR data.

Guidelines:
- Answer based ONLY on the policy documents and employee data provided below.
- If the answer is not in the provided context, say "I don't have enough information to answer that. Please contact HR."
- Be specific and cite the policy document name and section when possible.
- When answering about leave balances, always state the employee's current balance.
- Do NOT reveal other employees' data — you only have access to the current employee's data.
- Keep responses concise but helpful."""

    chunks_text = ""
    for i, chunk in enumerate(policy_chunks):
        chunks_text += f"\n--- Policy Document: {chunk['document_name']} ---\n"
        chunks_text += f"Section: {chunk['section_heading']}\n"
        chunks_text += f"{chunk['content']}\n"

    prompt = f"""{system}

=== RELEVANT POLICY DOCUMENTS ===
{chunks_text}

=== EMPLOYEE PERSONAL DATA ===
{personal_context}

=== QUESTION ===
{question}

=== ANSWER ===
"""
    return prompt


def answer_question(
    question: str,
    employee_id: str,
    personal_context: str,
) -> dict:
    """
    Full RAG pipeline for a single question.

    Returns a dict with:
    - answer: the LLM's response
    - chunks_retrieved: list of chunk summaries
    - timing: duration of retrieval and LLM call in seconds
    """
    timings = {}

    # Step 1: Embed query and retrieve chunks
    t0 = time.time()
    try:
        query_embedding = embed_query(question)
        retrieved_chunks = search_chunks(query_embedding, top_k=5)
    except Exception as e:
        logger.error(f"Retrieval failed for employee={employee_id}: {e}")
        return {
            "answer": "I'm sorry, I encountered an error while searching the policy database. Please try again.",
            "chunks_retrieved": [],
            "timing": {"retrieval": 0, "llm_call": 0, "error": str(e)},
        }
    timings["retrieval"] = time.time() - t0

    logger.info(
        "Retrieval: employee=%s, question=%s, chunks=%d, time=%.3fs",
        employee_id, question, len(retrieved_chunks), timings["retrieval"],
    )

    # Step 2: Build prompt
    prompt = build_prompt(question, retrieved_chunks, personal_context)

    # Step 3: Call LLM
    t1 = time.time()
    try:
        client = _get_llm_client()
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"LLM call failed for employee={employee_id}: {e}")
        answer = "I'm sorry, I encountered an error while generating a response. Please try again."
    timings["llm_call"] = time.time() - t1

    logger.info(
        "LLM call: employee=%s, model=%s, time=%.3fs",
        employee_id, LLM_MODEL, timings["llm_call"],
    )

    chunk_summaries = [
        {
            "document": c["document_name"],
            "section": c["section_heading"],
            "score": c["score"],
        }
        for c in retrieved_chunks
    ]

    return {
        "answer": answer,
        "chunks_retrieved": chunk_summaries,
        "timing": timings,
    }
