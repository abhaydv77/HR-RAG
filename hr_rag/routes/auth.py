from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hr_rag.db.database import get_db
from hr_rag.db.models import Employee
from hr_rag.services.auth_service import (
    verify_password,
    create_access_token,
    get_current_user,
    AuthContext,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    employee_id: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    employee_id: str
    name: str
    role: str


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate an employee and return a JWT.

    IDENTITY VERIFICATION:
    The employee proves who they are by providing their employee_id
    AND password. The server verifies the password hash. If valid,
    a JWT is issued with the employee_id and role embedded.

    After login, the client presents this JWT on every request.
    The server decrypts the JWT to get the identity — it never
    trusts a client-supplied employee_id from the request body.
    """
    employee = db.query(Employee).filter(
        Employee.employee_id == request.employee_id
    ).first()

    if not employee or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID or password",
        )

    if not verify_password(request.password, employee.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID or password",
        )

    token = create_access_token(
        employee_id=employee.employee_id,
        role=employee.role,
    )

    return LoginResponse(
        access_token=token,
        employee_id=employee.employee_id,
        name=employee.name,
        role=employee.role,
    )


class MeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    role: str
    leave_balance_sick: float
    leave_balance_casual: float
    leave_balance_earned: float


@router.get("/me", response_model=MeResponse)
def get_me(
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated employee's own profile data.

    IDENTITY sourced from: verified JWT token.
    NO identity information is taken from URL parameters or body.
    """
    employee = db.query(Employee).filter(
        Employee.employee_id == auth.employee_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return MeResponse(
        employee_id=employee.employee_id,
        name=employee.name,
        email=employee.email,
        department=employee.department,
        role=employee.role,
        leave_balance_sick=employee.leave_balance_sick,
        leave_balance_casual=employee.leave_balance_casual,
        leave_balance_earned=employee.leave_balance_earned,
    )
