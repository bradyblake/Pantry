from .products import router as products_router
from .inventory import router as inventory_router
from .freezers import router as freezers_router
from .shopping import router as shopping_router
from .sensors import router as sensors_router
from .recipes import router as recipes_router
from .zones import router as zones_router
from .rfid import router as rfid_router

__all__ = [
    "products_router",
    "inventory_router",
    "freezers_router",
    "shopping_router",
    "sensors_router",
    "recipes_router",
    "zones_router",
    "rfid_router"
]
