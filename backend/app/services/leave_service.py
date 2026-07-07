from datetime import date, timedelta, datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import (LeaveRequest, LeaveType, LeaveStatus, Holiday,
                        Attendance, AttendanceStatus, Notification)
from app.services.audit_service import record


def working_days(db: Session, start: date, end: date) -> float:
    """Count days excluding weekends and company holidays."""
    holidays = {h.date for h in db.query(Holiday).filter(Holiday.date.between(start, end)).all()}
    n, d = 0, start
    while d <= end:
        if d.weekday() < 5 and d not in holidays:
            n += 1
        d += timedelta(days=1)
    return float(n)


def used_days(db: Session, emp_id: int, type_id: int, year: int) -> float:
    total = db.query(func.coalesce(func.sum(LeaveRequest.days), 0.0)).filter(
        LeaveRequest.employee_id == emp_id,
        LeaveRequest.leave_type_id == type_id,
        LeaveRequest.status == LeaveStatus.approved,
        extract("year", LeaveRequest.start_date) == year,
    ).scalar()
    return float(total or 0)


def apply(db: Session, emp_id: int, type_id: int, start: date, end: date, reason: str | None) -> LeaveRequest:
    if end < start:
        raise HTTPException(422, "End date before start date")
    lt = db.get(LeaveType, type_id)
    if not lt:
        raise HTTPException(404, "Leave type not found")
    days = working_days(db, start, end)
    if days == 0:
        raise HTTPException(422, "Range contains no working days")
    remaining = lt.annual_quota - used_days(db, emp_id, type_id, start.year)
    if days > remaining:
        raise HTTPException(422, f"Insufficient balance: {remaining} day(s) left")
    overlap = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == emp_id,
        LeaveRequest.status.in_([LeaveStatus.pending, LeaveStatus.approved]),
        LeaveRequest.start_date <= end, LeaveRequest.end_date >= start,
    ).first()
    if overlap:
        raise HTTPException(409, "Overlaps an existing request")
    req = LeaveRequest(employee_id=emp_id, leave_type_id=type_id, start_date=start,
                       end_date=end, days=days, reason=reason)
    db.add(req)
    record(db, emp_id, "leave.apply", "leave_request")
    db.commit(); db.refresh(req)
    return req


def review(db: Session, req_id: int, reviewer_id: int, approve: bool, note: str | None) -> LeaveRequest:
    req = db.get(LeaveRequest, req_id)
    if not req:
        raise HTTPException(404, "Request not found")
    if req.status != LeaveStatus.pending:
        raise HTTPException(409, "Already reviewed")
    req.status = LeaveStatus.approved if approve else LeaveStatus.rejected
    req.reviewed_by = reviewer_id
    req.review_note = note
    req.reviewed_at = datetime.utcnow()
    if approve:
        _mark_attendance(db, req)
    db.add(Notification(employee_id=req.employee_id,
                        title=f"Leave {req.status.value}",
                        body=f"{req.start_date} to {req.end_date}" + (f" — {note}" if note else "")))
    record(db, reviewer_id, f"leave.{req.status.value}", "leave_request", req.id)
    db.commit(); db.refresh(req)
    return req


def _mark_attendance(db: Session, req: LeaveRequest):
    """Write on_leave rows for each working day of an approved request."""
    holidays = {h.date for h in db.query(Holiday).filter(Holiday.date.between(req.start_date, req.end_date)).all()}
    d = req.start_date
    while d <= req.end_date:
        if d.weekday() < 5 and d not in holidays:
            row = db.query(Attendance).filter(Attendance.employee_id == req.employee_id,
                                              Attendance.date == d).first()
            if not row:
                row = Attendance(employee_id=req.employee_id, date=d)
                db.add(row)
            row.status = AttendanceStatus.on_leave
        d += timedelta(days=1)


def cancel(db: Session, req_id: int, emp_id: int) -> LeaveRequest:
    req = db.get(LeaveRequest, req_id)
    if not req or req.employee_id != emp_id:
        raise HTTPException(404, "Request not found")
    if req.status != LeaveStatus.pending:
        raise HTTPException(409, "Only pending requests can be cancelled")
    req.status = LeaveStatus.cancelled
    record(db, emp_id, "leave.cancel", "leave_request", req.id)
    db.commit(); db.refresh(req)
    return req
