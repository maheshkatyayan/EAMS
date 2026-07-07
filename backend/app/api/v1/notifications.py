from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models import Employee, Notification
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotifOut(BaseModel):
    id: int
    title: str
    body: str | None
    is_read: bool
    created_at: datetime
    class Config: from_attributes = True


@router.get("", response_model=list[NotifOut])
def list_mine(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.employee_id == user.id)\
             .order_by(Notification.created_at.desc()).limit(50).all()


@router.post("/{notif_id}/read", status_code=204)
def mark_read(notif_id: int, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, notif_id)
    if n and n.employee_id == user.id:
        n.is_read = True
        db.commit()
