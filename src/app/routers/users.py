from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from src.app.core.database import SessionLocal
from src.app.models.user import Users


router = APIRouter(prefix="/users", tags=['Users'])

class CreateUserRequest(BaseModel):
    username: str
    hashed_password: str
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

        
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    print("helo...........")
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password = create_user_request.hashed_password
        # hashed_password=bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()

    return create_user_model