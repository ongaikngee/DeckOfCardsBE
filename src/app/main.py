import os
from typing import Annotated

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import src.app.models.user
from src.app.core.database import SessionLocal, engine
from src.app.models.user import Users
from src.app.routers import chips, games, items, models, users

load_dotenv()

app = FastAPI()
src.app.models.user.Base.metadata.create_all(bind=engine)

def create_default_admin():
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(255) DEFAULT 'user'"
        )
        connection.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
        )
        connection.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL"
        )

    db = SessionLocal()
    try:
        existing_admin = db.query(Users).filter(Users.username == "Admin").first()
        if existing_admin is None:
            hashed_password = bcrypt.hashpw(
                "password".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            admin_user = Users(
                username="Admin", hashed_password=hashed_password, role="admin"
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup_create_default_admin():
    create_default_admin()


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
app.include_router(users.public_router)
app.include_router(chips.router)

origins = [
    "https://deckofcard-beta.vercel.app",
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
