from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime

from database import get_db
from models.sensor import (
    Sensor, SensorCreate, SensorUpdate, SensorResponse,
    RfidTag, RfidTagCreate, RfidTagResponse,
    RfidEvent,
    CameraEvent, CameraEventCreate, CameraEventResponse,
    CanLane, CanLaneCreate, CanLaneUpdate, CanLaneResponse,
    CanEvent
)

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


# ============ Sensors ============

@router.get("/", response_model=list[SensorResponse])
async def list_sensors(
    sensor_type: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all sensors with optional filtering."""
    query = select(Sensor)

    if sensor_type:
        query = query.where(Sensor.sensor_type == sensor_type)
    if zone:
        query = query.where(Sensor.zone == zone)

    query = query.order_by(Sensor.zone, Sensor.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{sensor_id}", response_model=SensorResponse)
async def get_sensor(sensor_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single sensor."""
    query = select(Sensor).where(Sensor.id == sensor_id)
    result = await db.execute(query)
    sensor = result.scalar_one_or_none()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    return sensor


@router.post("/", response_model=SensorResponse, status_code=201)
async def create_sensor(sensor: SensorCreate, db: AsyncSession = Depends(get_db)):
    """Register a new sensor."""
    # Check for duplicate hardware_id
    existing = await db.execute(
        select(Sensor).where(Sensor.hardware_id == sensor.hardware_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Sensor with this hardware ID already exists")

    db_sensor = Sensor(**sensor.model_dump())
    db.add(db_sensor)
    await db.flush()
    await db.refresh(db_sensor)
    return db_sensor


@router.put("/{sensor_id}", response_model=SensorResponse)
async def update_sensor(sensor_id: int, sensor: SensorUpdate, db: AsyncSession = Depends(get_db)):
    """Update a sensor."""
    query = select(Sensor).where(Sensor.id == sensor_id)
    result = await db.execute(query)
    db_sensor = result.scalar_one_or_none()

    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    update_data = sensor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sensor, key, value)

    await db.flush()
    await db.refresh(db_sensor)
    return db_sensor


@router.post("/{sensor_id}/heartbeat", response_model=SensorResponse)
async def sensor_heartbeat(sensor_id: int, db: AsyncSession = Depends(get_db)):
    """Update sensor's last seen timestamp (called by ESP32)."""
    query = select(Sensor).where(Sensor.id == sensor_id)
    result = await db.execute(query)
    db_sensor = result.scalar_one_or_none()

    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    db_sensor.is_online = True
    db_sensor.last_seen_at = datetime.utcnow()

    await db.flush()
    await db.refresh(db_sensor)
    return db_sensor


@router.delete("/{sensor_id}", status_code=204)
async def delete_sensor(sensor_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a sensor."""
    query = select(Sensor).where(Sensor.id == sensor_id)
    result = await db.execute(query)
    db_sensor = result.scalar_one_or_none()

    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    await db.delete(db_sensor)


# ============ RFID Tags ============

@router.get("/rfid/tags", response_model=list[RfidTagResponse])
async def list_rfid_tags(
    zone: Optional[str] = Query(None),
    is_present: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all RFID tags."""
    query = select(RfidTag).options(selectinload(RfidTag.product))

    if zone:
        query = query.where(RfidTag.expected_zone == zone)
    if is_present is not None:
        query = query.where(RfidTag.is_present == is_present)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/rfid/tags", response_model=RfidTagResponse, status_code=201)
async def create_rfid_tag(tag: RfidTagCreate, db: AsyncSession = Depends(get_db)):
    """Register a new RFID tag."""
    existing = await db.execute(
        select(RfidTag).where(RfidTag.tag_id == tag.tag_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tag already registered")

    db_tag = RfidTag(**tag.model_dump())
    db.add(db_tag)
    await db.flush()
    await db.refresh(db_tag)
    return db_tag


@router.post("/rfid/event")
async def record_rfid_event(
    tag_id: str,
    sensor_id: int,
    event_type: str,
    zone: Optional[str] = None,
    rssi: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Record an RFID detection event (called by RFID reader)."""
    # Find the tag
    tag_query = await db.execute(select(RfidTag).where(RfidTag.tag_id == tag_id))
    tag = tag_query.scalar_one_or_none()

    if not tag:
        # Auto-create unknown tag
        tag = RfidTag(tag_id=tag_id, current_zone=zone)
        db.add(tag)
        await db.flush()

    # Update tag state
    tag.last_seen_at = datetime.utcnow()
    tag.current_zone = zone

    if event_type == "removed":
        tag.is_present = False
    elif event_type in ("detected", "returned"):
        tag.is_present = True

    # Log event
    event = RfidEvent(
        tag_id=tag.id,
        sensor_id=sensor_id,
        event_type=event_type,
        zone=zone,
        rssi=rssi
    )
    db.add(event)

    return {"status": "ok", "tag_id": tag.id, "event_type": event_type}


# ============ Camera Events ============

@router.get("/camera/events", response_model=list[CameraEventResponse])
async def list_camera_events(
    sensor_id: Optional[int] = Query(None),
    resolved: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """List camera detection events."""
    query = select(CameraEvent)

    if sensor_id:
        query = query.where(CameraEvent.sensor_id == sensor_id)
    if resolved is not None:
        query = query.where(CameraEvent.resolved == resolved)

    query = query.order_by(CameraEvent.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/camera/event", response_model=CameraEventResponse, status_code=201)
async def create_camera_event(event: CameraEventCreate, db: AsyncSession = Depends(get_db)):
    """Record a camera detection event (called by ESP32-CAM)."""
    db_event = CameraEvent(**event.model_dump())
    db.add(db_event)
    await db.flush()
    await db.refresh(db_event)
    return db_event


@router.post("/camera/events/{event_id}/resolve")
async def resolve_camera_event(
    event_id: int,
    product_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Resolve a camera event (user confirms what was detected)."""
    query = select(CameraEvent).where(CameraEvent.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.resolved = True
    event.resolved_at = datetime.utcnow()
    if product_id:
        event.product_id = product_id

    return {"status": "ok"}


# ============ Can Lanes ============

@router.get("/cans/lanes", response_model=list[CanLaneResponse])
async def list_can_lanes(db: AsyncSession = Depends(get_db)):
    """List all can rotation lanes."""
    query = select(CanLane).order_by(CanLane.sensor_id, CanLane.lane_number)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/cans/lanes", response_model=CanLaneResponse, status_code=201)
async def create_can_lane(lane: CanLaneCreate, db: AsyncSession = Depends(get_db)):
    """Create a can lane configuration."""
    db_lane = CanLane(**lane.model_dump())
    db.add(db_lane)
    await db.flush()
    await db.refresh(db_lane)
    return db_lane


@router.put("/cans/lanes/{lane_id}", response_model=CanLaneResponse)
async def update_can_lane(lane_id: int, lane: CanLaneUpdate, db: AsyncSession = Depends(get_db)):
    """Update a can lane."""
    query = select(CanLane).where(CanLane.id == lane_id)
    result = await db.execute(query)
    db_lane = result.scalar_one_or_none()

    if not db_lane:
        raise HTTPException(status_code=404, detail="Lane not found")

    update_data = lane.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lane, key, value)

    await db.flush()
    await db.refresh(db_lane)
    return db_lane


@router.post("/cans/event")
async def record_can_event(
    lane_id: int,
    event_type: str,  # 'in' or 'out'
    db: AsyncSession = Depends(get_db)
):
    """Record a can IN/OUT event (called by laser sensors)."""
    query = select(CanLane).where(CanLane.id == lane_id)
    result = await db.execute(query)
    lane = result.scalar_one_or_none()

    if not lane:
        raise HTTPException(status_code=404, detail="Lane not found")

    if event_type == "in":
        lane.current_count = min(lane.current_count + 1, lane.max_capacity)
    elif event_type == "out":
        lane.current_count = max(lane.current_count - 1, 0)
    else:
        raise HTTPException(status_code=400, detail="event_type must be 'in' or 'out'")

    # Log event
    event = CanEvent(
        lane_id=lane_id,
        event_type=event_type,
        count_after=lane.current_count
    )
    db.add(event)

    return {
        "status": "ok",
        "lane_id": lane_id,
        "event_type": event_type,
        "current_count": lane.current_count,
        "is_low": lane.current_count <= lane.low_stock_threshold
    }


@router.get("/cans/low-stock", response_model=list[CanLaneResponse])
async def get_low_stock_lanes(db: AsyncSession = Depends(get_db)):
    """Get can lanes that are low on stock."""
    query = select(CanLane).where(CanLane.current_count <= CanLane.low_stock_threshold)
    result = await db.execute(query)
    return result.scalars().all()
