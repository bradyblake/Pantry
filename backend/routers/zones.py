"""Zone management and LED control endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import json
import logging

from database import get_db
from models.zone import (
    Zone, ZoneCreate, ZoneUpdate, ZoneRead,
    LedCommand, LedState, IngredientLocation, InventoryEntry, FindIngredientsResponse
)
from models.product import Product
from models.inventory import Inventory
from models.recipe import Recipe, RecipeIngredient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/zones", tags=["zones"])


@router.get("/", response_model=List[ZoneRead])
async def list_zones(db: AsyncSession = Depends(get_db)):
    """List all zones."""
    result = await db.execute(
        select(Zone).order_by(Zone.display_order, Zone.id)
    )
    return result.scalars().all()


@router.get("/{zone_id}", response_model=ZoneRead)
async def get_zone(zone_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific zone."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.post("/", response_model=ZoneRead)
async def create_zone(zone: ZoneCreate, db: AsyncSession = Depends(get_db)):
    """Create a new zone."""
    db_zone = Zone(**zone.model_dump())
    db.add(db_zone)
    await db.flush()
    await db.refresh(db_zone)
    return db_zone


@router.put("/{zone_id}", response_model=ZoneRead)
async def update_zone(
    zone_id: int,
    zone_update: ZoneUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a zone."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    update_data = zone_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(zone, key, value)

    await db.flush()
    await db.refresh(zone)
    return zone


@router.delete("/{zone_id}")
async def delete_zone(zone_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a zone."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    await db.delete(zone)
    return {"status": "deleted", "zone_id": zone_id}


@router.post("/{zone_id}/led")
async def control_led(
    zone_id: int,
    command: LedCommand,
    db: AsyncSession = Depends(get_db)
):
    """
    Control the LED strip for a zone.

    This endpoint updates the zone's LED state in the database.
    The ESP32 devices poll for state changes or receive MQTT messages.
    """
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Update zone LED state
    zone.current_led_state = command.state.value

    # Map states to colors
    color_map = {
        LedState.OFF: "#000000",
        LedState.IDLE: "#333333",
        LedState.SCANNING: "#FF0000",
        LedState.CONFIRM: "#FFFF00",
        LedState.SUCCESS: "#00FF00",
        LedState.RETURN_HERE: "#0000FF",
        LedState.ADD_MODE: "#0066FF",
        LedState.HIGHLIGHT: "#FFFFFF",
    }

    zone.led_color = command.color or color_map.get(command.state, "#FFFFFF")

    await db.flush()

    # TODO: Send MQTT message to ESP32
    # For now, ESP32s will poll /api/zones/{id} for state changes
    logger.info(f"Zone {zone_id} LED set to {command.state.value} ({zone.led_color})")

    return {
        "zone_id": zone_id,
        "state": command.state.value,
        "color": zone.led_color,
        "duration_ms": command.duration_ms,
        "pulse": command.pulse
    }


@router.post("/led/batch")
async def control_leds_batch(
    zone_commands: dict[int, LedCommand],
    db: AsyncSession = Depends(get_db)
):
    """Control LEDs for multiple zones at once."""
    results = []
    for zone_id, command in zone_commands.items():
        result = await db.execute(select(Zone).where(Zone.id == zone_id))
        zone = result.scalar_one_or_none()
        if zone:
            zone.current_led_state = command.state.value
            results.append({"zone_id": zone_id, "state": command.state.value})

    await db.flush()
    return {"updated": results}


@router.post("/led/all-off")
async def all_leds_off(db: AsyncSession = Depends(get_db)):
    """Turn off all zone LEDs."""
    result = await db.execute(select(Zone))
    zones = result.scalars().all()

    for zone in zones:
        zone.current_led_state = LedState.OFF.value
        zone.led_color = "#000000"

    await db.flush()
    return {"status": "all_off", "zones_updated": len(zones)}


@router.get("/{zone_id}/products")
async def get_zone_products(zone_id: int, db: AsyncSession = Depends(get_db)):
    """Get all products assigned to a zone."""
    result = await db.execute(
        select(Product).where(Product.home_zone_id == zone_id)
    )
    products = result.scalars().all()
    return products


# ==================== INGREDIENT FINDER ====================


@router.post("/find-ingredients/{recipe_id}", response_model=FindIngredientsResponse)
async def find_ingredients(
    recipe_id: int,
    light_zones: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Find ingredient locations for a recipe and optionally light up zones.

    This powers the "ingredient finder" feature - user says "find ingredients for tacos"
    and the system lights up the zones where each ingredient is located.
    """
    # Get recipe with ingredients
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Get recipe ingredients
    result = await db.execute(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
    )
    ingredients = result.scalars().all()

    ingredient_locations = []
    zones_to_light = set()
    missing_ingredients = []

    for ing in ingredients:
        location = IngredientLocation(
            ingredient_text=ing.ingredient_text,
            product_id=ing.product_id,
            product_name=None,
            zone_id=None,
            zone_name=None,
            zone_location=None,
            in_stock=False,
            quantity_available=0
        )

        if ing.product_id:
            # Get product info including home zone
            product_result = await db.execute(
                select(Product).where(Product.id == ing.product_id)
            )
            product = product_result.scalar_one_or_none()

            if product:
                location.product_name = product.name

                # Get home zone
                if product.home_zone_id:
                    zone_result = await db.execute(
                        select(Zone).where(Zone.id == product.home_zone_id)
                    )
                    zone = zone_result.scalar_one_or_none()
                    if zone:
                        location.zone_id = zone.id
                        location.zone_name = zone.name
                        location.zone_location = zone.location
                        zones_to_light.add(zone.id)

                # Check inventory and collect entry details
                inv_result = await db.execute(
                    select(Inventory).where(Inventory.product_id == product.id)
                )
                inv_items = inv_result.scalars().all()
                total_qty = sum(item.quantity for item in inv_items)
                location.quantity_available = total_qty
                location.in_stock = total_qty > 0
                location.inventory_entries = [
                    InventoryEntry(
                        quantity=item.quantity,
                        location=item.location,
                        container_description=item.container_description,
                        freezer_name=item.freezer.name if item.freezer else None
                    )
                    for item in inv_items if item.quantity > 0
                ]

        if not location.in_stock:
            missing_ingredients.append(ing.ingredient_text)

        ingredient_locations.append(location)

    # Light up the zones
    if light_zones and zones_to_light:
        for zone_id in zones_to_light:
            zone_result = await db.execute(select(Zone).where(Zone.id == zone_id))
            zone = zone_result.scalar_one_or_none()
            if zone:
                zone.current_led_state = LedState.HIGHLIGHT.value
                zone.led_color = "#FFFFFF"

        await db.flush()
        logger.info(f"Lit up zones for recipe {recipe_id}: {zones_to_light}")

    # Build message
    found_count = len([loc for loc in ingredient_locations if loc.zone_id])
    total_count = len(ingredient_locations)

    if found_count == 0:
        message = "No ingredient locations found. Add home zones to products."
    elif missing_ingredients:
        message = f"Found {found_count} of {total_count} ingredients. Missing: {', '.join(missing_ingredients[:3])}"
        if len(missing_ingredients) > 3:
            message += f" and {len(missing_ingredients) - 3} more"
    else:
        message = f"All {total_count} ingredients found! Zones are lit."

    return FindIngredientsResponse(
        recipe_id=recipe_id,
        recipe_name=recipe.name,
        ingredients=ingredient_locations,
        zones_to_light=list(zones_to_light),
        missing_ingredients=missing_ingredients,
        message=message
    )


@router.post("/find-products")
async def find_products(
    product_ids: List[int],
    light_zones: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Find locations for specific products and light up their zones.
    Useful for "where is the taco seasoning?" type queries.
    """
    zones_to_light = set()
    product_locations = []

    for product_id in product_ids:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()

        if product and product.home_zone_id:
            zone_result = await db.execute(
                select(Zone).where(Zone.id == product.home_zone_id)
            )
            zone = zone_result.scalar_one_or_none()

            if zone:
                zones_to_light.add(zone.id)
                product_locations.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "zone_id": zone.id,
                    "zone_name": zone.name,
                    "zone_location": zone.location
                })

    # Light up zones
    if light_zones and zones_to_light:
        for zone_id in zones_to_light:
            zone_result = await db.execute(select(Zone).where(Zone.id == zone_id))
            zone = zone_result.scalar_one_or_none()
            if zone:
                zone.current_led_state = LedState.HIGHLIGHT.value
                zone.led_color = "#FFFFFF"

        await db.flush()

    return {
        "products": product_locations,
        "zones_lit": list(zones_to_light)
    }
