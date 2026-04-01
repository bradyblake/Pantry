from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import enum

from database import Base


class SensorType(str, enum.Enum):
    ESP32_CAM = "esp32_cam"
    RFID_ANTENNA = "rfid_antenna"
    LASER_COUNTER = "laser_counter"
    PIR_MOTION = "pir_motion"


class Sensor(Base):
    """Generic sensor registry."""
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_type = Column(String(50), nullable=False)
    hardware_id = Column(String(100), unique=True, nullable=False)  # MAC address or unique ID
    name = Column(String(255), nullable=False)
    zone = Column(String(100), nullable=True)  # e.g., "V1_Shelf_1", "V3_Spice_Tower"
    location_description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    is_online = Column(Boolean, default=False)
    last_seen_at = Column(DateTime, nullable=True)
    config_json = Column(Text, nullable=True)  # Sensor-specific config
    created_at = Column(DateTime, server_default=func.now())


class RfidTag(Base):
    """RFID tags linked to containers/products."""
    __tablename__ = "rfid_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_id = Column(String(100), unique=True, nullable=False)  # EPC or UID
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    container_name = Column(String(255), nullable=True)  # "Large flour container"

    # Zone tracking for "put it back" feature
    home_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)  # Where it belongs
    current_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)  # Where it is now

    # Status
    is_present = Column(Boolean, default=True)  # Is it in its home zone?
    is_out = Column(Boolean, default=False)  # Currently removed from shelf?
    removed_at = Column(DateTime, nullable=True)  # When it was taken
    last_seen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", lazy="joined")
    home_zone = relationship("Zone", foreign_keys=[home_zone_id], lazy="joined")
    current_zone = relationship("Zone", foreign_keys=[current_zone_id], lazy="joined")


class RfidEvent(Base):
    """RFID detection events for tracking item movement."""
    __tablename__ = "rfid_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_id = Column(Integer, ForeignKey("rfid_tags.id"), nullable=False)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=True)

    # Event types: 'removed', 'returned_correct', 'returned_wrong', 'moved', 'detected'
    event_type = Column(String(50), nullable=False)

    # Zone tracking
    from_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    to_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)

    rssi = Column(Integer, nullable=True)  # Signal strength
    created_at = Column(DateTime, server_default=func.now())

    tag = relationship("RfidTag", lazy="joined")
    sensor = relationship("Sensor", lazy="joined")
    from_zone = relationship("Zone", foreign_keys=[from_zone_id], lazy="joined")
    to_zone = relationship("Zone", foreign_keys=[to_zone_id], lazy="joined")


class CameraEvent(Base):
    """Camera detection/recognition events."""
    __tablename__ = "camera_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # 'motion', 'item_removed', 'item_added', 'unrecognized'
    zone = Column(String(100), nullable=True)
    zone_index = Column(Integer, nullable=True)  # Which LED zone (0-5)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    confidence = Column(Float, nullable=True)
    image_path = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    sensor = relationship("Sensor", lazy="joined")
    product = relationship("Product", lazy="joined")


class CanLane(Base):
    """Can rotation lane configuration."""
    __tablename__ = "can_lanes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    lane_number = Column(Integer, nullable=False)  # 1-6
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(255), nullable=True)  # Fallback if no product linked
    current_count = Column(Integer, default=0)
    max_capacity = Column(Integer, default=10)
    low_stock_threshold = Column(Integer, default=2)
    created_at = Column(DateTime, server_default=func.now())

    sensor = relationship("Sensor", lazy="joined")
    product = relationship("Product", lazy="joined")


class CanEvent(Base):
    """Can counting events (IN/OUT)."""
    __tablename__ = "can_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lane_id = Column(Integer, ForeignKey("can_lanes.id"), nullable=False)
    event_type = Column(String(10), nullable=False)  # 'in' or 'out'
    count_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    lane = relationship("CanLane", lazy="joined")


# Pydantic Schemas

class SensorBase(BaseModel):
    sensor_type: str
    hardware_id: str
    name: str
    zone: Optional[str] = None
    location_description: Optional[str] = None
    ip_address: Optional[str] = None
    config_json: Optional[str] = None


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    zone: Optional[str] = None
    location_description: Optional[str] = None
    ip_address: Optional[str] = None
    is_online: Optional[bool] = None
    config_json: Optional[str] = None


class SensorResponse(SensorBase):
    id: int
    is_online: bool
    last_seen_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RfidTagBase(BaseModel):
    tag_id: str
    product_id: Optional[int] = None
    container_name: Optional[str] = None
    home_zone_id: Optional[int] = None


class RfidTagCreate(RfidTagBase):
    pass


class RfidTagUpdate(BaseModel):
    product_id: Optional[int] = None
    container_name: Optional[str] = None
    home_zone_id: Optional[int] = None


class ZoneInfo(BaseModel):
    id: int
    name: str
    location: Optional[str] = None

    class Config:
        from_attributes = True


class ProductInfo(BaseModel):
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class RfidTagResponse(RfidTagBase):
    id: int
    current_zone_id: Optional[int] = None
    is_present: bool
    is_out: bool
    removed_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    home_zone: Optional[ZoneInfo] = None
    current_zone: Optional[ZoneInfo] = None
    product: Optional[ProductInfo] = None

    class Config:
        from_attributes = True


class RfidEventCreate(BaseModel):
    tag_id: int
    sensor_id: Optional[int] = None
    event_type: str
    from_zone_id: Optional[int] = None
    to_zone_id: Optional[int] = None
    rssi: Optional[int] = None


class RfidEventResponse(BaseModel):
    id: int
    tag_id: int
    event_type: str
    from_zone_id: Optional[int] = None
    to_zone_id: Optional[int] = None
    rssi: Optional[int] = None
    created_at: datetime
    from_zone: Optional[ZoneInfo] = None
    to_zone: Optional[ZoneInfo] = None

    class Config:
        from_attributes = True


class PutItBackAlert(BaseModel):
    """Alert for item that needs to be returned."""
    tag_id: int
    tag_epc: str
    product_name: Optional[str]
    container_name: Optional[str]
    home_zone_id: int
    home_zone_name: str
    home_zone_location: Optional[str]
    current_zone_id: Optional[int]
    current_zone_name: Optional[str]
    removed_at: Optional[datetime]
    minutes_out: int


class CanLaneBase(BaseModel):
    sensor_id: int
    lane_number: int
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    max_capacity: int = 10
    low_stock_threshold: int = 2


class CanLaneCreate(CanLaneBase):
    pass


class CanLaneUpdate(BaseModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    current_count: Optional[int] = None
    max_capacity: Optional[int] = None
    low_stock_threshold: Optional[int] = None


class CanLaneResponse(CanLaneBase):
    id: int
    current_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class CameraEventCreate(BaseModel):
    sensor_id: int
    event_type: str
    zone: Optional[str] = None
    zone_index: Optional[int] = None
    product_id: Optional[int] = None
    confidence: Optional[float] = None
    image_path: Optional[str] = None


class CameraEventResponse(BaseModel):
    id: int
    sensor_id: int
    event_type: str
    zone: Optional[str] = None
    zone_index: Optional[int] = None
    product_id: Optional[int] = None
    confidence: Optional[float] = None
    image_path: Optional[str] = None
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
