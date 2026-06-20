from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hr_rag.db.database import get_db
from hr_rag.db.models import Employee
from hr_rag.services.auth_service import get_current_user, AuthContext
from hr_rag.services.employee_service import (
    get_employee_by_id,
    get_employee_personal_context,
)
from hr_rag.rag.pipeline import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    chunks_retrieved: list
    timing: dict


@router.post("/ask", response_model=ChatResponse)
def ask_question(
    request: ChatRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ask an HR policy question. The answer is personalized with the
    authenticated employee's own data.

    CRITICAL: The employee_id used to fetch personal data comes from
    `auth.employee_id` — the verified JWT token. The question text
    cannot impersonate another employee because identity is bound to
    the token, not to any content in the request body.
    """
    employee = get_employee_by_id(db, auth.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    personal_context = get_employee_personal_context(employee)

    result = answer_question(
        question=request.question,
        employee_id=auth.employee_id,
        personal_context=personal_context,
    )

    return ChatResponse(
        answer=result["answer"],
        chunks_retrieved=result["chunks_retrieved"],
        timing=result["timing"],
    )
