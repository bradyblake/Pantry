"""Seed the database with sample data for testing."""
import asyncio
import random
from datetime import datetime, timedelta
from database import async_session, init_db
from models.zone import Zone
from models.product import Product
from models.freezer import Freezer
from models.inventory import Inventory
from models.sensor import RfidTag

# Sample products by category
PRODUCTS = {
    "Canned Goods": [
        "Diced Tomatoes", "Black Beans", "Kidney Beans", "Chickpeas", "Corn",
        "Green Beans", "Chicken Broth", "Beef Broth", "Vegetable Broth", "Tomato Sauce",
        "Tomato Paste", "Coconut Milk", "Cream of Mushroom Soup", "Tuna", "Salmon"
    ],
    "Cereals & Breakfast": [
        "Cheerios", "Frosted Flakes", "Oatmeal", "Granola", "Corn Flakes",
        "Raisin Bran", "Pancake Mix", "Maple Syrup"
    ],
    "Snacks": [
        "Goldfish Crackers", "Cheez-Its", "Pretzels", "Tortilla Chips", "Potato Chips",
        "Popcorn", "Graham Crackers", "Animal Crackers"
    ],
    "Baking & Cooking": [
        "All-Purpose Flour", "Sugar", "Brown Sugar", "Baking Soda", "Baking Powder",
        "Vanilla Extract", "Vegetable Oil", "Olive Oil", "Cooking Spray"
    ],
    "Condiments & Sauces": [
        "Ketchup", "Mustard", "Mayonnaise", "Ranch Dressing", "Italian Dressing",
        "Soy Sauce", "Hot Sauce", "BBQ Sauce", "Salsa", "Pasta Sauce"
    ],
    "Pasta & Grains": [
        "Spaghetti", "Penne", "Macaroni", "Rice", "Brown Rice",
        "Quinoa", "Egg Noodles", "Ramen Noodles"
    ],
    "Seasonings & Spices": [
        "Salt", "Black Pepper", "Garlic Powder", "Onion Powder", "Italian Seasoning",
        "Taco Seasoning", "Chili Powder", "Cumin", "Paprika", "Cinnamon"
    ],
    "Beverages": [
        "Coffee", "Tea Bags", "Hot Cocoa Mix", "Juice Boxes", "Lemonade Mix"
    ],
}

FREEZER_ITEMS = {
    "Meat & Protein": [
        ("Ground Beef", "lb"), ("Chicken Breasts", "lb"), ("Chicken Thighs", "lb"),
        ("Pork Chops", "lb"), ("Bacon", "pack"), ("Italian Sausage", "lb"),
        ("Breakfast Sausage", "pack"), ("Salmon Fillets", "lb"), ("Tilapia", "lb"),
        ("Shrimp", "lb"), ("Hot Dogs", "pack"), ("Hamburger Patties", "pack"),
        ("Steak", "lb"), ("Pork Tenderloin", "lb"), ("Turkey Breast", "lb")
    ],
    "Frozen Vegetables": [
        ("Frozen Corn", "bag"), ("Frozen Peas", "bag"), ("Frozen Broccoli", "bag"),
        ("Frozen Mixed Vegetables", "bag"), ("Frozen Green Beans", "bag"),
        ("Frozen Spinach", "bag"), ("Frozen Stir Fry Mix", "bag")
    ],
    "Frozen Prepared": [
        ("Frozen Pizza", "box"), ("Chicken Nuggets", "bag"), ("Fish Sticks", "box"),
        ("Frozen Burritos", "pack"), ("Frozen Waffles", "box"), ("Ice Cream", "container"),
        ("Frozen Fruit", "bag"), ("Frozen Berries", "bag"), ("Pie Crust", "pack")
    ],
    "Leftovers": [
        ("Leftover Chili", "container"), ("Leftover Soup", "container"),
        ("Leftover Pasta Sauce", "container"), ("Leftover Casserole", "container")
    ]
}

FREEZER_NAMES = [
    ("Kitchen Freezer", "Kitchen", "Main freezer above the fridge"),
    ("Garage Freezer", "Garage", "Chest freezer in the garage"),
    ("Basement Freezer", "Basement", "Upright freezer in basement"),
]

# Zones matching V4 spec
ZONES = [
    {"name": "V1 Shelf 1 - Bulk", "location": "V1 Shelf 1", "zone_type": "bulk", "rfid_antenna_id": 1, "esp32_id": "esp32_v1_1"},
    {"name": "V1 Shelf 2", "location": "V1 Shelf 2", "zone_type": "shelf", "esp32_id": "esp32_v1_2"},
    {"name": "V1 Shelf 3", "location": "V1 Shelf 3", "zone_type": "shelf", "esp32_id": "esp32_v1_3"},
    {"name": "V2 Shelf 1", "location": "V2 Shelf 1", "zone_type": "shelf", "esp32_id": "esp32_v2_1"},
    {"name": "V2 Shelf 2 - Cans", "location": "V2 Shelf 2", "zone_type": "can_lane", "esp32_id": "esp32_v2_2"},
    {"name": "V2 Shelf 3", "location": "V2 Shelf 3", "zone_type": "shelf", "esp32_id": "esp32_v2_3"},
    {"name": "V3 Spice Tower", "location": "V3 Spice Tower", "zone_type": "spice", "rfid_antenna_id": 2, "esp32_id": "esp32_v3_spice"},
    {"name": "V3 Pouch Bin", "location": "V3 Pouch Bin", "zone_type": "pouch", "esp32_id": "esp32_v3_pouch"},
]

