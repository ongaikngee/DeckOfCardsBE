from fastapi import APIRouter, Depends
from enum import Enum
from src.app.core.auth import get_current_user

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
    
router = APIRouter(prefix="/models", tags=["Models"])
    
@router.get("/{model_name}")
async def get_model(model_name: ModelName, current_user = Depends(get_current_user)):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


