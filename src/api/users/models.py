from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from src.models import BaseModel


class User(BaseModel, table=True):
    __tablename__: str = "users"

    name: str
    email: str
    password: str
    email_verified_at: datetime | None = None
    last_login_at: datetime | None = None


class EmailToken(SQLModel, table=True):
    __tablename__: str = "email_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    token: str = Field(sa_column_kwargs={"unique": True}, nullable=False)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)


class UserCreate(SQLModel):
    name: str
    email: str
    password: str


class UserCreateResponse(SQLModel):
    id: UUID
    name: str
    email: str
    created_at: datetime


class UserRead(SQLModel):
    id: UUID
    name: str
    email: str
    email_verified_at: datetime | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None


class UserUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    email_verified_at: datetime | None = None
