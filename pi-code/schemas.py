from pydantic import BaseModel
from typing import Optional


class IngredientCreate(BaseModel):
    name: str
    quantity: str = ""
    unit: str = ""
    notes: str = ""


class IngredientResponse(IngredientCreate):
    id: int
    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    title: str
    description: str = ""
    instructions: str = ""
    prep_time: int = 0
    cook_time: int = 0
    servings: int = 4
    source: str = ""
    ingredients: list[IngredientCreate] = []
    tags: list[str] = []


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    source: Optional[str] = None
    quick_meal_type: Optional[str] = None
    ingredients: Optional[list[IngredientCreate]] = None
    tags: Optional[list[str]] = None


class RecipeResponse(BaseModel):
    id: int
    title: str
    description: str
    instructions: str
    prep_time: int
    cook_time: int
    servings: int
    source: str
    image_path: str
    favorite: bool = False
    quick_meal_type: Optional[str] = None
    ingredients: list[IngredientResponse]
    tags: list[str]
    model_config = {"from_attributes": True}


class PantryItemCreate(BaseModel):
    name: str
    quantity: str = ""
    unit: str = ""
    category: str = "other"
    location: str = ""
    quick_meal_type: Optional[str] = None


class PantryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    quick_meal_type: Optional[str] = None


class PantryItemResponse(PantryItemCreate):
    id: int
    model_config = {"from_attributes": True}


class MealPlanCreate(BaseModel):
    name: str
    start_date: str  # YYYY-MM-DD


class MealPlanEntryCreate(BaseModel):
    recipe_id: int
    day_of_week: int  # 0=Monday, 6=Sunday
    meal_type: str    # breakfast, lunch, dinner, snack


class MealPlanResponse(BaseModel):
    id: int
    name: str
    start_date: str
    entries: list[dict]
    model_config = {"from_attributes": True}


class ShoppingListItemResponse(BaseModel):
    id: int
    name: str
    quantity: str
    unit: str
    checked: bool
    category: str
    model_config = {"from_attributes": True}


class RecipeMatch(BaseModel):
    recipe: RecipeResponse
    matched_ingredients: list[str]
    missing_ingredients: list[str]
    match_percentage: float
