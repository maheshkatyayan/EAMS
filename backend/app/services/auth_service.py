from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Employee, RefreshToken, Role
from app.core import security
from app.repositories import employee_repo
from app.services.audit_service import record


def register(db: Session, body, ip: str | None) -> dict:
    if employee_repo.by_email(db, body.email) or employee_repo.by_code(db, body.emp_code):
        raise HTTPException(409, "Email or employee code already exists")
    data = body.model_dump()
    data["password_hash"] = security.hash_password(data.pop("password"))
    data["role"] = Role.hr  # Default role for new employees
    if data["date_joined"] is None:
        data.pop("date_joined")
    print("Creating new employee with data:", data)
    user = Employee(**data)
    db.add(user)
    print("Flushing to get user ID...")
    db.flush()
    print("User ID obtained:", user.id)
    raw, h, exp = security.new_refresh_token()
    db.add(RefreshToken(employee_id=user.id, token_hash=h, expires_at=exp))
    record(db, None, "auth.register", "employee", user.id, ip=ip)
    db.commit(); db.refresh(user)
    return {
        "access_token": security.create_access_token(user.id, user.role.value),
        "refresh_token": raw,
    }


def login(db: Session, email: str, password: str, ip: str | None) -> dict:
    user = db.query(Employee).filter(Employee.email == email).first()
    if not user or not security.verify_password(password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    if not user.is_active:
        raise HTTPException(403, "Account disabled")
    raw, h, exp = security.new_refresh_token()
    db.add(RefreshToken(employee_id=user.id, token_hash=h, expires_at=exp))
    record(db, user.id, "auth.login", "employee", user.id, ip=ip)
    db.commit()
    return {
        "access_token": security.create_access_token(user.id, user.role.value),
        "refresh_token": raw,
    }


def refresh(db: Session, raw: str) -> dict:
    h = security.hash_refresh(raw)
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == h).first()
    if not row or row.revoked or row.expires_at < datetime.utcnow():
        raise HTTPException(401, "Invalid refresh token")
    user = db.get(Employee, row.employee_id)
    if not user or not user.is_active:
        raise HTTPException(401, "User inactive")
    # rotate: kill old, issue new
    row.revoked = True
    new_raw, new_h, exp = security.new_refresh_token()
    db.add(RefreshToken(employee_id=user.id, token_hash=new_h, expires_at=exp))
    db.commit()
    return {
        "access_token": security.create_access_token(user.id, user.role.value),
        "refresh_token": new_raw,
    }


def logout(db: Session, raw: str):
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == security.hash_refresh(raw)).first()
    if row:
        row.revoked = True
        db.commit()
