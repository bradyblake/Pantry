"""Zone model - physical locations with LED feedback."""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

from database import Base


class LedState(str, Enum):
    OFF = "off"
    IDLE = "idle"           # Dim white - monitoring
    SCANNING = "scanning"   # Red - change detected, scanning
    CONFIRM = "confirm"     # Yellow - needs user confirmation
    SUCCESS = "success"     # Green - logged successfully
    RETURN_HERE = "return"  # Blue pulsing - put item back here
    ADD_MODE = "add"        # Blue solid - scan items IN
    HIGHLIGHT = "highlight" # White bright - ingredient finder


class Zone(Base):
    """Physical zone with LED strip for feedback."""
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))  # e.g., "V1 Shelf 1", "V3 Spice Tower"
    description = Column(Text)

    # Hardware identifiers
    esp32_id = Column(String(50))  # Which ESP32-CAM controls this zone
    led_strip_index = Column(Integer, default=0)  # Which LED segment (0-5 typically)
    rfid_antenna_id = Column(Integer)  # Which RFID antenna covers this zone (nullable)

    # Zone type
    zone_type = Column(String(50), default="shelf")  # shelf, bulk, spice, pouch, can_lane

    # Current LED state
    current_led_state = Column(String(20), default="idle")
    led_color = Column(String(20))  # Current RGB hex color

    # Position for UI display
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="home_zone")


# Pydantic schemas
class ZoneBase(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    esp32_id: Optional[str] = None
    led_strip_index: int = 0
    rfid_antenna_id: Optional[int] = None
    zone_type: str = "shelf"
    display_order: int = 0


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    esp32_id: Optional[str] = None
    led_strip_index: Optional[int] = None
    rfid_antenna_id: Optional[int] = None
    zone_type: Optional[str] = None
    display_order: Optional[int] = None


class ZoneRead(ZoneBase):
    id: int
    current_led_state: str
    led_color: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LedCommand(BaseModel):
    """Command to control zone LED."""
    state: LedState
    color: Optional[str] = None  # Hex color override
    duration_ms: Optional[int] = None  # Auto-off after duration
    pulse: bool = False  # Pulsing effect


class InventoryEntry(BaseModel):
    """A single inventory entry showing where stock is stored."""
    quantity: float
    location: Optional[str] = None
    container_description: Optional[str] = None
    freezer_name: Optional[str] = None


class IngredientLocation(BaseModel):
    """Location info for an ingredient."""
    ingredient_text: str
    product_id: Optional[int]
    product_name: Optional[str]
    zone_id: Optional[int]
    zone_name: Optional[str]
    zone_location: Optional[str]
    in_stock: bool
    quantity_available: float = 0
    inventory_entries: List[InventoryEntry] = []


class FindIngredientsResponse(BaseModel):
    """Response from ingredient finder."""
    recipe_id: int
    recipe_name: str
    ingredients: List[IngredientLocation]
    zones_to_light: List[int]
    missing_ingredients: List[str]
    message: str
