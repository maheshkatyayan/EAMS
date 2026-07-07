from datetime import date
from pydantic import BaseModel, EmailStr
from app.models import Role


class DepartmentIn(BaseModel):
    name: str
    description: str | None = None


class DepartmentOut(DepartmentIn):
    id: int
    class Config: from_attributes = True


class EmployeeIn(BaseModel):
    emp_code: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str = ""
    phone: str | None = None
    role: Role = Role.employee
    designation: str | None = None
    department_id: int | None = None
    manager_id: int | None = None
    date_joined: date | None = None


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    role: Role | None = None
    designation: str | None = None
    department_id: int | None = None
    manager_id: int | None = None
    is_active: bool | None = None


class EmployeeOut(BaseModel):
    id: int
    emp_code: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    role: Role
    designation: str | None
    department_id: int | None
    manager_id: int | None
    date_joined: date
    is_active: bool
    class Config: from_attributes = True
