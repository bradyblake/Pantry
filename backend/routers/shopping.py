from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import Optional

from database import get_db
from models.shopping import ShoppingItem, ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse
from models.product import Product
from models.inventory import Inventory
from config import settings

router = APIRouter(prefix="/api/shopping", tags=["shopping"])


@router.get("/", response_model=list[ShoppingItemResponse])
async def list_shopping_items(
    checked: Optional[bool] = Query(None, description="Filter by checked status"),
    db: AsyncSession = Depends(get_db)
):
    """Get the shopping list."""
    query = select(ShoppingItem).options(selectinload(ShoppingItem.product))

    if checked is not None:
        query = query.where(ShoppingItem.checked == checked)

    # Unchecked first, then by created date
    query = query.order_by(ShoppingItem.checked.asc(), ShoppingItem.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{item_id}", response_model=ShoppingItemResponse)
async def get_shopping_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single shopping item."""
    query = select(ShoppingItem).options(
        selectinload(ShoppingItem.product)
    ).where(ShoppingItem.id == item_id)

    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Shopping item not found")

    return item


@router.post("/", response_model=ShoppingItemResponse, status_code=201)
async def create_shopping_item(
    item: ShoppingItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add an item to the shopping list."""
    # Validate product_id if provided
    if item.product_id:
        product_query = select(Product).where(Product.id == item.product_id)
        product_result = await db.execute(product_query)
        if not product_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Product not found")

    # Must have either product_id or custom_item_name
    if not item.product_id and not item.custom_item_name:
        raise HTTPException(
            status_code=400,
            detail="Must provide either product_id or custom_item_name"
        )

    db_item = ShoppingItem(**item.model_dump())
    db.add(db_item)
    await db.flush()

    # Reload with relationships
    reload_query = select(ShoppingItem).options(
        selectinload(ShoppingItem.product)
    ).where(ShoppingItem.id == db_item.id)
    result = await db.execute(reload_query)
    return result.scalar_one()


@router.put("/{item_id}", response_model=ShoppingItemResponse)
async def update_shopping_item(
    item_id: int,
    item: ShoppingItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a shopping item."""
    query = select(ShoppingItem).options(
        selectinload(ShoppingItem.product)
    ).where(ShoppingItem.id == item_id)

    result = await db.execute(query)
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Shopping item not found")

    update_data = item.model_dump(exclude_unset=True)

    # Validate product_id if being changed
    if "product_id" in update_data and update_data["product_id"]:
        product_query = select(Product).where(Product.id == update_data["product_id"])
        product_result = await db.execute(product_query)
        if not product_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Product not found")

    for key, value in update_data.items():
        setattr(db_item, key, value)

    await db.flush()
    await db.refresh(db_item)

    return db_item


@router.delete("/{item_id}", status_code=204)
async def delete_shopping_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Remove an item from the shopping list."""
    query = select(ShoppingItem).where(ShoppingItem.id == item_id)
    result = await db.execute(query)
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Shopping item not found")

    await db.delete(db_item)


@router.delete("/clear-checked", status_code=204)
async def clear_checked_items(db: AsyncSession = Depends(get_db)):
    """Remove all checked items from the shopping list."""
    await db.execute(delete(ShoppingItem).where(ShoppingItem.checked == True))


@router.post("/generate-from-low-stock", response_model=list[ShoppingItemResponse])
async def generate_from_low_stock(
    threshold: Optional[float] = Query(None, description="Custom threshold"),
    db: AsyncSession = Depends(get_db)
):
    """Auto-generate shopping list from low stock items."""
    threshold_value = threshold if threshold is not None else settings.low_stock_threshold

    # Get low stock items
    low_stock_query = select(Inventory).options(
        selectinload(Inventory.product)
    ).where(Inventory.quantity <= threshold_value)

    result = await db.execute(low_stock_query)
    low_stock_items = result.scalars().all()

    added_items = []

    for inv_item in low_stock_items:
        # Check if already in shopping list
        existing_query = select(ShoppingItem).where(
            ShoppingItem.product_id == inv_item.product_id,
            ShoppingItem.checked == False
        )
        existing_result = await db.execute(existing_query)

        if not existing_result.scalar_one_or_none():
            # Add to shopping list
            shopping_item = ShoppingItem(
                product_id=inv_item.product_id,
                quantity=inv_item.product.default_quantity,
                unit=inv_item.product.default_unit,
                added_reason="low_stock"
            )
            db.add(shopping_item)
            added_items.append(shopping_item)

    await db.flush()

    # Reload with relationships
    if added_items:
        item_ids = [item.id for item in added_items]
        reload_query = select(ShoppingItem).options(
            selectinload(ShoppingItem.product)
        ).where(ShoppingItem.id.in_(item_ids))
        result = await db.execute(reload_query)
        return result.scalars().all()

    return []
