from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app.core.database import SessionLocal
from src.app.core.security import (
    decode_access_token,
    security
)
from fastapi.security import HTTPAuthorizationCredentials

from src.app.models.user import Users


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    payload = decode_access_token(token)
    username = payload.get("sub")

    user = (
        db.query(Users)
        .filter(Users.username == username)
        .filter(Users.deleted_at.is_(None))
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return user
