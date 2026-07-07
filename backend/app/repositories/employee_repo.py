from sqlalchemy.orm import Session
from app.models import Employee


def by_email(db: Session, email: str) -> Employee | None:
    return db.query(Employee).filter(Employee.email == email).first()


def by_code(db: Session, code: str) -> Employee | None:
    return db.query(Employee).filter(Employee.emp_code == code).first()


def list_(db: Session, department_id: int | None = None, manager_id: int | None = None,
          q: str | None = None, skip: int = 0, limit: int = 50) -> list[Employee]:
    query = db.query(Employee)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if manager_id:
        query = query.filter(Employee.manager_id == manager_id)
    if q:
        like = f"%{q}%"
        query = query.filter((Employee.first_name.ilike(like)) | (Employee.last_name.ilike(like)) | (Employee.emp_code.ilike(like)))
    return query.order_by(Employee.id).offset(skip).limit(limit).all()
