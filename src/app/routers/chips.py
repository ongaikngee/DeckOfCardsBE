from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timezone

from sqlalchemy import func

from src.app.core.database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from src.app.models.chips import Chips as ChipsModel
from src.app.models.user import Users
from enum import Enum
from starlette import status

router = APIRouter(prefix="/chips", tags=["Chips"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class Reason(str, Enum):
    topup = "Topup"
    lottery = "Lottery"
    jackpot = "Jackpot"
    payout = "Payout"
    loss = "Loss"
    bet = "Bet"
    ante = "Ante"


class Chips(BaseModel):
    amount: int = Field(
        ge=-10000, le=10000, description="Value can be between -10,000 to 10,000"
    )
    reason: Reason

    @model_validator(mode="after")
    def validate_amount(self):
        if self.reason == Reason.loss or self.reason == Reason.ante:
            if self.amount >= 0:
                raise ValueError("Loss amount must be negative")
        else:
            if self.amount <= 0:
                raise ValueError(f"{self.reason.value} amount must be positive")

        return self


@router.get("/", status_code=status.HTTP_200_OK)
def get_all(db: db_dependency, skip: int = 0, limit: int = 100):
    chips = (
        db.query(ChipsModel)
        .order_by(ChipsModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"data": chips}


@router.get("/{user_id}")
def get_chips_by_user(
    db: db_dependency,
    user_id: int,
    showTopup: bool = Query(True),
    skip: int = 0,
    limit: int = 20,
):
    # Check if user exists in users table, if not return error
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Return chips for the user
    query = db.query(ChipsModel).filter(ChipsModel.user_id == user_id)

    # Only show top-up record if requested
    if showTopup:
        query = query.filter(ChipsModel.reason == Reason.topup)

    chips = query.order_by(ChipsModel.created_at.desc()).offset(skip).limit(limit).all()

    # Get the sum of amount based on user_id
    total_amount = (
        db.query(ChipsModel)
        .filter(ChipsModel.user_id == user_id)
        .with_entities(func.sum(ChipsModel.amount))
        .scalar()
    )

    return {"data": chips, "total_amount": total_amount}


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
def update_chips_count(user_id: int, chips: Chips, db: db_dependency):
    chips_model = ChipsModel(
        amount=chips.amount,
        user_id=user_id,
        reason=chips.reason,
        created_at=datetime.now(timezone.utc),
    )

    # check if user exists in users table, if not return error
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.add(chips_model)
    db.commit()
    db.refresh(chips_model)

    return {"data": chips_model.id}
