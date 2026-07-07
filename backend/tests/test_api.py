import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, engine, SessionLocal
from app.models import Employee, LeaveType, Role
from app.core.security import hash_password

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

db = SessionLocal()
admin = Employee(emp_code="EMP001", email="admin@x.com", password_hash=hash_password("pw"),
                 first_name="Admin", role=Role.super_admin)
db.add(admin); db.flush()
mgr = Employee(emp_code="EMP002", email="mgr@x.com", password_hash=hash_password("pw"),
               first_name="Mgr", role=Role.manager)
db.add(mgr); db.flush()
emp = Employee(emp_code="EMP003", email="emp@x.com", password_hash=hash_password("pw"),
               first_name="Emp", role=Role.employee, manager_id=mgr.id)
db.add(emp)
db.add(LeaveType(name="Casual", annual_quota=12))
db.commit(); db.close()

client = TestClient(app)


def tok(email):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.json()


def auth(t):
    return {"Authorization": f"Bearer {t['access_token']}"}


def test_login_wrong_password():
    assert client.post("/api/v1/auth/login", json={"email": "emp@x.com", "password": "no"}).status_code == 401


def test_refresh_rotation():
    t = tok("emp@x.com")
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": t["refresh_token"]})
    assert r.status_code == 200
    # old refresh token must now be dead
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": t["refresh_token"]}).status_code == 401


def test_register_new_employee():
    r = client.post("/api/v1/auth/register", json={
        "emp_code": "EMP004",
        "email": "new@x.com",
        "password": "pw",
        "first_name": "New"
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["access_token"] and data["refresh_token"]
    login_r = client.post("/api/v1/auth/login", json={"email": "new@x.com", "password": "pw"})
    assert login_r.status_code == 200


def test_register_duplicate_credentials():
    assert client.post("/api/v1/auth/register", json={
        "emp_code": "EMP001",
        "email": "unique@x.com",
        "password": "pw",
        "first_name": "Dup"
    }).status_code == 409
    assert client.post("/api/v1/auth/register", json={
        "emp_code": "EMP005",
        "email": "emp@x.com",
        "password": "pw",
        "first_name": "Dup"
    }).status_code == 409


def test_rbac_employee_cannot_create():
    t = tok("emp@x.com")
    r = client.post("/api/v1/employees", headers=auth(t), json={
        "emp_code": "X", "email": "x@x.com", "password": "pw", "first_name": "X"})
    assert r.status_code == 403


def test_checkin_checkout_flow():
    t = tok("emp@x.com")
    r = client.post("/api/v1/attendance/check-in", headers=auth(t), json={"latitude": 12.3, "longitude": 76.6})
    assert r.status_code == 200 and r.json()["check_in"]
    # double check-in blocked
    assert client.post("/api/v1/attendance/check-in", headers=auth(t), json={}).status_code == 409
    r = client.post("/api/v1/attendance/check-out", headers=auth(t), json={})
    body = r.json()
    assert r.status_code == 200 and body["check_out"]
    assert body["working_hours"] < 4 and body["status"] == "absent"  # instant checkout => under half-day


def test_leave_flow():
    t_emp, t_mgr = tok("emp@x.com"), tok("mgr@x.com")
    r = client.post("/api/v1/leaves", headers=auth(t_emp), json={
        "leave_type_id": 1, "start_date": "2026-07-13", "end_date": "2026-07-14", "reason": "trip"})
    assert r.status_code == 201, r.text
    req = r.json()
    assert req["days"] == 2.0  # Mon+Tue
    pend = client.get("/api/v1/leaves/pending", headers=auth(t_mgr)).json()
    assert any(p["id"] == req["id"] for p in pend)
    r = client.post(f"/api/v1/leaves/{req['id']}/review", headers=auth(t_mgr), json={"approve": True})
    assert r.json()["status"] == "approved"
    bal = client.get("/api/v1/leaves/balance?year=2026", headers=auth(t_emp)).json()
    assert bal[0]["used"] == 2.0 and bal[0]["remaining"] == 10.0


def test_dashboard_and_audit_rbac():
    t_mgr, t_emp, t_adm = tok("mgr@x.com"), tok("emp@x.com"), tok("admin@x.com")
    assert client.get("/api/v1/reports/dashboard", headers=auth(t_mgr)).status_code == 200
    assert client.get("/api/v1/audit", headers=auth(t_emp)).status_code == 403
    logs = client.get("/api/v1/audit", headers=auth(t_adm)).json()
    assert any(l["action"] == "attendance.check_in" for l in logs)
