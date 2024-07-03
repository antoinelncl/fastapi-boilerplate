import os

from sqlmodel import Session, create_engine

db_url = os.environ.get("DATABASE_URL")

if db_url is None:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(db_url, echo=True)


def get_db():
    with Session(engine) as session:
        yield session
