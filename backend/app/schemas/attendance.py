from datetime import date, datetime
from pydantic import BaseModel
from app.models import AttendanceStatus, LogType


class PunchIn(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    device_info: str | None = None


class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    date: date
    check_in: datetime | None
    check_out: datetime | None
    working_hours: float
    overtime_hours: float
    is_late: bool
    early_exit: bool
    status: AttendanceStatus
    class Config: from_attributes = True


class LogOut(BaseModel):
    id: int
    employee_id: int
    log_type: LogType
    timestamp: datetime
    latitude: float | None
    longitude: float | None
    ip_address: str | None
    device_info: str | None
    class Config: from_attributes = True
