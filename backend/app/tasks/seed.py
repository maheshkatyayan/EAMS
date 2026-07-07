"""Seed initial data: run once after migrations.
   python -m app.tasks.seed
"""
from app.db.session import SessionLocal
from app.models import Employee, Department, LeaveType, Role
from app.core.security import hash_password


def run():
    db = SessionLocal()
    if db.query(Employee).count():
        print("Already seeded"); return
    eng = Department(name="Engineering")
    hr_d = Department(name="Human Resources")
    db.add_all([eng, hr_d]); db.flush()
    admin = Employee(emp_code="EMP001", email="admin@eams.local",
                     password_hash=hash_password("Admin@123"),
                     first_name="Super", last_name="Admin",
                     role=Role.super_admin, department_id=hr_d.id)
    db.add(admin)
    db.add_all([LeaveType(name="Casual", annual_quota=12),
                LeaveType(name="Sick", annual_quota=10),
                LeaveType(name="Earned", annual_quota=15),
                LeaveType(name="Unpaid", annual_quota=365, is_paid=False)])
    db.commit()
    print("Seeded. Login: admin@eams.local / Admin@123")


if __name__ == "__main__":
    run()
