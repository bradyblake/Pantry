from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import date

from database import get_db
from models.inventory import (
    Inventory, InventoryLog, InventoryAdd, InventoryUse, InventoryUpdate,
    InventoryResponse, InventoryLogResponse
)
from models.product import Product
from config import settings

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("/", response_model=list[InventoryResponse])
async def list_inventory(
    location: Optional[str] = Query(None, description="Filter by location (pantry, fridge, freezer)"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    db: AsyncSession = Depends(get_db)
):
    """Get current inventory state."""
    query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    )

    if location:
        query = query.where(Inventory.location == location)

    if category:
        query = query.join(Product).where(Product.category == category)

    query = query.order_by(Inventory.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/low-stock", response_model=list[InventoryResponse])
async def get_low_stock(
    threshold: Optional[float] = Query(None, description="Custom threshold"),
    db: AsyncSession = Depends(get_db)
):
    """Get items below low stock threshold."""
    threshold_value = threshold if threshold is not None else settings.low_stock_threshold

    query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    ).where(Inventory.quantity <= threshold_value)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/product/{product_id}", response_model=list[InventoryResponse])
async def get_inventory_for_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get all inventory entries for a specific product."""
    query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    ).where(Inventory.product_id == product_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/log", response_model=list[InventoryLogResponse])
async def get_inventory_log(
    product_id: Optional[int] = Query(None, description="Filter by product"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get inventory change history."""
    query = select(InventoryLog).options(selectinload(InventoryLog.product))

    if product_id:
        query = query.where(InventoryLog.product_id == product_id)

    if source:
        query = query.where(InventoryLog.source == source)

    query = query.order_by(InventoryLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/add", response_model=InventoryResponse, status_code=201)
async def add_stock(data: InventoryAdd, db: AsyncSession = Depends(get_db)):
    """Add stock to inventory."""
    # Verify product exists
    product_query = select(Product).where(Product.id == data.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Find existing inventory entry for this product/location/freezer combo
    inv_query = select(Inventory).where(
        Inventory.product_id == data.product_id,
        Inventory.location == data.location
    )

    if data.freezer_id:
        inv_query = inv_query.where(Inventory.freezer_id == data.freezer_id)
    else:
        inv_query = inv_query.where(Inventory.freezer_id.is_(None))

    result = await db.execute(inv_query)
    inventory = result.scalar_one_or_none()

    if inventory:
        # Update existing entry
        inventory.quantity += data.quantity
        if data.expiration_date:
            inventory.expiration_date = data.expiration_date
        if data.frozen_date:
            inventory.frozen_date = data.frozen_date
        if data.freeze_by_date:
            inventory.freeze_by_date = data.freeze_by_date
        if data.container_description:
            inventory.container_description = data.container_description
    else:
        # Create new inventory entry
        inventory = Inventory(
            product_id=data.product_id,
            quantity=data.quantity,
            location=data.location,
            expiration_date=data.expiration_date,
            freezer_id=data.freezer_id,
            frozen_date=data.frozen_date or (date.today() if data.freezer_id else None),
            freeze_by_date=data.freeze_by_date,
            container_description=data.container_description
        )
        db.add(inventory)

    # Log the change
    log_entry = InventoryLog(
        product_id=data.product_id,
        quantity_change=data.quantity,
        source="manual",
        notes=data.notes
    )
    db.add(log_entry)

    await db.flush()

    # Reload with relationships
    await db.refresh(inventory)
    reload_query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    ).where(Inventory.id == inventory.id)
    result = await db.execute(reload_query)
    return result.scalar_one()


@router.post("/use", response_model=InventoryResponse)
async def use_stock(data: InventoryUse, db: AsyncSession = Depends(get_db)):
    """Use/remove stock from inventory."""
    # Find inventory entry with the most stock for this product
    inv_query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    ).where(
        Inventory.product_id == data.product_id,
        Inventory.quantity > 0
    ).order_by(Inventory.quantity.desc())

    result = await db.execute(inv_query)
    inventory = result.scalar_one_or_none()

    if not inventory:
        raise HTTPException(status_code=404, detail="No inventory found for this product")

    # Reduce quantity
    inventory.quantity = max(0, inventory.quantity - data.quantity)

    # Log the change
    log_entry = InventoryLog(
        product_id=data.product_id,
        quantity_change=-data.quantity,
        source="manual",
        notes=data.notes
    )
    db.add(log_entry)

    await db.flush()
    await db.refresh(inventory)

    return inventory


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: int,
    data: InventoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an inventory entry."""
    query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    ).where(Inventory.id == inventory_id)

    result = await db.execute(query)
    inventory = result.scalar_one_or_none()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory entry not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inventory, key, value)

    await db.flush()
    await db.refresh(inventory)

    return inventory


@router.delete("/{inventory_id}", status_code=204)
async def delete_inventory(inventory_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an inventory entry."""
    query = select(Inventory).where(Inventory.id == inventory_id)
    result = await db.execute(query)
    inventory = result.scalar_one_or_none()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory entry not found")

    await db.delete(inventory)
