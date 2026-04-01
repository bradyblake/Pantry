from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from pathlib import Path

from config import settings


class Base(DeclarativeBase):
    pass


# Ensure data directory exists
settings.database_path.parent.mkdir(parents=True, exist_ok=True)

# Create async engine
engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.database_path}",
    echo=False,
)

# Session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Dependency for getting database sessions."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Initialize database tables and seed default data."""
    # Import models to register them
    # Zone must be imported before Product due to FK relationship
    from models.zone import Zone
    from models.product import Product
    from models.freezer import Freezer
    from models.inventory import Inventory, InventoryLog
    from models.shopping import ShoppingItem
    from models.settings import Setting
    # Hardware/sensor models
    from models.sensor import Sensor, RfidTag, RfidEvent, CameraEvent, CanLane, CanEvent
    # Recipe models
    from models.recipe import Recipe, RecipeIngredient, RecipeDocument

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default freezer if none exists
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(Freezer))
        if not result.scalars().first():
            default_freezer = Freezer(
                name="Main Freezer",
                location="Kitchen",
                description="Primary kitchen freezer"
            )
            session.add(default_freezer)
            await session.commit()
