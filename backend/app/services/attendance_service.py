from datetime import datetime, date, time
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import Attendance, AttendanceLog, AttendanceStatus, LogType, Holiday
from app.services.audit_service import record


def _t(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def _today_row(db: Session, emp_id: int, d: date) -> Attendance | None:
    return db.query(Attendance).filter(Attendance.employee_id == emp_id, Attendance.date == d).first()


def check_in(db: Session, emp_id: int, lat, lng, ip, device) -> Attendance:
    now = datetime.now()
    today = now.date()
    row = _today_row(db, emp_id, today)
    if row and row.check_in:
        raise HTTPException(409, "Already checked in today")
    if not row:
        row = Attendance(employee_id=emp_id, date=today)
        db.add(row)
    row.check_in = now
    grace_deadline = datetime.combine(today, _t(settings.WORK_START)).timestamp() + settings.LATE_GRACE_MINUTES * 60
    row.is_late = now.timestamp() > grace_deadline
    row.status = AttendanceStatus.present  # provisional; finalized at check-out
    db.add(AttendanceLog(employee_id=emp_id, log_type=LogType.check_in, timestamp=now,
                         latitude=lat, longitude=lng, ip_address=ip, device_info=device))
    record(db, emp_id, "attendance.check_in", "attendance", detail={"late": row.is_late}, ip=ip)
    db.commit(); db.refresh(row)
    return row


def check_out(db: Session, emp_id: int, lat, lng, ip, device) -> Attendance:
    now = datetime.now()
    row = _today_row(db, emp_id, now.date())
    if not row or not row.check_in:
        raise HTTPException(409, "Check in first")
    row.check_out = now
    hours = round((now - row.check_in).total_seconds() / 3600, 2)
    row.working_hours = hours
    row.overtime_hours = round(max(0.0, hours - settings.FULL_DAY_HOURS), 2)
    row.early_exit = now.time() < _t(settings.WORK_END)
    if hours >= settings.FULL_DAY_HOURS:
        row.status = AttendanceStatus.present
    elif hours >= settings.HALF_DAY_HOURS:
        row.status = AttendanceStatus.half_day
    else:
        row.status = AttendanceStatus.absent
    db.add(AttendanceLog(employee_id=emp_id, log_type=LogType.check_out, timestamp=now,
                         latitude=lat, longitude=lng, ip_address=ip, device_info=device))
    record(db, emp_id, "attendance.check_out", "attendance", detail={"hours": hours}, ip=ip)
    db.commit(); db.refresh(row)
    return row


def is_holiday(db: Session, d: date) -> bool:
    return db.query(Holiday).filter(Holiday.date == d).first() is not None


def history(db: Session, emp_id: int, start: date | None, end: date | None) -> list[Attendance]:
    q = db.query(Attendance).filter(Attendance.employee_id == emp_id)
    if start: q = q.filter(Attendance.date >= start)
    if end: q = q.filter(Attendance.date <= end)
    return q.order_by(Attendance.date.desc()).all()
