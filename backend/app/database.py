"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.log_level == "DEBUG"
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def init_db():
    """Initialize database by creating all tables."""
    from app.models import Conversation, Message, IndexedFile, AppSettings

    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def get_db() -> Session:
    """
    Dependency function to get database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
