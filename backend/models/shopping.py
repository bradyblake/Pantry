from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import Base


class ShoppingItem(Base):
    """SQLAlchemy model for shopping list items."""
    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    custom_item_name = Column(String(255), nullable=True)  # For items not in products table
    quantity = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    checked = Column(Boolean, default=False)
    added_reason = Column(String(50), nullable=True)  # 'manual', 'recipe', 'low_stock'
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    product = relationship("Product", lazy="joined")


# Pydantic schemas
class ShoppingItemBase(BaseModel):
    product_id: Optional[int] = None
    custom_item_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    added_reason: Optional[str] = "manual"


class ShoppingItemCreate(ShoppingItemBase):
    pass


class ShoppingItemUpdate(BaseModel):
    product_id: Optional[int] = None
    custom_item_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    checked: Optional[bool] = None


class ProductInShopping(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    default_unit: str

    class Config:
        from_attributes = True


class ShoppingItemResponse(BaseModel):
    id: int
    product_id: Optional[int] = None
    custom_item_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    checked: bool
    added_reason: Optional[str] = None
    created_at: datetime
    product: Optional[ProductInShopping] = None

    class Config:
        from_attributes = True
