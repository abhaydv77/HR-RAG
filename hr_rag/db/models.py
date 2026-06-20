import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from hr_rag.db.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="employee")  # "admin" or "employee"
    hashed_password = Column(String(255), nullable=False)
    leave_balance_sick = Column(Float, default=12.0)
    leave_balance_casual = Column(Float, default=15.0)
    leave_balance_earned = Column(Float, default=20.0)
    join_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PolicyChunk(Base):
    """Stores chunked policy text with metadata.
    Embeddings are stored in ChromaDB (vector store), not in SQLite.
    This table links chunks back to their source documents and provides
    metadata for the retrieval step.
    """
    __tablename__ = "policy_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(64), unique=True, nullable=False, index=True)
    document_name = Column(String(200), nullable=False)
    section_heading = Column(String(300), default="")
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
