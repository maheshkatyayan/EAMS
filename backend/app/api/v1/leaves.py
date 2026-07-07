from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user, require
from app.models import Employee, Role, LeaveRequest, LeaveType, LeaveStatus
from app.schemas.leave import LeaveApply, LeaveReview, LeaveOut, LeaveTypeIn, LeaveTypeOut, BalanceOut
from app.services import leave_service as svc
from app.websocket.manager import manager

router = APIRouter(prefix="/leaves", tags=["leaves"])


@router.get("/types", response_model=list[LeaveTypeOut])
def types(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(LeaveType).all()


@router.post("/types", response_model=LeaveTypeOut, status_code=201)
def create_type(body: LeaveTypeIn, user: Employee = Depends(require(Role.hr)), db: Session = Depends(get_db)):
    lt = LeaveType(**body.model_dump())
    db.add(lt); db.commit(); db.refresh(lt)
    return lt


@router.get("/balance", response_model=list[BalanceOut])
def balance(year: int | None = None, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    from datetime import date
    y = year or date.today().year
    out = []
    for lt in db.query(LeaveType).all():
        used = svc.used_days(db, user.id, lt.id, y)
        out.append(BalanceOut(leave_type_id=lt.id, name=lt.name, quota=lt.annual_quota,
                              used=used, remaining=lt.annual_quota - used))
    return out


@router.post("", response_model=LeaveOut, status_code=201)
async def apply(body: LeaveApply, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    req = svc.apply(db, user.id, body.leave_type_id, body.start_date, body.end_date, body.reason)
    await manager.broadcast_role("manager", {"event": "leave_request", "employee_id": user.id,
                                             "name": f"{user.first_name} {user.last_name}"})
    return req


@router.get("/mine", response_model=list[LeaveOut])
def mine(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(LeaveRequest).filter(LeaveRequest.employee_id == user.id)\
             .order_by(LeaveRequest.created_at.desc()).all()


@router.get("/pending", response_model=list[LeaveOut])
def pending(user: Employee = Depends(require(Role.manager)), db: Session = Depends(get_db)):
    q = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.pending)
    if user.role == Role.manager:
        q = q.join(Employee, LeaveRequest.employee_id == Employee.id).filter(Employee.manager_id == user.id)
    return q.order_by(LeaveRequest.created_at).all()


@router.post("/{req_id}/review", response_model=LeaveOut)
async def review(req_id: int, body: LeaveReview,
                 user: Employee = Depends(require(Role.manager)), db: Session = Depends(get_db)):
    req = db.get(LeaveRequest, req_id)
    if not req:
        raise HTTPException(404, "Request not found")
    if user.role == Role.manager:
        target = db.get(Employee, req.employee_id)
        if target.manager_id != user.id:
            raise HTTPException(403, "Not your report")
    req = svc.review(db, req_id, user.id, body.approve, body.note)
    await manager.send_to(req.employee_id, {"event": "leave_reviewed", "status": req.status.value})
    return req


@router.post("/{req_id}/cancel", response_model=LeaveOut)
def cancel(req_id: int, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    return svc.cancel(db, req_id, user.id)
