import uuid
import os
import json
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db, init_db
from models import Recipe, RecipeIngredient, Tag, PantryItem, MatchExclusion, MealPlan, MealPlanEntry, ShoppingListItem
from schemas import (
    RecipeCreate, RecipeUpdate, RecipeResponse, IngredientResponse,
    PantryItemCreate, PantryItemUpdate, PantryItemResponse,
    MealPlanCreate, MealPlanEntryCreate, MealPlanResponse,
    ShoppingListItemResponse, RecipeMatch,
)
from recipe_parser import parse_recipe_image
from config import UPLOAD_PATH, GROQ_API_KEY

app = FastAPI(title="Recipe Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images
app.mount("/images", StaticFiles(directory=UPLOAD_PATH), name="images")


@app.on_event("startup")
def startup():
    init_db()


# ── Helper ──────────────────────────────────────────────────────────────

def _recipe_to_response(recipe: Recipe) -> dict:
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "servings": recipe.servings,
        "source": recipe.source,
        "image_path": recipe.image_path,
        "favorite": bool(recipe.favorite),
        "quick_meal_type": recipe.quick_meal_type,
        "ingredients": [
            {"id": i.id, "name": i.name, "quantity": i.quantity, "unit": i.unit, "notes": i.notes}
            for i in recipe.ingredients
        ],
        "tags": [t.name for t in recipe.tags],
    }


def _get_or_create_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    tags = []
    for name in tag_names:
        name = name.lower().strip()
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags


# ── Recipes ─────────────────────────────────────────────────────────────

