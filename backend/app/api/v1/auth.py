from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, RefreshIn
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])




@router.post("/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, request: Request, db: Session = Depends(get_db)):
    print("Registering user with email:", body.email)
    return auth_service.register(db, body, request.client.host if request.client else None)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    return auth_service.login(db, body.email, body.password, request.client.host if request.client else None)


@router.post("/refresh", response_model=TokenOut)
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    return auth_service.refresh(db, body.refresh_token)


@router.post("/logout", status_code=204)
def logout(body: RefreshIn, db: Session = Depends(get_db)):
    auth_service.logout(db, body.refresh_token)

