from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import Base


class Product(Base):
    """SQLAlchemy model for products."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    default_unit = Column(String(50), default="unit")
    default_quantity = Column(Float, default=1.0)
    shelf_life_days = Column(Integer, nullable=True)
    image_url = Column(Text, nullable=True)

    # Home zone - where this product belongs (for "put it back" feature)
    home_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)

    # RFID tag ID if this product has one (for bulk containers, spices, snacks)
    rfid_tag_id = Column(String(100), nullable=True, index=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    home_zone = relationship("Zone", back_populates="products")


# Pydantic schemas
class ProductBase(BaseModel):
    name: str
    barcode: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    default_unit: str = "unit"
    default_quantity: float = 1.0
    shelf_life_days: Optional[int] = None
    image_url: Optional[str] = None
    home_zone_id: Optional[int] = None
    rfid_tag_id: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    default_unit: Optional[str] = None
    default_quantity: Optional[float] = None
    shelf_life_days: Optional[int] = None
    image_url: Optional[str] = None
    home_zone_id: Optional[int] = None
    rfid_tag_id: Optional[str] = None


class ZoneBasic(BaseModel):
    """Minimal zone info for embedding in product response."""
    id: int
    name: str
    location: Optional[str]

    class Config:
        from_attributes = True


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    home_zone: Optional[ZoneBasic] = None

    class Config:
        from_attributes = True
