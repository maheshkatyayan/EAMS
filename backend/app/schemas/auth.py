from datetime import date
from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(BaseModel):
    emp_code: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str = ""
    phone: str | None = None
    designation: str | None = None
    department_id: int | None = None
    date_joined: date | None = None


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str
