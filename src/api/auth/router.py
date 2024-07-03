from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlmodel import Session, select

from src.api.auth.models import Login, LoginResponse, Refresh, RefreshResponse, RefreshToken
from src.api.auth.services import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_email_secure_token,
    verify_refresh_token,
)
from src.api.users.models import EmailToken, User, UserCreate
from src.api.users.services import create_user
from src.config import limiter
from src.database import get_db

router = APIRouter(tags=["login"])
session = Depends(get_db)


@router.post("/register", status_code=204, summary="User registration")
@limiter.limit("5/minute")
async def register(request: Request, background_tasks: BackgroundTasks, user: UserCreate, db: Session = session):
    transaction = db.begin()
    try:
        token = await create_user(db, user)

        transaction.commit()
        return token

    except:
        transaction.rollback()
        raise


@router.post("/verify_email/{token}", status_code=204, summary="Verify email")
@limiter.limit("5/minute")
async def verify_email(request: Request, token: str, db: Session = session):
    email = verify_email_secure_token(token, db)

    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong URL")

    user = db.exec(select(User).where(email == User.email)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong URL")

    try:
        user.sqlmodel_update({"email_verified_at": datetime.now()})
        db.add(user)
        db.commit()
    except:
        db.rollback()
        raise

    try:
        email_token = db.exec(select(EmailToken).where(EmailToken.token == token)).first()
        db.delete(email_token)
        db.commit()
    except:
        db.rollback()
        raise


@router.post("/login", summary="User login")
@limiter.limit("5/minute")
async def login(request: Request, response: Response, login: Login, db: Session = session) -> LoginResponse:
    user = await authenticate_user(db, login.email, login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    current_refresh_token = db.exec(select(RefreshToken).where(RefreshToken.user_id == user.id)).first()
    if current_refresh_token:
        db.delete(current_refresh_token)
        db.commit()

    refresh_token = create_refresh_token({"sub": str(user.id)}, db)
    access_token = create_access_token({"sub": str(user.id)})

    token = LoginResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    response.set_cookie(key="access_token", value=token.access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return token


@router.post("/refresh", summary="Refresh token")
@limiter.limit("5/minute")
async def refresh(request: Request, token: Refresh, response: Response, db: Session = session) -> RefreshResponse:
    refresh_data = verify_refresh_token(token.refresh_token, db)

    access_token = create_access_token(data=refresh_data)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return RefreshResponse(access_token=access_token, token_type="bearer")
