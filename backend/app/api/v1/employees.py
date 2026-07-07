from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user, require
from app.core.security import hash_password
from app.models import Employee, Department, Role
from app.repositories import employee_repo
from app.schemas.employee import EmployeeIn, EmployeeOut, EmployeeUpdate, DepartmentIn, DepartmentOut
from app.services.audit_service import record

router = APIRouter(tags=["employees"])


@router.get("/employees/me", response_model=EmployeeOut)
def me(user: Employee = Depends(get_current_user)):
    return user


@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(department_id: int | None = None, q: str | None = None,
                   skip: int = 0, limit: int = 50,
                   user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role in (Role.hr, Role.super_admin):
        return employee_repo.list_(db, department_id, None, q, skip, limit)
    if user.role == Role.manager:
        return employee_repo.list_(db, department_id, user.id, q, skip, limit)
    return [user]  # plain employees see only themselves


@router.post("/employees", response_model=EmployeeOut, status_code=201)
def create_employee(body: EmployeeIn, request: Request,
                    user: Employee = Depends(require(Role.hr)), db: Session = Depends(get_db)):
    if employee_repo.by_email(db, body.email) or employee_repo.by_code(db, body.emp_code):
        raise HTTPException(409, "Email or employee code already exists")
    data = body.model_dump()
    data["password_hash"] = hash_password(data.pop("password"))
    if data["date_joined"] is None:
        data.pop("date_joined")
    emp = Employee(**data)
    db.add(emp)
    db.flush()
    record(db, user.id, "employee.create", "employee", emp.id, ip=request.client.host if request.client else None)
    db.commit(); db.refresh(emp)
    return emp


@router.patch("/employees/{emp_id}", response_model=EmployeeOut)
def update_employee(emp_id: int, body: EmployeeUpdate,
                    user: Employee = Depends(require(Role.hr)), db: Session = Depends(get_db)):
    emp = db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    changes = body.model_dump(exclude_unset=True)
    for k, v in changes.items():
        setattr(emp, k, v)
    record(db, user.id, "employee.update", "employee", emp.id, detail=jsonable(changes))
    db.commit(); db.refresh(emp)
    return emp


def jsonable(d: dict) -> dict:
    return {k: (v.value if hasattr(v, "value") else v) for k, v in d.items()}


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Department).order_by(Department.name).all()


@router.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(body: DepartmentIn, user: Employee = Depends(require(Role.hr)), db: Session = Depends(get_db)):
    if db.query(Department).filter(Department.name == body.name).first():
        raise HTTPException(409, "Department exists")
    d = Department(**body.model_dump())
    db.add(d)
    record(db, user.id, "department.create", "department")
    db.commit(); db.refresh(d)
    return d
