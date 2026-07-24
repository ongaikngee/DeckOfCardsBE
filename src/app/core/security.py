import hashlib
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

load_dotenv()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def hash_password(password: str) -> str:
    # Convert string to bytes
    password_bytes = password.encode("utf-8")
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as a string to store in your database
    return hashed.decode("utf-8")


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = data.copy()
    payload.update({"exp": expire, "type": "refresh"})
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return token, expire


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "token_expired",
                "message": "Access token expired",
            },
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "message": "Invalid access token",
            },
        )

    return payload


# def decode_access_token(token: str) -> dict:
#     try:
#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM],
#         )
#     except InvalidTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#         )

#     return payload


def decode_refresh_token(token: str) -> dict:

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return payload
