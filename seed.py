"""
Seed Script
===========
Run this to create/reset the database with dummy employees and
index the HR policy documents into the vector store.

Usage:
    python seed.py

This is safe to re-run — it drops and recreates tables, so you get
a clean state every time.
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("seed")

# Ensure we can import hr_rag
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hr_rag.db.database import engine, Base, SessionLocal
from hr_rag.db.models import Employee
from hr_rag.services.auth_service import hash_password
from hr_rag.rag.chunker import chunk_all_policies
from hr_rag.rag.embeddings import embed_texts
from hr_rag.rag.vector_store import index_chunks, get_chroma_client
from hr_rag.config import POLICIES_DIR


def seed_database():
    """Drop all tables, recreate them, and insert dummy data."""
    logger.info("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Admin user
        admin = Employee(
            employee_id="ADM001",
            name="Sarah Chen",
            email="sarah.chen@techcorp.com",
            department="Human Resources",
            role="admin",
            hashed_password=hash_password("admin123"),
            leave_balance_sick=0,
            leave_balance_casual=0,
            leave_balance_earned=0,
        )
        db.add(admin)

        # Dummy employees — varied departments, roles, and leave balances
        employees_data = [
            {
                "employee_id": "EMP001", "name": "Alice Johnson",
                "email": "alice.johnson@techcorp.com", "department": "Engineering",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 8.0, "leave_balance_casual": 10.0, "leave_balance_earned": 15.0,
            },
            {
                "employee_id": "EMP002", "name": "Bob Martinez",
                "email": "bob.martinez@techcorp.com", "department": "Engineering",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 12.0, "leave_balance_casual": 5.0, "leave_balance_earned": 20.0,
            },
            {
                "employee_id": "EMP003", "name": "Chiara Patel",
                "email": "chiara.patel@techcorp.com", "department": "Design",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 3.5, "leave_balance_casual": 14.0, "leave_balance_earned": 10.0,
            },
            {
                "employee_id": "EMP004", "name": "David Kim",
                "email": "david.kim@techcorp.com", "department": "Engineering",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 6.0, "leave_balance_casual": 8.0, "leave_balance_earned": 25.0,
            },
            {
                "employee_id": "EMP005", "name": "Elena Torres",
                "email": "elena.torres@techcorp.com", "department": "Marketing",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 10.0, "leave_balance_casual": 12.0, "leave_balance_earned": 18.0,
            },
            {
                "employee_id": "EMP006", "name": "Frank Okafor",
                "email": "frank.okafor@techcorp.com", "department": "Sales",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 1.0, "leave_balance_casual": 3.0, "leave_balance_earned": 30.0,
            },
            {
                "employee_id": "EMP007", "name": "Grace Liu",
                "email": "grace.liu@techcorp.com", "department": "Engineering",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 11.0, "leave_balance_casual": 7.0, "leave_balance_earned": 22.0,
            },
            {
                "employee_id": "EMP008", "name": "Hassan Ali",
                "email": "hassan.ali@techcorp.com", "department": "Design",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 4.0, "leave_balance_casual": 9.0, "leave_balance_earned": 12.0,
            },
            {
                "employee_id": "EMP009", "name": "Irina Petrova",
                "email": "irina.petrova@techcorp.com", "department": "Marketing",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 7.0, "leave_balance_casual": 11.0, "leave_balance_earned": 16.0,
            },
            {
                "employee_id": "EMP010", "name": "James Wilson",
                "email": "james.wilson@techcorp.com", "department": "Finance",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 9.0, "leave_balance_casual": 6.0, "leave_balance_earned": 14.0,
            },
            {
                "employee_id": "EMP011", "name": "Katherine Ng",
                "email": "katherine.ng@techcorp.com", "department": "HR",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 5.0, "leave_balance_casual": 13.0, "leave_balance_earned": 19.0,
            },
            {
                "employee_id": "EMP012", "name": "Leo Schmidt",
                "email": "leo.schmidt@techcorp.com", "department": "Engineering",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 2.0, "leave_balance_casual": 4.0, "leave_balance_earned": 28.0,
            },
            {
                "employee_id": "EMP013", "name": "Maya Singh",
                "email": "maya.singh@techcorp.com", "department": "Sales",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 10.5, "leave_balance_casual": 8.5, "leave_balance_earned": 21.0,
            },
            {
                "employee_id": "EMP014", "name": "Nathan Cooper",
                "email": "nathan.cooper@techcorp.com", "department": "Operations",
                "role": "employee", "password": "pass123",
                "leave_balance_sick": 6.5, "leave_balance_casual": 10.0, "leave_balance_earned": 17.0,
            },
        ]

        for emp_data in employees_data:
            employee = Employee(
                employee_id=emp_data["employee_id"],
                name=emp_data["name"],
                email=emp_data["email"],
                department=emp_data["department"],
                role=emp_data["role"],
                hashed_password=hash_password(emp_data["password"]),
                leave_balance_sick=emp_data["leave_balance_sick"],
                leave_balance_casual=emp_data["leave_balance_casual"],
                leave_balance_earned=emp_data["leave_balance_earned"],
            )
            db.add(employee)

        db.commit()
        logger.info("Seeded %d employees (1 admin + 14 regular)", 1 + len(employees_data))
    finally:
        db.close()


def seed_vector_store():
    """Chunk policy documents and index them into ChromaDB."""
    if not os.path.isdir(POLICIES_DIR):
        logger.warning("Policies directory '%s' not found. Skipping vector store seeding.", POLICIES_DIR)
        return

    logger.info("Chunking policy documents from '%s'...", POLICIES_DIR)
    chunks = chunk_all_policies(POLICIES_DIR)
    logger.info("Generated %d chunks", len(chunks))

    if not chunks:
        logger.warning("No chunks generated. Nothing to index.")
        return

    logger.info("Generating embeddings for %d chunks...", len(chunks))
    texts = [c["content"] for c in chunks]
    embeddings = embed_texts(texts)
    logger.info("Generated %d embeddings", len(embeddings))

    logger.info("Indexing into ChromaDB...")
    index_chunks(chunks, embeddings)

    logger.info("Vector store seeded successfully with %d chunks", len(chunks))


def main():
    logger.info("=" * 50)
    logger.info("HR RAG Database Seed")
    logger.info("=" * 50)

    seed_database()
    seed_vector_store()

    logger.info("Seeding complete! You can now run the server:")
    logger.info("  uvicorn hr_rag.main:app --reload")


if __name__ == "__main__":
    main()
