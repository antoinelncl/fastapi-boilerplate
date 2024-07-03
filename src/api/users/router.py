from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from src.api.auth.services import verify_access_token
from src.api.users.models import User, UserRead, UserUpdate
from src.database import get_db

router = APIRouter(prefix="/users", tags=["users"])
session = Depends(get_db)


@router.patch("/{user_id}", response_model=UserRead, status_code=200, summary="Updates a user")
async def update_user(
    request: Request, user_id: str, user: UserUpdate, db: Session = session, token: str = Depends(verify_access_token)
) -> UserRead:
    user_db = db.get(User, user_id)

    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User not found."})

    user_data = user.model_dump(exclude_unset=True)
    user_data["updated_at"] = datetime.now()
    user_db.sqlmodel_update(user_data)

    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return UserRead.model_validate(user_db)


@router.get("/", response_model=list[UserRead], status_code=200, summary="Lists all users")
async def list_users(db: Session = session, token: str = Depends(verify_access_token)) -> List[UserRead]:
    users = db.exec(select(User)).all()
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserRead, status_code=200, summary="Shows a user")
async def show_user(user_id: str, db: Session = session, token: str = Depends(verify_access_token)) -> UserRead:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User not found."})

    return UserRead.model_validate(user)
