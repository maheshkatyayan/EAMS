from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.core.deps import get_current_user, require
from app.models import Employee, Role, Holiday

router = APIRouter(prefix="/holidays", tags=["holidays"])


class HolidayIn(BaseModel):
    name: str
    date: date


class HolidayOut(HolidayIn):
    id: int
    class Config: from_attributes = True


@router.get("", response_model=list[HolidayOut])
def list_holidays(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Holiday).order_by(Holiday.date).all()


@router.post("", response_model=HolidayOut, status_code=201)
def add_holiday(body: HolidayIn, user: Employee = Depends(require(Role.hr)), db: Session = Depends(get_db)):
    if db.query(Holiday).filter(Holiday.date == body.date).first():
        raise HTTPException(409, "Holiday already exists on that date")
    h = Holiday(**body.model_dump())
    db.add(h); db.commit(); db.refresh(h)
    return h
