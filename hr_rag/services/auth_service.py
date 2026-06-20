"""
AUTH SERVICE — Identity from Token, NEVER from User Input
==========================================================

CRITICAL DESIGN DECISION:
Every API request that touches employee-specific data MUST verify
identity from the JWT token — NEVER from a value in the request body,
URL parameter, or query string.

WHY?
If we allowed the client to tell us "I am employee E004", a malicious
user could simply change that value to E005 and see another employee's
data. The JWT is cryptographically signed and cannot be forged. By
extracting identity ONLY from the verified token, we guarantee that
users can only access their own data.

HOW?
1. User logs in with employee_id + password → receives a JWT
2. JWT payload contains {"sub": employee_id, "role": "employee"}
3. Every protected endpoint requires the JWT in the Authorization header
4. A FastAPI dependency decodes the JWT and injects the verified
   identity into the request — the route handler uses that, never
   a user-supplied parameter.
"""

import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from hr_rag.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS
from hr_rag.db.database import get_db
from hr_rag.db.models import Employee

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(employee_id: str, role: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS)
    payload = {
        "sub": employee_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


class AuthContext:
    """Injected into route handlers to provide verified identity."""
    def __init__(self, employee_id: str, role: str):
        self.employee_id = employee_id
        self.role = role


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AuthContext:
    """
    FastAPI dependency that:
    1. Extracts the JWT from the Authorization header
    2. Decodes and verifies it
    3. Looks up the employee in the database
    4. Returns an AuthContext with the verified identity

    Route handlers MUST use this dependency and MUST use the returned
    AuthContext.employee_id — never a value from the request body.
    """
    payload = decode_access_token(credentials.credentials)
    employee_id: Optional[str] = payload.get("sub")
    role: Optional[str] = payload.get("role")

    if employee_id is None or role is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()
    if not employee or not employee.is_active:
        raise HTTPException(status_code=401, detail="Employee not found or inactive")

    return AuthContext(employee_id=employee_id, role=role)


def require_admin(auth: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Dependency for admin-only endpoints."""
    if auth.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return auth
