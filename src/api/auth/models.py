from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Login(SQLModel):
    email: str
    password: str


class LoginResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str


class Register(SQLModel):
    email: EmailStr
    password: str


class VerifyEmail(SQLModel):
    token: str


class RefreshToken(SQLModel, table=True):
    __tablename__: str = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    token: str
    user_id: str
    created_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)


class Refresh(SQLModel):
    refresh_token: str


class RefreshResponse(SQLModel):
    access_token: str
    token_type: str
