from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["Items"])

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@router.get("/")
async def read_items(q: str | None = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@router.get("/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@router.post("/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@router.put("/{item_id}")
async def update_item(item_id: int, item:Item, q:str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q":q})
    return result
