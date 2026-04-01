from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


# Many-to-many: recipe <-> tags
recipe_tags = Table(
    "recipe_tags",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

# Many-to-many: meal_plan <-> recipes
meal_plan_recipes = Table(
    "meal_plan_recipes",
    Base.metadata,
    Column("meal_plan_id", Integer, ForeignKey("meal_plans.id"), primary_key=True),
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("meal_type", String(20)),  # breakfast, lunch, dinner, snack
    Column("day_of_week", Integer),   # 0=Monday, 6=Sunday
)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, default="")
    instructions = Column(Text, default="")
    prep_time = Column(Integer, default=0)       # minutes
    cook_time = Column(Integer, default=0)       # minutes
    servings = Column(Integer, default=4)
    source = Column(String(255), default="")     # where the recipe came from
    image_path = Column(String(500), default="")
    favorite = Column(Boolean, default=False)
    quick_meal_type = Column(String(20), nullable=True)  # breakfast, lunch, dinner, snack
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=recipe_tags, back_populates="recipes")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    quantity = Column(String(50), default="")
    unit = Column(String(50), default="")
    notes = Column(String(255), default="")  # e.g., "diced", "room temperature"

    recipe = relationship("Recipe", back_populates="ingredients")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

    recipes = relationship("Recipe", secondary=recipe_tags, back_populates="tags")


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    quantity = Column(String(50), default="")
    unit = Column(String(50), default="")
    category = Column(String(100), default="other")  # produce, dairy, meat, pantry, frozen, etc.
    location = Column(String(255), default="")  # e.g., "Garage Freezer", "Kitchen Fridge"
    quick_meal_type = Column(String(20), nullable=True)  # breakfast, lunch, dinner, snack
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MatchExclusion(Base):
    """Stores user rejections of ingredient-to-pantry matches."""
    __tablename__ = "match_exclusions"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_name = Column(String(255), nullable=False, index=True)
    pantry_item_name = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    entries = relationship("MealPlanEntry", back_populates="meal_plan", cascade="all, delete-orphan")


class MealPlanEntry(Base):
    __tablename__ = "meal_plan_entries"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack

    meal_plan = relationship("MealPlan", back_populates="entries")
    recipe = relationship("Recipe")


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=True)
    name = Column(String(255), nullable=False)
    quantity = Column(String(50), default="")
    unit = Column(String(50), default="")
    checked = Column(Boolean, default=False)
    category = Column(String(100), default="other")
