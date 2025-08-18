from sqlmodel import SQLModel, create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.SQLALCHEMY_ECHO)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)