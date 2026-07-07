from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.models import Employee, Role

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# role hierarchy: higher number = more power
LEVEL = {Role.employee: 0, Role.manager: 1, Role.hr: 2, Role.super_admin: 3}


def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> Employee:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = db.get(Employee, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User inactive or not found")
    return user


def require(min_role: Role):
    """Allow the given role and anything above it in the hierarchy."""
    def checker(user: Employee = Depends(get_current_user)) -> Employee:
        if LEVEL[user.role] < LEVEL[min_role]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker
