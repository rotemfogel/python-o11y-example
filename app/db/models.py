from datetime import datetime, UTC
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(36), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    password = Column(Text, nullable=False)
