from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import settings
from database import init_db
from routers import (
    products_router, inventory_router, freezers_router,
    shopping_router, sensors_router, recipes_router,
    zones_router, rfid_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="PantryPal API",
    description="Smart Pantry Inventory Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(freezers_router)
app.include_router(shopping_router)
app.include_router(sensors_router)
app.include_router(recipes_router)
app.include_router(zones_router)
app.include_router(rfid_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/categories")
async def get_default_categories():
    """Get the default product categories."""
    return settings.default_categories


# Serve frontend static files in production
frontend_dist = Path(__file__).parent.parent / "frontend" / "build"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
