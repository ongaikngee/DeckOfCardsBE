from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from typing import Annotated
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.app.core.database import SessionLocal
from src.app.models.user import Users
from src.app.models.chips import Chips as ChipsModel
import bcrypt

router = APIRouter(prefix="/users", tags=["Users"])


def hash_password(password: str) -> str:
    # Convert string to bytes
    password_bytes = password.encode("utf-8")
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as a string to store in your database
    return hashed.decode("utf-8")


class CreateUserRequest(BaseModel):
    username: str
    password: str
    
class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
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

    return {
        "user_id": create_user_model.id,
        "username": create_user_model.username,
        "role": create_user_model.role,
    }


@router.get("/chip-counts")
async def get_users_chip_counts(db: db_dependency):
    results = (
        db.query(
            Users.id.label("user_id"),
            Users.username,
            func.coalesce(func.sum(ChipsModel.amount), 0).label("chip_count"),
        )
        .outerjoin(ChipsModel, ChipsModel.user_id == Users.id)
        .group_by(Users.id)
        .all()
    )

    return [
        {
            "user_id": row.user_id,
            "username": row.username,
            "chip_count": int(row.chip_count or 0),
        }
        for row in results
    ]


@router.get("/{user_id}")
async def get_user(db: db_dependency, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/")
async def get_users(db: db_dependency):
    users = db.query(Users).all()
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.put("/{user_id}")
async def update_user(
    db: db_dependency, user_id: int, update_user_request: CreateUserRequest
):
    user = db.query(Users).filter(Users.id == user_id).first()
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

@router.post("/login")
async def login_user(db: db_dependency, login_request: CreateUserRequest):
    user = db.query(Users).filter(Users.username == login_request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if the provided password matches the hashed password
    if not bcrypt.checkpw(login_request.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return {
        "message": "Login successful",
        "user_id": user.id,
        "role": user.role,
    }

@router.put("/{user_id}/update-password")
async def update_password(db: db_dependency, user_id: int, update_password_request: UpdatePasswordRequest):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if the current password is correct
    if not bcrypt.checkpw(update_password_request.current_password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect"
        )

    # Update the password
    user.hashed_password = hash_password(update_password_request.new_password)
    db.add(user)
    db.commit()
    
    return {"message": "Password updated successfully"}     