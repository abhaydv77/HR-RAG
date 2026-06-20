from sqlalchemy.orm import Session
from hr_rag.db.models import Employee


def get_employee_by_id(db: Session, employee_id: str) -> Employee | None:
    """Fetch employee by their unique employee_id.
    This is used by the RAG pipeline to pull personal data
    for the prompt. Identity is verified by the auth layer
    before this is called — employee_id comes from the token, not user input."""
    return db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()


def get_employee_personal_context(employee: Employee) -> str:
    """Formats the employee's personal data into a string
    that will be injected into the LLM prompt."""
    return f"""
Employee Personal Data (confidential — only this employee's data):
- Name: {employee.name}
- Department: {employee.department}
- Role: {employee.role}
- Leave Balances:
  - Sick Leave: {employee.leave_balance_sick} days
  - Casual Leave: {employee.leave_balance_casual} days
  - Earned Leave: {employee.leave_balance_earned} days
- Join Date: {employee.join_date.strftime('%Y-%m-%d') if employee.join_date else 'N/A'}
"""
