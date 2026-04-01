from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import date, timedelta

from database import get_db
from models.freezer import Freezer, FreezerCreate, FreezerUpdate, FreezerResponse
from models.inventory import Inventory, InventoryResponse

router = APIRouter(prefix="/api/freezers", tags=["freezers"])


@router.get("/", response_model=list[FreezerResponse])
async def list_freezers(db: AsyncSession = Depends(get_db)):
    """List all freezers."""
    query = select(Freezer).order_by(Freezer.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/oldest", response_model=list[InventoryResponse])
async def get_oldest_frozen_items(
    freezer_id: Optional[int] = Query(None, description="Filter by freezer"),
    days: int = Query(90, description="Items frozen longer than this many days"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get items frozen longest (candidates for use-soon)."""
    cutoff_date = date.today() - timedelta(days=days)

    query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    ).where(
        Inventory.location == "freezer",
        Inventory.frozen_date.isnot(None),
        Inventory.frozen_date <= cutoff_date,
        Inventory.quantity > 0
    )

    if freezer_id:
        query = query.where(Inventory.freezer_id == freezer_id)

    query = query.order_by(Inventory.frozen_date.asc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{freezer_id}", response_model=FreezerResponse)
async def get_freezer(freezer_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single freezer by ID."""
    query = select(Freezer).where(Freezer.id == freezer_id)
    result = await db.execute(query)
    freezer = result.scalar_one_or_none()

    if not freezer:
        raise HTTPException(status_code=404, detail="Freezer not found")

    return freezer


@router.get("/{freezer_id}/contents", response_model=list[InventoryResponse])
async def get_freezer_contents(
    freezer_id: int,
    category: Optional[str] = Query(None, description="Filter by product category"),
    db: AsyncSession = Depends(get_db)
):
    """Get all items in a specific freezer."""
    # Verify freezer exists
    freezer_query = select(Freezer).where(Freezer.id == freezer_id)
    freezer_result = await db.execute(freezer_query)
    if not freezer_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Freezer not found")

    query = select(Inventory).options(
        selectinload(Inventory.product),
        selectinload(Inventory.freezer)
    ).where(
        Inventory.freezer_id == freezer_id,
        Inventory.quantity > 0
    )

    if category:
        from models.product import Product
        query = query.join(Product).where(Product.category == category)

    query = query.order_by(Inventory.frozen_date.asc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=FreezerResponse, status_code=201)
async def create_freezer(freezer: FreezerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new freezer."""
    db_freezer = Freezer(**freezer.model_dump())
    db.add(db_freezer)
    await db.flush()
    await db.refresh(db_freezer)
    return db_freezer


@router.put("/{freezer_id}", response_model=FreezerResponse)
async def update_freezer(
    freezer_id: int,
    freezer: FreezerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a freezer."""
    query = select(Freezer).where(Freezer.id == freezer_id)
    result = await db.execute(query)
    db_freezer = result.scalar_one_or_none()

    if not db_freezer:
        raise HTTPException(status_code=404, detail="Freezer not found")

    update_data = freezer.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_freezer, key, value)

    await db.flush()
    await db.refresh(db_freezer)
    return db_freezer


@router.delete("/{freezer_id}", status_code=204)
async def delete_freezer(freezer_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a freezer."""
    query = select(Freezer).where(Freezer.id == freezer_id)
    result = await db.execute(query)
    db_freezer = result.scalar_one_or_none()

    if not db_freezer:
        raise HTTPException(status_code=404, detail="Freezer not found")

    # Check if freezer has items
    items_query = select(Inventory).where(Inventory.freezer_id == freezer_id)
    items_result = await db.execute(items_query)
    if items_result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete freezer with items. Remove or move items first."
        )

    await db.delete(db_freezer)