@app.post("/api/recipes/scan")
async def scan_recipe(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a recipe photo, parse it with Claude Vision, and return structured data for review."""
    ext = Path(file.filename or "photo.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_PATH, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    try:
        parsed = parse_recipe_image(filepath)
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(status_code=422, detail=f"Failed to parse recipe: {str(e)}")

    parsed["image_filename"] = filename
    return parsed


@app.post("/api/recipes", response_model=RecipeResponse)
def create_recipe(recipe: RecipeCreate, image_filename: str = "", db: Session = Depends(get_db)):
    """Save a reviewed/edited recipe to the database."""
    db_recipe = Recipe(
        title=recipe.title,
        description=recipe.description,
        instructions=recipe.instructions,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        servings=recipe.servings,
        source=recipe.source,
        image_path=image_filename,
    )
    db.add(db_recipe)
    db.flush()

    for ing in recipe.ingredients:
        db.add(RecipeIngredient(
            recipe_id=db_recipe.id,
            name=ing.name.lower().strip(),
            quantity=ing.quantity,
            unit=ing.unit,
            notes=ing.notes,
        ))

    db_recipe.tags = _get_or_create_tags(db, recipe.tags)
    db.commit()
    db.refresh(db_recipe)
    return _recipe_to_response(db_recipe)


@app.get("/api/recipes")
def list_recipes(search: str = "", tag: str = "", db: Session = Depends(get_db)):
    """List all recipes, optionally filtered by search term or tag."""
    query = db.query(Recipe)
    if search:
        query = query.filter(Recipe.title.ilike(f"%{search}%"))
    if tag:
        query = query.join(Recipe.tags).filter(Tag.name == tag.lower())
    recipes = query.order_by(Recipe.title).all()
    return [_recipe_to_response(r) for r in recipes]


@app.get("/api/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return _recipe_to_response(recipe)


@app.put("/api/recipes/{recipe_id}")
def update_recipe(recipe_id: int, updates: RecipeUpdate, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if updates.title is not None:
        recipe.title = updates.title
    if updates.description is not None:
        recipe.description = updates.description
    if updates.instructions is not None:
        recipe.instructions = updates.instructions
    if updates.prep_time is not None:
        recipe.prep_time = updates.prep_time
    if updates.cook_time is not None:
        recipe.cook_time = updates.cook_time
    if updates.servings is not None:
        recipe.servings = updates.servings
    if updates.source is not None:
        recipe.source = updates.source
    if updates.quick_meal_type is not None:
        recipe.quick_meal_type = updates.quick_meal_type if updates.quick_meal_type != "" else None

    if updates.ingredients is not None:
        db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_id).delete()
        for ing in updates.ingredients:
            db.add(RecipeIngredient(
                recipe_id=recipe_id,
                name=ing.name.lower().strip(),
                quantity=ing.quantity,
                unit=ing.unit,
                notes=ing.notes,
            ))

    if updates.tags is not None:
        recipe.tags = _get_or_create_tags(db, updates.tags)

    db.commit()
    db.refresh(recipe)
    return _recipe_to_response(recipe)


@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.image_path:
        img = os.path.join(UPLOAD_PATH, recipe.image_path)
        if os.path.exists(img):
            os.remove(img)
    db.delete(recipe)
    db.commit()
    return {"ok": True}


@app.put("/api/recipes/{recipe_id}/favorite")
def toggle_favorite(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.favorite = not recipe.favorite
    db.commit()
    return {"id": recipe.id, "favorite": bool(recipe.favorite)}


@app.get("/api/tags")
def list_tags(db: Session = Depends(get_db)):
    return [t.name for t in db.query(Tag).order_by(Tag.name).all()]


# ── Quick Meals ────────────────────────────────────────────────────────

@app.get("/api/quick-meals")
def list_quick_meals(meal_type: str = "", db: Session = Depends(get_db)):
    """List recipes and pantry items marked as quick meals, optionally filtered by type."""
    # Get quick meal recipes
    query = db.query(Recipe).filter(Recipe.quick_meal_type.isnot(None))
    if meal_type:
        query = query.filter(Recipe.quick_meal_type == meal_type.lower())
    recipes = query.order_by(Recipe.title).all()

    # Get quick meal pantry items
    pq = db.query(PantryItem).filter(PantryItem.quick_meal_type.isnot(None))
    if meal_type:
        pq = pq.filter(PantryItem.quick_meal_type == meal_type.lower())
    pantry_meals = pq.order_by(PantryItem.name).all()

    result = []
    for r in recipes:
        item = _recipe_to_response(r)
        item["source_type"] = "recipe"
        result.append(item)
    for p in pantry_meals:
        result.append({
            "id": p.id,
            "title": p.name,
            "quick_meal_type": p.quick_meal_type,
            "source_type": "pantry",
            "quantity": p.quantity,
            "unit": p.unit,
            "location": p.location,
            "category": p.category,
        })
    return result


@app.put("/api/recipes/{recipe_id}/quick-meal")
def set_quick_meal_type(recipe_id: int, meal_type: str = "", db: Session = Depends(get_db)):
    """Set or clear a recipe's quick meal type (breakfast, lunch, dinner, snack)."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    valid_types = {"breakfast", "lunch", "dinner", "snack", "instant", ""}
    if meal_type.lower() not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid meal type. Must be one of: {', '.join(valid_types - {''})}")
    recipe.quick_meal_type = meal_type.lower() if meal_type else None
    db.commit()
    return {"id": recipe.id, "quick_meal_type": recipe.quick_meal_type}


# ── Pantry ──────────────────────────────────────────────────────────────

@app.get("/api/pantry")
def list_pantry(db: Session = Depends(get_db)):
    items = db.query(PantryItem).order_by(PantryItem.category, PantryItem.name).all()
    return [{"id": i.id, "name": i.name, "quantity": i.quantity, "unit": i.unit, "category": i.category, "location": i.location, "quick_meal_type": i.quick_meal_type} for i in items]


@app.post("/api/pantry")
def add_pantry_item(item: PantryItemCreate, db: Session = Depends(get_db)):
    db_item = PantryItem(
        name=item.name.lower().strip(),
        quantity=item.quantity,
        unit=item.unit,
        category=item.category.lower().strip(),
        location=item.location.strip(),
        quick_meal_type=item.quick_meal_type.lower() if item.quick_meal_type else None,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"id": db_item.id, "name": db_item.name, "quantity": db_item.quantity, "unit": db_item.unit, "category": db_item.category, "location": db_item.location, "quick_meal_type": db_item.quick_meal_type}


@app.put("/api/pantry/{item_id}")
def update_pantry_item(item_id: int, updates: PantryItemUpdate, db: Session = Depends(get_db)):
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    if updates.name is not None:
        item.name = updates.name.lower().strip()
    if updates.quantity is not None:
        item.quantity = updates.quantity
    if updates.unit is not None:
        item.unit = updates.unit
    if updates.category is not None:
        item.category = updates.category.lower().strip()
    if updates.location is not None:
        item.location = updates.location.strip()
    if updates.quick_meal_type is not None:
        item.quick_meal_type = updates.quick_meal_type.lower() if updates.quick_meal_type else None
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "quantity": item.quantity, "unit": item.unit, "category": item.category, "location": item.location, "quick_meal_type": item.quick_meal_type}


