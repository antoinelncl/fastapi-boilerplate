from sqlmodel import Session

from src.api.auth.services import create_email_secure_token
from src.api.users.models import EmailToken, User, UserCreate
from src.api.users.utils import hash_password


async def create_user(db: Session, body: UserCreate):
    user = User(name=body.name, email=body.email, password=hash_password(body.password))
    token = create_email_secure_token(user.email)
    email_token = EmailToken(token=token, user_id=user.id)
    db.add(user)
    db.flush()
    db.add(email_token)
    db.flush()
    return token
