from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import exceptions, jwt
from pydantic import EmailStr
from sqlmodel import Session, select

from src.api.auth.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    REFRESH_TOKEN_SECRET_KEY,
    SALT,
    SECRET_KEY,
)
from src.api.auth.models import RefreshToken
from src.api.users.models import EmailToken, User
from src.api.users.utils import check_password

url_serializer = URLSafeTimedSerializer(SECRET_KEY, salt=SALT)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_token = Depends(oauth2_scheme)


async def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        return None
    if not check_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, db: Session, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)

    db.add(RefreshToken(token=encoded_token, user_id=data["sub"]))
    db.commit()

    return encoded_token


def verify_access_token(token: str = bearer_token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except exceptions.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})

    return payload


def verify_refresh_token(token: str, db: Session):
    refresh_token = db.exec(select(RefreshToken).where(RefreshToken.token == token)).first()
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token", headers={"WWW-Authenticate": "Bearer"})

    user = db.exec(select(User).where(User.id == refresh_token.user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
    except exceptions.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token", headers={"WWW-Authenticate": "Bearer"})

    return payload


def create_email_secure_token(email: EmailStr) -> str:
    token = url_serializer.dumps(email)
    return token


def verify_email_secure_token(token: str, db: Session) -> Optional[str]:
    email_token = db.exec(select(EmailToken).where(EmailToken.token == token)).first()
    if not email_token:
        return None

    try:
        email = url_serializer.loads(token, max_age=1800)
    except SignatureExpired:
        return None
    except BadSignature:
        return None

    return email
