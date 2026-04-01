from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import Base


class Freezer(Base):
    """SQLAlchemy model for freezer units."""
    __tablename__ = "freezers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# Pydantic schemas
class FreezerBase(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None


class FreezerCreate(FreezerBase):
    pass


class FreezerUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class FreezerResponse(FreezerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
