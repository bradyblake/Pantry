from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

from database import Base


class Inventory(Base):
    """SQLAlchemy model for inventory items."""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Float, nullable=False, default=0)
    location = Column(String(100), nullable=True)  # 'pantry', 'fridge', 'freezer'
    expiration_date = Column(Date, nullable=True)
    # Freezer-specific fields
    freezer_id = Column(Integer, ForeignKey("freezers.id"), nullable=True, index=True)
    frozen_date = Column(Date, nullable=True)
    freeze_by_date = Column(Date, nullable=True)
    container_description = Column(Text, nullable=True)
    photo_path = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", lazy="joined")
    freezer = relationship("Freezer", lazy="joined")


class InventoryLog(Base):
    """SQLAlchemy model for inventory change log."""
    __tablename__ = "inventory_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity_change = Column(Float, nullable=False)  # positive = add, negative = use
    source = Column(String(50), nullable=False)  # 'manual', 'receipt_scan', 'weight_sensor', etc.
    confidence = Column(Float, default=1.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    product = relationship("Product", lazy="joined")


# Pydantic schemas
class InventoryBase(BaseModel):
    product_id: int
    quantity: float
    location: Optional[str] = None
    expiration_date: Optional[date] = None
    freezer_id: Optional[int] = None
    frozen_date: Optional[date] = None
    freeze_by_date: Optional[date] = None
    container_description: Optional[str] = None
    photo_path: Optional[str] = None


class InventoryAdd(BaseModel):
    """Schema for adding stock."""
    product_id: int
    quantity: float
    location: Optional[str] = "pantry"
    expiration_date: Optional[date] = None
    notes: Optional[str] = None
    # Freezer-specific
    freezer_id: Optional[int] = None
    frozen_date: Optional[date] = None
    freeze_by_date: Optional[date] = None
    container_description: Optional[str] = None


class InventoryUse(BaseModel):
    """Schema for using/removing stock."""
    product_id: int
    quantity: float
    notes: Optional[str] = None


class InventoryUpdate(BaseModel):
    """Schema for updating an inventory item."""
    quantity: Optional[float] = None
    location: Optional[str] = None
    expiration_date: Optional[date] = None
    freezer_id: Optional[int] = None
    frozen_date: Optional[date] = None
    freeze_by_date: Optional[date] = None
    container_description: Optional[str] = None


class ProductInInventory(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    default_unit: str

    class Config:
        from_attributes = True


class FreezerInInventory(BaseModel):
    id: int
    name: str
    location: Optional[str] = None

    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    location: Optional[str] = None
    expiration_date: Optional[date] = None
    freezer_id: Optional[int] = None
    frozen_date: Optional[date] = None
    freeze_by_date: Optional[date] = None
    container_description: Optional[str] = None
    photo_path: Optional[str] = None
    updated_at: datetime
    product: ProductInInventory
    freezer: Optional[FreezerInInventory] = None

    class Config:
        from_attributes = True


class InventoryLogResponse(BaseModel):
    id: int
    product_id: int
    quantity_change: float
    source: str
    confidence: float
    notes: Optional[str] = None
    created_at: datetime
    product: ProductInInventory

    class Config:
        from_attributes = True
