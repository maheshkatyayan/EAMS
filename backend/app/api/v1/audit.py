from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import require
from app.models import Employee, Role, AuditLog
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditOut(BaseModel):
    id: int
    actor_id: int | None
    action: str
    entity: str | None
    entity_id: int | None
    detail: dict | None
    ip_address: str | None
    created_at: datetime
    class Config: from_attributes = True


@router.get("", response_model=list[AuditOut])
def list_audit(skip: int = 0, limit: int = 100, action: str | None = None,
               user: Employee = Depends(require(Role.super_admin)), db: Session = Depends(get_db)):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    return q.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
