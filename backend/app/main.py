from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.rate_limit import rate_limit
from app.api.v1 import auth, employees, attendance, leaves, reports, notifications, audit, holidays, ws

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.CORS_ORIGINS.split(","),
    allow_origins=["*"], #do not use this in production, use the above line instead
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(rate_limit)

API = "/api/v1"
for r in (auth.router, employees.router, attendance.router, leaves.router,
          reports.router, notifications.router, audit.router, holidays.router, ws.router):
    app.include_router(r, prefix=API)


@app.get("/health")
def health():
    return {"status": "ok"}
