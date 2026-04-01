from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import Optional

from database import get_db
from models.product import Product, ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    search: Optional[str] = Query(None, description="Search by name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db)
):
    """List all products with optional search and filter."""
    query = select(Product).options(selectinload(Product.home_zone))

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    if category:
        query = query.where(Product.category == category)

    query = query.order_by(Product.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/categories", response_model=list[str])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get list of all categories in use."""
    query = select(Product.category).where(Product.category.isnot(None)).distinct()
    result = await db.execute(query)
    categories = [row[0] for row in result.all() if row[0]]
    return sorted(categories)


@router.get("/barcode/{barcode}", response_model=ProductResponse)
async def get_product_by_barcode(barcode: str, db: AsyncSession = Depends(get_db)):
    """Lookup product by barcode."""
    query = select(Product).options(selectinload(Product.home_zone)).where(Product.barcode == barcode)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single product by ID."""
    query = select(Product).options(selectinload(Product.home_zone)).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Create a new product."""
    # Check for duplicate barcode if provided
    if product.barcode:
        existing = await db.execute(
            select(Product).where(Product.barcode == product.barcode)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Product with this barcode already exists")

    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.flush()

    # Reload with relationships
    reload_query = select(Product).options(selectinload(Product.home_zone)).where(Product.id == db_product.id)
    result = await db.execute(reload_query)
    return result.scalar_one()


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a product."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check for duplicate barcode if being changed
    update_data = product.model_dump(exclude_unset=True)
    if "barcode" in update_data and update_data["barcode"]:
        existing = await db.execute(
            select(Product).where(
                Product.barcode == update_data["barcode"],
                Product.id != product_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Product with this barcode already exists")

    for key, value in update_data.items():
        setattr(db_product, key, value)

    await db.flush()

    # Reload with relationships
    reload_query = select(Product).options(selectinload(Product.home_zone)).where(Product.id == product_id)
    result = await db.execute(reload_query)
    return result.scalar_one()


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a product."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(db_product)
