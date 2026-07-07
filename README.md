# EAMS — Employee Attendance Management System

Production-ready attendance platform: React + TypeScript + Vite + Tailwind frontend,
FastAPI + SQLAlchemy + Alembic backend, PostgreSQL, Redis, JWT auth with refresh-token
rotation, RBAC, WebSockets, Docker, and GitHub Actions CI.

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env   # set SECRET_KEY for production
docker compose up --build
```

Open http://localhost — seeded login: **admin@eams.local / Admin@123**
(change it immediately in production).

## Local development

Backend:
```bash
cd backend
pip install -r requirements.txt
# point DATABASE_URL at your postgres, then:
alembic upgrade head
python -m app.tasks.seed
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev        # proxies /api to localhost:8000
```

API docs (Swagger): http://localhost:8000/docs

## Tests

```bash
cd backend && python -m pytest tests/ -q
```

## Architecture

```
frontend (React/TS/Tailwind, Nginx)  ──/api──▶  backend (FastAPI)
                                                 ├── api/v1      routes (thin)
                                                 ├── services    business rules
                                                 ├── repositories DB queries
                                                 ├── models      SQLAlchemy tables
                                                 ├── websocket   live events
                                                 └── middleware  redis rate limit
                                     PostgreSQL ◀┘        Redis ◀┘
```

## Roles

| Role | Can do |
|---|---|
| employee | check in/out, own history, apply/cancel leave |
| manager | + team visibility, approve team leaves, dashboard |
| hr | + manage employees/departments/holidays/leave types, CSV export, raw logs |
| super_admin | + audit log |

## Business rules (configurable in `app/core/config.py` / env)

- Work day 09:00–18:00, 10 min late grace
- Full day ≥ 8h, half day ≥ 4h, overtime = hours − 8
- Leave days exclude weekends & holidays; balance enforced per type per year
- Approved leave auto-marks attendance as `on_leave` and notifies the employee

## Security

JWT access (15 min) + rotating refresh tokens (7 d, stored hashed, revocable),
bcrypt password hashing, role hierarchy RBAC, per-IP rate limiting via Redis,
append-only audit log with actor/IP, HTTPS via your reverse proxy of choice.