@app.delete("/api/pantry/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    db.delete(item)
    db.commit()
    return {"ok": True}


# ── Make What We Have ───────────────────────────────────────────────────

# Common words to ignore when matching ingredients
_SKIP_WORDS = {
    'fresh', 'dried', 'ground', 'chopped', 'diced', 'sliced', 'minced',
    'large', 'small', 'medium', 'whole', 'boneless', 'skinless', 'raw',
    'cooked', 'frozen', 'canned', 'organic', 'low-sodium', 'unsalted',
    'extra', 'virgin', 'light', 'dark', 'sweet', 'hot', 'cold', 'warm',
    'thick', 'thin', 'fine', 'coarse', 'crushed', 'shredded', 'grated',
    'melted', 'softened', 'packed', 'sifted', 'toasted', 'roasted',
}


def _get_keywords(name: str) -> set[str]:
    """Extract meaningful keywords from an ingredient name."""
    words = name.lower().strip().split()
    return {w for w in words if w not in _SKIP_WORDS and len(w) > 1}


def _find_matching_pantry_items(
    pantry_items_by_name: dict[str, "PantryItem"],
    pantry_keywords: dict[str, set[str]],
    ingredient_name: str,
    exclusions: set[tuple[str, str]],
) -> list[dict]:
    """Find all pantry items that match a recipe ingredient.

    Returns list of matching pantry item details (name, quantity, unit, location, category).
    Respects exclusions - pairs the user has marked as 'not a match'.
    """
    ing_keywords = _get_keywords(ingredient_name)
    ing_full = ingredient_name.lower().strip()
    matches = []

    for pantry_name, p_keywords in pantry_keywords.items():
        # Check exclusions
        if (ing_full, pantry_name) in exclusions:
            continue

        is_match = False
        # Check if any pantry keyword appears in the full ingredient name
        if any(kw in ing_full for kw in p_keywords):
            is_match = True
        # Check if any ingredient keyword appears in the full pantry name
        if any(kw in pantry_name for kw in ing_keywords):
            is_match = True

        if is_match:
            item = pantry_items_by_name[pantry_name]
            matches.append({
                "pantry_id": item.id,
                "pantry_name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "location": item.location,
                "category": item.category,
            })

    return matches


@app.get("/api/recipes/match/pantry")
def match_recipes_to_pantry(db: Session = Depends(get_db)):
    """Find recipes that can be made with current pantry items, ranked by match percentage."""
    pantry_items = db.query(PantryItem).all()
    pantry_keywords = {
        item.name.lower().strip(): _get_keywords(item.name)
        for item in pantry_items
    }
    pantry_items_by_name = {
        item.name.lower().strip(): item
        for item in pantry_items
    }

    # Load exclusions
    exclusion_rows = db.query(MatchExclusion).all()
    exclusions = {
        (e.ingredient_name.lower().strip(), e.pantry_item_name.lower().strip())
        for e in exclusion_rows
    }

    recipes = db.query(Recipe).all()
    matches = []

    for recipe in recipes:
        recipe_ingredients = [i.name.lower().strip() for i in recipe.ingredients]
        if not recipe_ingredients:
            continue

        matched = []
        matched_details = []
        missing = []
        for ing_name in recipe_ingredients:
            pantry_matches = _find_matching_pantry_items(
                pantry_items_by_name, pantry_keywords, ing_name, exclusions
            )
            if pantry_matches:
                matched.append(ing_name)
                matched_details.append({
                    "ingredient": ing_name,
                    "matched_pantry_items": pantry_matches,
                })
            else:
                missing.append(ing_name)

        pct = len(matched) / len(recipe_ingredients) * 100
        matches.append({
            "recipe": _recipe_to_response(recipe),
            "matched_ingredients": matched,
            "matched_details": matched_details,
            "missing_ingredients": missing,
            "match_percentage": round(pct, 1),
        })

    matches.sort(key=lambda m: m["match_percentage"], reverse=True)
    return matches


# ── Match Exclusions ───────────────────────────────────────────────────

@app.post("/api/match-exclusions")
def add_match_exclusion(
    ingredient_name: str,
    pantry_item_name: str,
    db: Session = Depends(get_db),
):
    """Mark a pantry item as 'not a match' for a recipe ingredient."""
    existing = db.query(MatchExclusion).filter(
        MatchExclusion.ingredient_name == ingredient_name.lower().strip(),
        MatchExclusion.pantry_item_name == pantry_item_name.lower().strip(),
    ).first()
    if existing:
        return {"ok": True, "id": existing.id, "message": "Already excluded"}

    excl = MatchExclusion(
        ingredient_name=ingredient_name.lower().strip(),
        pantry_item_name=pantry_item_name.lower().strip(),
    )
    db.add(excl)
    db.commit()
    db.refresh(excl)
    return {"ok": True, "id": excl.id}


@app.get("/api/match-exclusions")
def list_match_exclusions(db: Session = Depends(get_db)):
    """List all match exclusions."""
    exclusions = db.query(MatchExclusion).order_by(MatchExclusion.ingredient_name).all()
    return [
        {"id": e.id, "ingredient_name": e.ingredient_name, "pantry_item_name": e.pantry_item_name}
        for e in exclusions
    ]


@app.delete("/api/match-exclusions/{exclusion_id}")
def remove_match_exclusion(exclusion_id: int, db: Session = Depends(get_db)):
    """Remove a match exclusion (re-allow the match)."""
    excl = db.query(MatchExclusion).filter(MatchExclusion.id == exclusion_id).first()
    if not excl:
        raise HTTPException(status_code=404, detail="Exclusion not found")
    db.delete(excl)
    db.commit()
    return {"ok": True}


# ── Meal Plans ──────────────────────────────────────────────────────────

@app.post("/api/meal-plans")
def create_meal_plan(plan: MealPlanCreate, db: Session = Depends(get_db)):
    db_plan = MealPlan(name=plan.name, start_date=plan.start_date)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return {"id": db_plan.id, "name": db_plan.name, "start_date": db_plan.start_date, "entries": []}


@app.get("/api/meal-plans")
def list_meal_plans(db: Session = Depends(get_db)):
    plans = db.query(MealPlan).order_by(MealPlan.created_at.desc()).all()
    result = []
    for plan in plans:
        entries = []
        for e in plan.entries:
            recipe = db.query(Recipe).filter(Recipe.id == e.recipe_id).first()
            entries.append({
                "id": e.id,
                "recipe_id": e.recipe_id,
                "recipe_title": recipe.title if recipe else "Deleted recipe",
                "day_of_week": e.day_of_week,
                "meal_type": e.meal_type,
            })
        result.append({"id": plan.id, "name": plan.name, "start_date": plan.start_date, "entries": entries})
    return result


@app.get("/api/meal-plans/{plan_id}")
def get_meal_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    entries = []
    for e in plan.entries:
        recipe = db.query(Recipe).filter(Recipe.id == e.recipe_id).first()
        entries.append({
            "id": e.id,
            "recipe_id": e.recipe_id,
            "recipe_title": recipe.title if recipe else "Deleted recipe",
            "day_of_week": e.day_of_week,
            "meal_type": e.meal_type,
        })
    return {"id": plan.id, "name": plan.name, "start_date": plan.start_date, "entries": entries}


@app.post("/api/meal-plans/{plan_id}/entries")
def add_meal_plan_entry(plan_id: int, entry: MealPlanEntryCreate, db: Session = Depends(get_db)):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    db_entry = MealPlanEntry(
        meal_plan_id=plan_id,
        recipe_id=entry.recipe_id,
        day_of_week=entry.day_of_week,
        meal_type=entry.meal_type,
    )
    db.add(db_entry)
    db.commit()
    return {"ok": True}


@app.delete("/api/meal-plans/{plan_id}/entries/{entry_id}")
def remove_meal_plan_entry(plan_id: int, entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(MealPlanEntry).filter(
        MealPlanEntry.id == entry_id, MealPlanEntry.meal_plan_id == plan_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"ok": True}


@app.delete("/api/meal-plans/{plan_id}")
def delete_meal_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    db.delete(plan)
    db.commit()
    return {"ok": True}


# ── Shopping List ───────────────────────────────────────────────────────

@app.post("/api/meal-plans/{plan_id}/shopping-list")
def generate_shopping_list(plan_id: int, db: Session = Depends(get_db)):
    """Generate a shopping list from a meal plan, subtracting what's in the pantry."""
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    # Clear existing shopping list for this plan
    db.query(ShoppingListItem).filter(ShoppingListItem.meal_plan_id == plan_id).delete()

    # Gather all ingredients needed
    needed: dict[str, dict] = {}
    for entry in plan.entries:
        recipe = db.query(Recipe).filter(Recipe.id == entry.recipe_id).first()
        if not recipe:
            continue
        for ing in recipe.ingredients:
            key = f"{ing.name}|{ing.unit}"
            if key in needed:
                needed[key]["quantity"] += ing.quantity
            else:
                needed[key] = {
                    "name": ing.name,
                    "quantity": ing.quantity,
                    "unit": ing.unit,
                    "category": "other",
                }

    # Subtract pantry items (using flexible matching)
    pantry_items = db.query(PantryItem).all()
    pantry_kw = {
        item.name.lower().strip(): _get_keywords(item.name)
        for item in pantry_items
    }
    pantry_by_name = {item.name.lower().strip(): item for item in pantry_items}
    exclusion_rows = db.query(MatchExclusion).all()
    exclusions = {
        (e.ingredient_name.lower().strip(), e.pantry_item_name.lower().strip())
        for e in exclusion_rows
    }
    shopping_items = []

    for key, item in needed.items():
        # Check if we have this ingredient (flexible match)
        if _find_matching_pantry_items(pantry_by_name, pantry_kw, item["name"], exclusions):
            # Find the best matching pantry item for quantity subtraction
            pantry_match = pantry_by_name.get(item["name"])
            if pantry_match and pantry_match.unit == item["unit"]:
                remaining = item["quantity"] - pantry_match.quantity
                if remaining <= 0:
                    continue
                item["quantity"] = remaining
                item["category"] = pantry_match.category
            else:
                # Flexible match found but can't compare quantities — skip it
                continue

        db_item = ShoppingListItem(
            meal_plan_id=plan_id,
            name=item["name"],
            quantity=item["quantity"],
            unit=item["unit"],
            category=item["category"],
        )
        db.add(db_item)
        shopping_items.append(db_item)

    db.commit()
    return [
        {"id": i.id, "name": i.name, "quantity": i.quantity, "unit": i.unit, "checked": i.checked, "category": i.category}
        for i in shopping_items
    ]


@app.get("/api/meal-plans/{plan_id}/shopping-list")
def get_shopping_list(plan_id: int, db: Session = Depends(get_db)):
    items = db.query(ShoppingListItem).filter(ShoppingListItem.meal_plan_id == plan_id).order_by(
        ShoppingListItem.category, ShoppingListItem.name
    ).all()
    return [
        {"id": i.id, "name": i.name, "quantity": i.quantity, "unit": i.unit, "checked": i.checked, "category": i.category}
        for i in items
    ]


@app.put("/api/shopping-list/{item_id}/toggle")
def toggle_shopping_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.checked = not item.checked
    db.commit()
    return {"id": item.id, "checked": item.checked}


# ── AI Features (using Groq - free tier) ──────────────────────────────

_groq_client = None
def _get_groq():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client

GROQ_MODEL = "llama-3.3-70b-versatile"


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.post("/api/ai/categorize-recipes")
def ai_categorize_recipes(db: Session = Depends(get_db)):
    """Use AI to auto-categorize all uncategorized recipes by meal type."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured. Get a free key at https://console.groq.com")

    uncategorized = db.query(Recipe).filter(Recipe.quick_meal_type.is_(None)).all()
    if not uncategorized:
        return {"message": "All recipes are already categorized", "updated": 0}

    recipe_list = []
    for r in uncategorized:
        ings = ", ".join(i.name for i in r.ingredients[:8])
        recipe_list.append(f"- ID {r.id}: {r.title} (ingredients: {ings})")

    prompt = f"""Categorize each recipe below as one of: breakfast, lunch, dinner, snack, dessert.

Guidelines:
- Breakfast: eggs, pancakes, waffles, coffee cake, tostadas, quiche, biscuits, cereal, german pancakes
- Lunch: sandwiches, soups, salads, wraps, light meals
- Dinner: main courses with meat/protein, casseroles, roasts, pasta, hearty meals, enchiladas, meatloaf, chili
- Snack: small bites, dips, popcorn, bars, finger foods, muddy buddies, sausage balls
- Dessert: cakes, cookies, pudding, ice cream, sweet treats, brownies, frosting, cobbler

Recipes:
{chr(10).join(recipe_list)}

Respond ONLY with a JSON array: [{{"id": 1, "meal_type": "dinner"}}, ...]
No markdown, no explanation, no extra text."""

    try:
        response = _get_groq().chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:-1])
        results = json.loads(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI categorization failed: {str(e)}")

    updated = 0
    valid_types = {"breakfast", "lunch", "dinner", "snack", "dessert", "instant"}
    recipe_map = {r.id: r for r in uncategorized}
    for item in results:
        rid = item.get("id")
        mtype = item.get("meal_type", "").lower()
        if rid in recipe_map and mtype in valid_types:
            recipe_map[rid].quick_meal_type = mtype
            updated += 1

    db.commit()
    return {"message": f"Categorized {updated} recipes", "updated": updated, "results": results}


@app.post("/api/ai/chat")
def ai_chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Chat with AI about recipes, get suggestions, find new recipes."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured. Get a free key at https://console.groq.com")

    pantry_items = db.query(PantryItem).all()
    pantry_summary = ", ".join(sorted(set(i.name for i in pantry_items)))

    recipe_list = db.query(Recipe).all()
    recipe_titles = ", ".join(r.title for r in recipe_list)

    # Analyze food preferences from existing recipes
    all_tags = set()
    all_ingredients = {}
    for r in recipe_list:
        for t in r.tags:
            all_tags.add(t.name)
        for ing in r.ingredients:
            name = ing.name.lower()
            all_ingredients[name] = all_ingredients.get(name, 0) + 1
    # Get top ingredients to understand preferences
    top_ingredients = sorted(all_ingredients.items(), key=lambda x: -x[1])[:30]
    top_ing_str = ", ".join(f"{name} ({count}x)" for name, count in top_ingredients)

    system_prompt = f"""You are a helpful cooking assistant for a family's Recipe Manager app called PantryPal.
You know their pantry, recipes, and food preferences.

THEIR PANTRY ({len(pantry_items)} items): {pantry_summary}

THEIR RECIPES ({len(recipe_list)} recipes): {recipe_titles}

FOOD PREFERENCES (based on their recipe collection):
- Recipe tags/styles: {", ".join(sorted(all_tags)) if all_tags else "none tagged yet"}
- Most-used ingredients: {top_ing_str}
- This is a family that likes comfort food, southern/American cooking, crockpot meals, Tex-Mex, and simple home-style recipes.
- They keep things like frozen meals, pot pies, and convenience foods on hand.

IMPORTANT: Only suggest recipes that match their cooking style and preferences. Don't suggest exotic ingredients they're unlikely to have or want. Stick to the types of food they already cook - hearty, family-friendly meals. If suggesting something new, base it on ingredients and flavors they already use.

You can help with:
- Suggesting what to cook based on what they have
- Finding new recipe ideas that fit their style
- Answering cooking questions
- Suggesting substitutions for missing ingredients
- Meal planning ideas

When suggesting a NEW recipe, describe it conversationally first.
If they want to SAVE a recipe, include this JSON block in your response:

```json
{{"save_recipe": true, "title": "Recipe Name", "description": "Brief desc", "prep_time": 10, "cook_time": 30, "servings": 4, "ingredients": [{{"name": "ingredient", "quantity": "1", "unit": "cup", "notes": ""}}], "instructions": "Step 1.\\nStep 2.\\nStep 3.", "tags": ["dinner"]}}
```

Only include the save JSON when they explicitly ask to save. Otherwise just describe recipes conversationally.
Keep responses friendly and concise."""

    messages = [{"role": "system", "content": system_prompt}]
    for h in req.history[-10:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": req.message})

    try:
        response = _get_groq().chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        reply = response.choices[0].message.content

        # Check if the response contains a recipe to save
        saved_recipe = None
        if '"save_recipe"' in reply and '"save_recipe": true' in reply:
            try:
                # Find JSON block (might be in markdown code fence)
                text_to_parse = reply
                if "```json" in text_to_parse:
                    start = text_to_parse.index("```json") + 7
                    end = text_to_parse.index("```", start)
                    text_to_parse = text_to_parse[start:end]
                elif "```" in text_to_parse:
                    start = text_to_parse.index("```") + 3
                    end = text_to_parse.index("```", start)
                    text_to_parse = text_to_parse[start:end]
                else:
                    start = text_to_parse.index("{")
                    depth = 0
                    end = start
                    for ci in range(start, len(text_to_parse)):
                        if text_to_parse[ci] == "{": depth += 1
                        elif text_to_parse[ci] == "}": depth -= 1
                        if depth == 0: end = ci + 1; break
                    text_to_parse = text_to_parse[start:end]

                recipe_json = json.loads(text_to_parse.strip())
                if recipe_json.get("save_recipe"):
                    db_recipe = Recipe(
                        title=recipe_json.get("title", "AI Suggested Recipe"),
                        description=recipe_json.get("description", ""),
                        instructions=recipe_json.get("instructions", ""),
                        prep_time=recipe_json.get("prep_time", 0),
                        cook_time=recipe_json.get("cook_time", 0),
                        servings=recipe_json.get("servings", 4),
                        source="ai-chat",
                        quick_meal_type=recipe_json.get("tags", [None])[0] if recipe_json.get("tags") else None,
                    )
                    db.add(db_recipe)
                    db.flush()
                    for ing in recipe_json.get("ingredients", []):
                        db.add(RecipeIngredient(
                            recipe_id=db_recipe.id,
                            name=ing.get("name", ""),
                            quantity=str(ing.get("quantity", "")),
                            unit=ing.get("unit", ""),
                            notes=ing.get("notes", ""),
                        ))
                    if recipe_json.get("tags"):
                        tags = []
                        for tname in recipe_json["tags"]:
                            tag = db.query(Tag).filter(Tag.name == tname.lower()).first()
                            if not tag:
                                tag = Tag(name=tname.lower())
                                db.add(tag)
                            tags.append(tag)
                        db_recipe.tags = tags
                    db.commit()
                    saved_recipe = {"id": db_recipe.id, "title": db_recipe.title}
            except (ValueError, json.JSONDecodeError):
                pass

        return {"reply": reply, "saved_recipe": saved_recipe}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
