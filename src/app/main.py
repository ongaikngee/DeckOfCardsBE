from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.app.routers import games, items, models, users
import os
from src.app.core.database import engine, SessionLocal
from dotenv import load_dotenv
import src.app.models.user
from typing import Annotated
from sqlalchemy.orm import Session

load_dotenv()

app = FastAPI()
src.app.models.user.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

app.include_router(items.router)
app.include_router(games.router)
app.include_router(models.router)
app.include_router(users.router)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/")
def read_root():
    url = os.getenv("DATABASE_URL")
    return {"Hello": url}
