from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/games", tags=['Games'])

class Decks(BaseModel):
    deck_id: int
    deck: list
    
@router.get("/")
def get_all():
    return {"data": [1,2,3,4]}


@router.get("/{game_id}")
def read_game(game_id: int, q: str | None = None):
    return {"game_id": game_id, "q": q}

