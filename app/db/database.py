import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/o11y")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    logger.debug("database session opened")
    try:
        yield db
    except Exception:
        logger.exception("database session encountered an error; rolling back")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("database session closed")
