"""RFID tracking and "put it back" feature endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from database import get_db
from models.sensor import (
    RfidTag, RfidEvent, Sensor,
    RfidTagCreate, RfidTagUpdate, RfidTagResponse,
    RfidEventCreate, RfidEventResponse, PutItBackAlert
)
from models.zone import Zone, LedState
from models.product import Product

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rfid", tags=["rfid"])


# ==================== RFID TAG MANAGEMENT ====================


@router.get("/tags", response_model=List[RfidTagResponse])
async def list_tags(
    is_out: Optional[bool] = None,
    zone_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all RFID tags, optionally filtered."""
    query = select(RfidTag)

    if is_out is not None:
        query = query.where(RfidTag.is_out == is_out)
    if zone_id is not None:
        query = query.where(RfidTag.home_zone_id == zone_id)

    result = await db.execute(query.order_by(RfidTag.id))
    return result.scalars().all()


@router.get("/tags/{tag_id}", response_model=RfidTagResponse)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific RFID tag."""
    result = await db.execute(select(RfidTag).where(RfidTag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/tags/by-epc/{epc}")
async def get_tag_by_epc(epc: str, db: AsyncSession = Depends(get_db)):
    """Look up tag by EPC/UID."""
    result = await db.execute(select(RfidTag).where(RfidTag.tag_id == epc))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/tags", response_model=RfidTagResponse)
async def create_tag(tag: RfidTagCreate, db: AsyncSession = Depends(get_db)):
    """Register a new RFID tag."""
    # Check if tag already exists
    existing = await db.execute(
        select(RfidTag).where(RfidTag.tag_id == tag.tag_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tag ID already registered")

    db_tag = RfidTag(
        tag_id=tag.tag_id,
        product_id=tag.product_id,
        container_name=tag.container_name,
        home_zone_id=tag.home_zone_id,
        current_zone_id=tag.home_zone_id,  # Start at home
        is_present=True,
        is_out=False
    )
    db.add(db_tag)
    await db.flush()
    await db.refresh(db_tag)
    return db_tag


@router.put("/tags/{tag_id}", response_model=RfidTagResponse)
async def update_tag(
    tag_id: int,
    tag_update: RfidTagUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an RFID tag."""
    result = await db.execute(select(RfidTag).where(RfidTag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    update_data = tag_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)

    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an RFID tag."""
    result = await db.execute(select(RfidTag).where(RfidTag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await db.delete(tag)
    return {"status": "deleted", "tag_id": tag_id}


# ==================== RFID EVENTS (from hardware) ====================


@router.post("/events/detected")
async def tag_detected(
    epc: str,
    antenna_id: int,
    rssi: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Called when RFID reader detects a tag.
    This is the main entry point from the RFID hardware.
    """
    # Find the tag
    result = await db.execute(select(RfidTag).where(RfidTag.tag_id == epc))
    tag = result.scalar_one_or_none()

    if not tag:
        # Unknown tag - could auto-register or return error
        logger.warning(f"Unknown RFID tag detected: {epc}")
        return {"status": "unknown_tag", "epc": epc}

    # Find which zone this antenna covers
    zone_result = await db.execute(
        select(Zone).where(Zone.rfid_antenna_id == antenna_id)
    )
    detected_zone = zone_result.scalar_one_or_none()
    detected_zone_id = detected_zone.id if detected_zone else None

    # Update tag state
    tag.last_seen_at = datetime.utcnow()

    # Determine event type based on current state
    if tag.is_out:
        # Item was out, now detected - it's being returned
        if detected_zone_id == tag.home_zone_id:
            # Returned to correct zone
            event_type = "returned_correct"
            tag.is_out = False
            tag.is_present = True
            tag.current_zone_id = detected_zone_id
            tag.removed_at = None

            # Set LED to green (success)
            if detected_zone:
                detected_zone.current_led_state = LedState.SUCCESS.value
                detected_zone.led_color = "#00FF00"

            logger.info(f"Tag {epc} returned to correct zone {detected_zone_id}")
        else:
            # Returned to wrong zone
            event_type = "returned_wrong"
            tag.current_zone_id = detected_zone_id

            # Set current zone yellow, home zone blue
            if detected_zone:
                detected_zone.current_led_state = LedState.CONFIRM.value
                detected_zone.led_color = "#FFFF00"

            if tag.home_zone_id:
                home_zone_result = await db.execute(
                    select(Zone).where(Zone.id == tag.home_zone_id)
                )
                home_zone = home_zone_result.scalar_one_or_none()
                if home_zone:
                    home_zone.current_led_state = LedState.RETURN_HERE.value
                    home_zone.led_color = "#0000FF"

            logger.info(f"Tag {epc} returned to wrong zone {detected_zone_id}, should be {tag.home_zone_id}")
    else:
        # Item was present, still detected - just a periodic read
        event_type = "detected"
        tag.current_zone_id = detected_zone_id

    # Log event
    event = RfidEvent(
        tag_id=tag.id,
        event_type=event_type,
        from_zone_id=tag.current_zone_id if event_type == "detected" else None,
        to_zone_id=detected_zone_id,
        rssi=rssi
    )
    db.add(event)
    await db.flush()

    return {
        "status": event_type,
        "tag_id": tag.id,
        "epc": epc,
        "zone_id": detected_zone_id,
        "is_home": detected_zone_id == tag.home_zone_id
    }


@router.post("/events/removed")
async def tag_removed(
    epc: str,
    antenna_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Called when a tag is no longer detected (item removed from zone).
    The RFID reader should call this after a tag stops being read for X seconds.
    """
    result = await db.execute(select(RfidTag).where(RfidTag.tag_id == epc))
    tag = result.scalar_one_or_none()

    if not tag:
        return {"status": "unknown_tag", "epc": epc}

    # Find zone
    zone_result = await db.execute(
        select(Zone).where(Zone.rfid_antenna_id == antenna_id)
    )
    zone = zone_result.scalar_one_or_none()

    # Mark as removed
    tag.is_out = True
    tag.is_present = False
    tag.removed_at = datetime.utcnow()

    # Set zone LED to scanning/red
    if zone:
        zone.current_led_state = LedState.SCANNING.value
        zone.led_color = "#FF0000"

    # Log event
    event = RfidEvent(
        tag_id=tag.id,
        event_type="removed",
        from_zone_id=tag.home_zone_id
    )
    db.add(event)
    await db.flush()

    logger.info(f"Tag {epc} removed from zone {zone.id if zone else 'unknown'}")

    return {
        "status": "removed",
        "tag_id": tag.id,
        "epc": epc,
        "product_name": tag.product.name if tag.product else tag.container_name,
        "home_zone_id": tag.home_zone_id
    }


# ==================== PUT IT BACK FEATURE ====================


@router.get("/out", response_model=List[PutItBackAlert])
async def get_items_out(
    minutes_threshold: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all items currently removed from their home zones.
    Used for "put it back" alerts on the UI.
    """
    query = select(RfidTag).where(RfidTag.is_out == True)

    if minutes_threshold > 0:
        threshold_time = datetime.utcnow() - timedelta(minutes=minutes_threshold)
        query = query.where(RfidTag.removed_at <= threshold_time)

    result = await db.execute(query)
    tags = result.scalars().all()

    alerts = []
    for tag in tags:
        # Get zone info
        home_zone_name = "Unknown"
        home_zone_location = None
        if tag.home_zone_id:
            zone_result = await db.execute(
                select(Zone).where(Zone.id == tag.home_zone_id)
            )
            zone = zone_result.scalar_one_or_none()
            if zone:
                home_zone_name = zone.name
                home_zone_location = zone.location

        current_zone_name = None
        if tag.current_zone_id and tag.current_zone_id != tag.home_zone_id:
            zone_result = await db.execute(
                select(Zone).where(Zone.id == tag.current_zone_id)
            )
            zone = zone_result.scalar_one_or_none()
            if zone:
                current_zone_name = zone.name

        # Calculate minutes out
        minutes_out = 0
        if tag.removed_at:
            delta = datetime.utcnow() - tag.removed_at
            minutes_out = int(delta.total_seconds() / 60)

        alerts.append(PutItBackAlert(
            tag_id=tag.id,
            tag_epc=tag.tag_id,
            product_name=tag.product.name if tag.product else None,
            container_name=tag.container_name,
            home_zone_id=tag.home_zone_id,
            home_zone_name=home_zone_name,
            home_zone_location=home_zone_location,
            current_zone_id=tag.current_zone_id,
            current_zone_name=current_zone_name,
            removed_at=tag.removed_at,
            minutes_out=minutes_out
        ))

    return alerts


@router.post("/guide-return/{tag_id}")
async def guide_return(tag_id: int, db: AsyncSession = Depends(get_db)):
    """
    Activate LEDs to guide user to return an item to its home zone.
    Pulses blue at the home zone.
    """
    result = await db.execute(select(RfidTag).where(RfidTag.id == tag_id))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if not tag.home_zone_id:
        raise HTTPException(status_code=400, detail="Tag has no home zone assigned")

    # Light up home zone blue/pulsing
    zone_result = await db.execute(
        select(Zone).where(Zone.id == tag.home_zone_id)
    )
    zone = zone_result.scalar_one_or_none()

    if zone:
        zone.current_led_state = LedState.RETURN_HERE.value
        zone.led_color = "#0000FF"
        await db.flush()

    return {
        "status": "guiding",
        "tag_id": tag_id,
        "home_zone_id": tag.home_zone_id,
        "home_zone_name": zone.name if zone else None,
        "led_state": "return_here"
    }


@router.post("/acknowledge-return/{tag_id}")
async def acknowledge_return(tag_id: int, db: AsyncSession = Depends(get_db)):
    """
    Manually acknowledge that an item was returned.
    Used when RFID doesn't detect the return automatically.
    """
    result = await db.execute(select(RfidTag).where(RfidTag.id == tag_id))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.is_out = False
    tag.is_present = True
    tag.current_zone_id = tag.home_zone_id
    tag.removed_at = None

    # Log event
    event = RfidEvent(
        tag_id=tag.id,
        event_type="returned_correct",
        to_zone_id=tag.home_zone_id
    )
    db.add(event)

    # Set LED to success green briefly
    if tag.home_zone_id:
        zone_result = await db.execute(
            select(Zone).where(Zone.id == tag.home_zone_id)
        )
        zone = zone_result.scalar_one_or_none()
        if zone:
            zone.current_led_state = LedState.SUCCESS.value
            zone.led_color = "#00FF00"

    await db.flush()

    return {"status": "acknowledged", "tag_id": tag_id}


# ==================== EVENT HISTORY ====================


@router.get("/events", response_model=List[RfidEventResponse])
async def list_events(
    tag_id: Optional[int] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get RFID event history."""
    query = select(RfidEvent)

    if tag_id:
        query = query.where(RfidEvent.tag_id == tag_id)
    if event_type:
        query = query.where(RfidEvent.event_type == event_type)

    query = query.order_by(RfidEvent.created_at.desc()).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
