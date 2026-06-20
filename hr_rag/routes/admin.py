from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from hr_rag.db.database import get_db
from hr_rag.db.models import Employee
from hr_rag.services.auth_service import (
    hash_password,
    require_admin,
    AuthContext,
)

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateEmployeeRequest(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    password: str
    role: str = "employee"
    leave_balance_sick: float = 12.0
    leave_balance_casual: float = 15.0
    leave_balance_earned: float = 20.0


class EmployeeResponse(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    role: str


@router.post("/employees", response_model=EmployeeResponse, status_code=201)
def create_employee(
    request: CreateEmployeeRequest,
    auth: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Admin-only: Add a new employee to the system.

    In a real HR system, this simulates HR creating accounts for new hires.
    There is no public signup — employees cannot create their own accounts.
    """
    existing = db.query(Employee).filter(
        (Employee.employee_id == request.employee_id) |
        (Employee.email == request.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee ID or email already exists",
        )

    employee = Employee(
        employee_id=request.employee_id,
        name=request.name,
        email=request.email,
        department=request.department,
        role=request.role,
        hashed_password=hash_password(request.password),
        leave_balance_sick=request.leave_balance_sick,
        leave_balance_casual=request.leave_balance_casual,
        leave_balance_earned=request.leave_balance_earned,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)

    return EmployeeResponse(
        employee_id=employee.employee_id,
        name=employee.name,
        email=employee.email,
        department=employee.department,
        role=employee.role,
    )


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]


@router.get("/employees", response_model=EmployeeListResponse)
def list_employees(
    auth: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: List all employees in the system."""
    employees = db.query(Employee).all()
    return EmployeeListResponse(
        employees=[
            EmployeeResponse(
                employee_id=e.employee_id,
                name=e.name,
                email=e.email,
                department=e.department,
                role=e.role,
            )
            for e in employees
        ]
    )
