
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL


def create_db_engine(database_url: str = DATABASE_URL):
 

    connect_args = {}

    # SQLite-specific connection configuration
    if database_url.startswith("sqlite"):
        connect_args = {
            "check_same_thread": False
        }

    engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )

    return engine


# Main application database engine
engine = create_db_engine()


# Database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():
 
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
