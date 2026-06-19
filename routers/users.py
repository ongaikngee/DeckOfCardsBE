from fastapi import APIRouter, Depends
from typing import Annotated
from core.database import SessionLocal
from sqlalchemy.orm import Session
from models.user import User
from starlette import status
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool
    
@router.get("/")
def get_users(db: db_dependency):
    return db.query(User).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):

    create_user_model = User(
        username=create_user_request.username,
        hashed_password = create_user_request.password,
        is_admin = create_user_request.is_admin
        # hashed_password=bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()

    return create_user_model