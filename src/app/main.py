from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from src.app.routers import games, items, models, users, chips
import os
from src.app.core.database import engine, SessionLocal
from dotenv import load_dotenv
import src.app.models.user
from src.app.models.user import Users
from src.app.routers.users import (
    get_user_by_username,
)
from typing import Annotated
from sqlalchemy.orm import Session
import bcrypt
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
import jwt


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "5f875aa0970d55c20f50c01a222f297c551a33622c1b981cfe1e07c07e9d4920"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


load_dotenv()

app = FastAPI()
src.app.models.user.Base.metadata.create_all(bind=engine)


def verify_password(plain, hashed):
    # Check if the provided password matches the hashed password
    if not bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return True


def authenticate_user(db, username: str, password: str):
    print("Inside authenticate_user")
    print("username:", username)
    print("password:", password)

    user = get_user_by_username(db, username)

    # 1. Check if the user is None FIRST
    if not user:
        print("Authentication failed: User not found in database.")
        return False

    # 2. Safe to print now! We know for sure the user exists here.
    print("Successfully retrieved the user!")
    print("User ID:", user.id)

    if not verify_password(password, user.hashed_password):
        print("Authentication failed: Incorrect password.")
        return False

    print("Authentication successful for user ID:", user.id)
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
) -> Token:

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
