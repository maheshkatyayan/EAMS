from datetime import date, datetime
from pydantic import BaseModel
from app.models import LeaveStatus


class LeaveTypeIn(BaseModel):
    name: str
    annual_quota: int = 12
    is_paid: bool = True


class LeaveTypeOut(LeaveTypeIn):
    id: int
    class Config: from_attributes = True


class LeaveApply(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveReview(BaseModel):
    approve: bool
    note: str | None = None


class LeaveOut(BaseModel):
    id: int
    employee_id: int
    leave_type_id: int
    start_date: date
    end_date: date
    days: float
    reason: str | None
    status: LeaveStatus
    reviewed_by: int | None
    review_note: str | None
    created_at: datetime
    class Config: from_attributes = True


class BalanceOut(BaseModel):
    leave_type_id: int
    name: str
    quota: int
    used: float
    remaining: float
