from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.app.core.auth import get_current_user

router = APIRouter(
    prefix="/games", tags=["Games"], dependencies=[Depends(get_current_user)]
)


class Decks(BaseModel):
    deck_id: int
    deck: list


@router.get("/")
def get_all():
    return {"data": [1, 2, 3, 4]}


@router.get("/{game_id}")
def read_game(game_id: int, q: str | None = None):
    return {"game_id": game_id, "q": q}