# Which categories go in which zones
CATEGORY_ZONES = {
    "Canned Goods": "V2 Shelf 2 - Cans",
    "Cereals & Breakfast": "V1 Shelf 2",
    "Snacks": "V1 Shelf 3",
    "Baking & Cooking": "V1 Shelf 1 - Bulk",  # Flour, sugar, etc
    "Condiments & Sauces": "V2 Shelf 1",
    "Pasta & Grains": "V2 Shelf 3",
    "Seasonings & Spices": "V3 Spice Tower",
    "Beverages": "V1 Shelf 2",
}

# Products that get RFID tags (bulk containers and snacks)
RFID_PRODUCTS = [
    "All-Purpose Flour", "Sugar", "Brown Sugar", "Rice", "Brown Rice",
    "Goldfish Crackers", "Cheez-Its", "Pretzels", "Tortilla Chips", "Potato Chips",
    "Salt", "Black Pepper", "Garlic Powder", "Onion Powder", "Italian Seasoning",
    "Taco Seasoning", "Chili Powder", "Cumin", "Paprika", "Cinnamon"
]

CONTAINER_DESCRIPTIONS = [
    "Red lid container", "Blue lid container", "Glass container",
    "Freezer bag", "Foil wrapped", "Plastic wrap", "Vacuum sealed",
    "Original packaging", "Ziploc bag", "Tupperware"
]


async def seed_database():
    """Seed the database with sample data."""
    await init_db()

    async with async_session() as session:
        # Check if already seeded
        from sqlalchemy import select, func
        product_count = await session.scalar(select(func.count(Product.id)))
        if product_count > 10:
            print(f"Database already has {product_count} products. Skipping seed.")
            return

        print("Seeding database...")

        # Create zones first
        zone_map = {}  # name -> Zone object
        for zone_data in ZONES:
            zone = Zone(
                name=zone_data["name"],
                location=zone_data["location"],
                zone_type=zone_data["zone_type"],
                rfid_antenna_id=zone_data.get("rfid_antenna_id"),
                esp32_id=zone_data.get("esp32_id"),
                display_order=ZONES.index(zone_data)
            )
            session.add(zone)
            zone_map[zone_data["name"]] = zone

        await session.flush()
        print(f"Created {len(ZONES)} zones")

        # Create products with zone assignments
        products = []
        for category, items in PRODUCTS.items():
            zone_name = CATEGORY_ZONES.get(category)
            zone_id = zone_map[zone_name].id if zone_name and zone_name in zone_map else None

            for name in items:
                product = Product(
                    name=name,
                    category=category,
                    default_unit="unit",
                    default_quantity=1,
                    shelf_life_days=random.randint(180, 730),
                    home_zone_id=zone_id
                )
                session.add(product)
                products.append(product)

        # Create freezer products
        freezer_products = []
        for category, items in FREEZER_ITEMS.items():
            for name, unit in items:
                product = Product(
                    name=name,
                    category=category,
                    default_unit=unit,
                    default_quantity=1,
                    shelf_life_days=random.randint(90, 365)
                )
                session.add(product)
                freezer_products.append(product)

        await session.flush()
        print(f"Created {len(products)} pantry products and {len(freezer_products)} freezer products")

        # Create RFID tags for bulk containers and snacks
        rfid_count = 0
        for product in products:
            if product.name in RFID_PRODUCTS:
                tag = RfidTag(
                    tag_id=f"E200{rfid_count:04d}0000{product.id:04d}",  # Simulated EPC
                    product_id=product.id,
                    container_name=f"{product.name} container",
                    home_zone_id=product.home_zone_id,
                    current_zone_id=product.home_zone_id,
                    is_present=True,
                    is_out=False
                )
                session.add(tag)
                # Also set rfid_tag_id on product
                product.rfid_tag_id = tag.tag_id
                rfid_count += 1

        await session.flush()
        print(f"Created {rfid_count} RFID tags")

        # Create/get freezers
        freezers = []
        for name, location, description in FREEZER_NAMES:
            # Check if exists
            existing = await session.scalar(
                select(Freezer).where(Freezer.name == name)
            )
            if existing:
                freezers.append(existing)
            else:
                freezer = Freezer(name=name, location=location, description=description)
                session.add(freezer)
                freezers.append(freezer)

        await session.flush()
        print(f"Created/found {len(freezers)} freezers")

        # Add pantry inventory (50 items)
        pantry_locations = ["pantry_shelf_1", "pantry_shelf_2", "pantry_shelf_3", "pantry_door"]
        for i, product in enumerate(random.sample(products, min(50, len(products)))):
            inventory = Inventory(
                product_id=product.id,
                quantity=random.randint(1, 5),
                location=random.choice(pantry_locations),
            )
            session.add(inventory)
        print("Added 50 pantry inventory items")

        # Add freezer inventory (25 items per freezer = 75 total)
        for freezer in freezers:
            # Get 25 random freezer products for this freezer
            items_for_freezer = random.sample(freezer_products, min(25, len(freezer_products)))

            for product in items_for_freezer:
                # Random frozen date in last 6 months
                days_ago = random.randint(1, 180)
                frozen_date = datetime.now() - timedelta(days=days_ago)

                inventory = Inventory(
                    product_id=product.id,
                    quantity=random.uniform(0.5, 3),
                    location="freezer",
                    freezer_id=freezer.id,
                    frozen_date=frozen_date.date(),
                    container_description=random.choice(CONTAINER_DESCRIPTIONS),
                )
                session.add(inventory)

            print(f"Added 25 items to {freezer.name}")

        await session.commit()
        print("\nSeed complete!")
        print(f"  - {len(ZONES)} zones")
        print(f"  - {len(products) + len(freezer_products)} products")
        print(f"  - {rfid_count} RFID tags")
        print(f"  - {len(freezers)} freezers")
        print(f"  - 50 pantry items")
        print(f"  - 75 freezer items (25 per freezer)")


if __name__ == "__main__":
    asyncio.run(seed_database())
