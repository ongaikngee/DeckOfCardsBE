from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.app.core.database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from src.app.models.chips import Chips as ChipsModel
from src.app.models.user import Users

router = APIRouter(prefix="/chips", tags=["Chips"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[Session, Depends(get_db)]


class Chips(BaseModel):
    amount: int
    user_id: int
    reason: str | None = None
    
    
@router.get("/")
def get_all():
    return {"data": [1,2,3,4]}

@router.get("/{user_id}")
def get_chips_by_user(user_id: int):
    # Check if user exists in users table, if not return error
    db = next(get_db())
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    # Return chips for the user
    chips = db.query(ChipsModel).filter(ChipsModel.user_id == user_id).all()
    return {"data": chips}

@router.post("/")
def update_chips_count(chips: Chips, db: db_dependency):
    chips_model = ChipsModel(
        amount=chips.amount,
        user_id=chips.user_id,
        reason=chips.reason
    )
    
    # check if user exists in users table, if not return error
    user = db.query(Users).filter(Users.id == chips.user_id).first()
    if not user:
        return {"error": "User not found"}
    
    db.add(chips_model)
    db.commit()
    db.refresh(chips_model)
    
    return {"data": chips_model.id}