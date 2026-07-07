from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user, require
from app.models import Employee, Role, AttendanceLog
from app.schemas.attendance import PunchIn, AttendanceOut, LogOut
from app.services import attendance_service as svc
from app.websocket.manager import manager

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _ip(request: Request):
    return request.client.host if request.client else None


@router.post("/check-in", response_model=AttendanceOut)
async def check_in(body: PunchIn, request: Request,
                   user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    row = svc.check_in(db, user.id, body.latitude, body.longitude, _ip(request), body.device_info)
    await manager.broadcast_role("manager", {"event": "check_in", "employee_id": user.id,
                                             "name": f"{user.first_name} {user.last_name}", "late": row.is_late})
    return row


@router.post("/check-out", response_model=AttendanceOut)
async def check_out(body: PunchIn, request: Request,
                    user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    row = svc.check_out(db, user.id, body.latitude, body.longitude, _ip(request), body.device_info)
    await manager.broadcast_role("manager", {"event": "check_out", "employee_id": user.id,
                                             "name": f"{user.first_name} {user.last_name}", "hours": row.working_hours})
    return row


@router.get("/me", response_model=list[AttendanceOut])
def my_history(start: date | None = None, end: date | None = None,
               user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    return svc.history(db, user.id, start, end)


@router.get("/employee/{emp_id}", response_model=list[AttendanceOut])
def employee_history(emp_id: int, start: date | None = None, end: date | None = None,
                     user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    target = db.get(Employee, emp_id)
    if not target:
        raise HTTPException(404, "Employee not found")
    allowed = user.role in (Role.hr, Role.super_admin) or user.id == emp_id \
        or (user.role == Role.manager and target.manager_id == user.id)
    if not allowed:
        raise HTTPException(403, "Not permitted")
    return svc.history(db, emp_id, start, end)


@router.get("/logs/{emp_id}", response_model=list[LogOut])
def raw_logs(emp_id: int, user: Employee = Depends(require(Role.hr)), db: Session = Depends(get_db)):
    return db.query(AttendanceLog).filter(AttendanceLog.employee_id == emp_id)\
             .order_by(AttendanceLog.timestamp.desc()).limit(200).all()
