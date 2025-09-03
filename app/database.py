from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Tworzenie silnika bazy danych
engine = create_engine(
    settings.database_url, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)


def create_db_and_tables():
    """Tworzy tabele w bazie danych"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Generator sesji bazy danych"""
    with Session(engine) as session:
        yield session
