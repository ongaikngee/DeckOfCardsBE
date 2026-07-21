from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from typing import Annotated
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.app.core.database import SessionLocal
from src.app.models.user import Users
from src.app.models.chips import Chips as ChipsModel
from datetime import timedelta
from src.app.core.security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    hash_password,
)
from src.app.core.auth import get_current_user

router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)]
)

public_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class UserInfo(BaseModel):
    id: int
    username: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str


class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@public_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=hash_password(create_user_request.password),
        role="user",
    )

    try:
        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": create_user_model.username}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=create_user_model.id,
            username=create_user_model.username,
            role=create_user_model.role,
        ),
    )
    
@router.get("/chip-counts")
async def get_users_chip_counts(db: db_dependency):
    results = (
        db.query(
            Users.id.label("user_id"),
            Users.created_at,
            Users.username,
            Users.role,
            func.coalesce(func.sum(ChipsModel.amount), 0).label("chip_count"),
        )
        .outerjoin(ChipsModel, ChipsModel.user_id == Users.id)
        .filter(Users.deleted_at.is_(None))
        .group_by(Users.id)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "username": row.username,
            "role": row.role,
            "created_at": row.created_at,
            "chip_count": int(row.chip_count or 0),
        }
        for row in results
    ]


@router.get("/{user_id}")
async def get_user(db: db_dependency, user_id: int):
    user = (
        db.query(Users)
        .filter(Users.id == user_id)
        .filter(Users.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/")
async def get_users(db: db_dependency):
    users = db.query(Users).filter(Users.deleted_at.is_(None)).all()
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user_id: int):
    user = (
        db.query(Users)
        .filter(Users.id == user_id)
        .filter(Users.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # mutate username so it becomes available for reuse
    now = datetime.utcnow()
    base_username = f"{user.username}_deleted_{now.strftime('%d%m%y')}"
    attempt = base_username
    counter = 1
    # ensure uniqueness excluding the current record
    while (
        db.query(Users)
        .filter(Users.id != user.id)
        .filter(Users.username == attempt)
        .first()
    ):
        attempt = f"{base_username}_{counter}"
        counter += 1

    user.username = attempt
    user.deleted_at = func.now()
    db.add(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/make-admin")
async def make_admin(db: db_dependency, user_id: int):
    user = (
        db.query(Users)
        .filter(Users.id == user_id)
        .filter(Users.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.role = "admin"
    db.add(user)
    db.commit()

    return {"message": "User promoted to admin", "user_id": user.id, "role": user.role}


@router.put("/{user_id}")
async def update_user(
    db: db_dependency, user_id: int, update_user_request: CreateUserRequest
):
    user = (
        db.query(Users)
        .filter(Users.id == user_id)
        .filter(Users.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.username = update_user_request.username
    user.hashed_password = hash_password(update_user_request.password)

    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    return user


@public_router.post(
    "/login",
    response_model=LoginResponse,
)
async def login_user(db: db_dependency, login_request: LoginRequest):

    user = (
        db.query(Users)
        .filter(Users.username == login_request.username)
        .filter(Users.deleted_at.is_(None))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            username=user.username,
            role=user.role,
        ),
    )


@router.put("/{user_id}/update-password")
async def update_password(
    db: db_dependency, user_id: int, update_password_request: UpdatePasswordRequest
):
    user = (
        db.query(Users)
        .filter(Users.id == user_id)
        .filter(Users.deleted_at.is_(None))
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if the current password is correct
    if not verify_password(
        update_password_request.current_password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Update the password
    user.hashed_password = hash_password(update_password_request.new_password)
    db.add(user)
    db.commit()

    return {"message": "Password updated successfully"}
