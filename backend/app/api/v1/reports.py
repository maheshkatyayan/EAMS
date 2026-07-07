import csv, io
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db.session import get_db
from app.core.deps import get_current_user, require
from app.models import Employee, Role, Attendance, AttendanceStatus, LeaveRequest, LeaveStatus

router = APIRouter(prefix="/reports", tags=["reports"])


def month_summary(db: Session, emp_id: int, year: int, month: int) -> dict:
    rows = db.query(Attendance).filter(
        Attendance.employee_id == emp_id,
        extract("year", Attendance.date) == year,
        extract("month", Attendance.date) == month,
    ).all()
    return {
        "employee_id": emp_id, "year": year, "month": month,
        "present_days": sum(1 for r in rows if r.status == AttendanceStatus.present),
        "half_days": sum(1 for r in rows if r.status == AttendanceStatus.half_day),
        "leave_days": sum(1 for r in rows if r.status == AttendanceStatus.on_leave),
        "late_days": sum(1 for r in rows if r.is_late),
        "total_hours": round(sum(r.working_hours for r in rows), 2),
        "overtime_hours": round(sum(r.overtime_hours for r in rows), 2),
    }


@router.get("/monthly/{emp_id}")
def monthly(emp_id: int, year: int, month: int,
            user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    target = db.get(Employee, emp_id)
    if not target:
        raise HTTPException(404, "Employee not found")
    ok = user.id == emp_id or user.role in (Role.hr, Role.super_admin) \
        or (user.role == Role.manager and target.manager_id == user.id)
    if not ok:
        raise HTTPException(403, "Not permitted")
    return month_summary(db, emp_id, year, month)


@router.get("/dashboard")
def dashboard(user: Employee = Depends(require(Role.manager)), db: Session = Depends(get_db)):
    """Org-wide today snapshot for managers/HR dashboards."""
    today = date.today()
    total = db.query(func.count(Employee.id)).filter(Employee.is_active == True).scalar()
    rows = db.query(Attendance).filter(Attendance.date == today).all()
    return {
        "date": str(today),
        "total_employees": total,
        "checked_in": sum(1 for r in rows if r.check_in),
        "late": sum(1 for r in rows if r.is_late),
        "on_leave": sum(1 for r in rows if r.status == AttendanceStatus.on_leave),
        "pending_leaves": db.query(func.count(LeaveRequest.id))
            .filter(LeaveRequest.status == LeaveStatus.pending).scalar(),
    }


@router.get("/export")
def export_csv(year: int, month: int, user: Employee = Depends(require(Role.hr)), db: Session = Depends(get_db)):
    emps = db.query(Employee).filter(Employee.is_active == True).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["emp_code", "name", "present", "half", "leave", "late", "hours", "overtime"])
    for e in emps:
        s = month_summary(db, e.id, year, month)
        w.writerow([e.emp_code, f"{e.first_name} {e.last_name}", s["present_days"], s["half_days"],
                    s["leave_days"], s["late_days"], s["total_hours"], s["overtime_hours"]])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename=attendance_{year}_{month}.csv"})
