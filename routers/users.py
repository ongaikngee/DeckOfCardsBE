from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime, timezone

router = APIRouter(prefix="/users", tags=["Users"])

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))    


@router.get("/")
def get_users():
    return {'hello': 'user'}