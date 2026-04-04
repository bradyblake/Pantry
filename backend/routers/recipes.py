from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import uuid
import json
import os

from database import get_db
from pydantic import BaseModel as PydanticBaseModel
from models.recipe import (
    Recipe, RecipeCreate, RecipeUpdate, RecipeResponse,
    RecipeIngredient, RecipeIngredientCreate, RecipeIngredientResponse,
    RecipeDocument, RecipeDocumentResponse,
    RecipeSuggestion
)
from models.inventory import Inventory
from services.recipe_parser import RecipeParser

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

# Directory for uploaded files
UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "uploads" / "recipes"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============ Recipes CRUD ============

@router.get("/", response_model=list[RecipeResponse])
async def list_recipes(
    search: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all recipes with optional search and filter."""
    query = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product),
        selectinload(Recipe.source_document)
    )

    if search:
        query = query.where(Recipe.name.ilike(f"%{search}%"))

    if tags:
        # Filter by tags (stored as JSON array string)
        for tag in tags.split(","):
            query = query.where(Recipe.tags.ilike(f"%{tag.strip()}%"))

    query = query.order_by(Recipe.name).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/suggestions", response_model=list[RecipeSuggestion])
async def get_recipe_suggestions(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get recipe suggestions based on current inventory."""
    # Get all recipes with ingredients
    recipes_query = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product)
    )
    recipes_result = await db.execute(recipes_query)
    recipes = recipes_result.scalars().all()

    # Get current inventory (aggregate quantities across locations)
    inv_query = select(Inventory)
    inv_result = await db.execute(inv_query)
    inventory = {}
    for item in inv_result.scalars().all():
        if item.product_id in inventory:
            inventory[item.product_id] += item.quantity
        else:
            inventory[item.product_id] = item.quantity

    suggestions = []

    for recipe in recipes:
        required_ingredients = [i for i in recipe.ingredients if not i.is_optional]
        optional_ingredients = [i for i in recipe.ingredients if i.is_optional]

        required_have = 0
        required_missing = []

        for ing in required_ingredients:
            if ing.product_id and ing.product_id in inventory:
                inv_qty = inventory[ing.product_id]
                needed_qty = ing.quantity or 1
                if inv_qty >= needed_qty:
                    required_have += 1
                else:
                    required_missing.append(ing)
            elif ing.product_id:
                required_missing.append(ing)
            else:
                # Untracked ingredient - give half credit
                required_have += 0.5

        optional_have = 0
        optional_missing = []

        for ing in optional_ingredients:
            if ing.product_id and ing.product_id in inventory:
                inv_qty = inventory[ing.product_id]
                needed_qty = ing.quantity or 1
                if inv_qty >= needed_qty:
                    optional_have += 1
                else:
                    optional_missing.append(ing)
            elif ing.product_id:
                optional_missing.append(ing)

        # Calculate score
        if len(required_ingredients) == 0:
            required_score = 100
        else:
            required_score = (required_have / len(required_ingredients)) * 100

        if len(optional_ingredients) == 0:
            optional_bonus = 0
        else:
            optional_bonus = (optional_have / len(optional_ingredients)) * 10

        score = required_score + optional_bonus

        # Determine status
        if score >= 100:
            status = "ready"
        elif score >= 80:
            status = "almost_ready"
        elif score >= 50:
            status = "need_items"
        else:
            status = "need_shopping"

        suggestions.append(RecipeSuggestion(
            recipe=recipe,
            score=score,
            missing_required=required_missing,
            missing_optional=optional_missing,
            status=status
        ))

    # Sort by score descending
    suggestions.sort(key=lambda x: x.score, reverse=True)

    return suggestions[:limit]


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single recipe with all details."""
    query = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product),
        selectinload(Recipe.source_document)
    ).where(Recipe.id == recipe_id)

    result = await db.execute(query)
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe


@router.post("/", response_model=RecipeResponse, status_code=201)
async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
    """Create a new recipe manually."""
    ingredients_data = recipe.ingredients or []
    recipe_dict = recipe.model_dump(exclude={"ingredients"})

    db_recipe = Recipe(**recipe_dict)
    db.add(db_recipe)
    await db.flush()

    # Add ingredients
    for ing_data in ingredients_data:
        ingredient = RecipeIngredient(recipe_id=db_recipe.id, **ing_data.model_dump())
        db.add(ingredient)

    await db.flush()

    # Reload with relationships
    query = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product),
        selectinload(Recipe.source_document)
    ).where(Recipe.id == db_recipe.id)
    result = await db.execute(query)
    return result.scalar_one()


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(recipe_id: int, recipe: RecipeUpdate, db: AsyncSession = Depends(get_db)):
    """Update a recipe."""
    query = select(Recipe).where(Recipe.id == recipe_id)
    result = await db.execute(query)
    db_recipe = result.scalar_one_or_none()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = recipe.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_recipe, key, value)

    await db.flush()

    # Reload with relationships
    query = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product),
        selectinload(Recipe.source_document)
    ).where(Recipe.id == recipe_id)
    result = await db.execute(query)
    return result.scalar_one()


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a recipe."""
    query = select(Recipe).where(Recipe.id == recipe_id)
    result = await db.execute(query)
    db_recipe = result.scalar_one_or_none()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    await db.delete(db_recipe)


# ============ Recipe Ingredients ============

@router.post("/{recipe_id}/ingredients", response_model=RecipeIngredientResponse, status_code=201)
async def add_ingredient(
    recipe_id: int,
    ingredient: RecipeIngredientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add an ingredient to a recipe."""
    # Verify recipe exists
    recipe_query = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe_query.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_ingredient = RecipeIngredient(recipe_id=recipe_id, **ingredient.model_dump())
    db.add(db_ingredient)
    await db.flush()

    # Reload with product
    query = select(RecipeIngredient).options(
        selectinload(RecipeIngredient.product)
    ).where(RecipeIngredient.id == db_ingredient.id)
    result = await db.execute(query)
    return result.scalar_one()


@router.delete("/{recipe_id}/ingredients/{ingredient_id}", status_code=204)
async def remove_ingredient(recipe_id: int, ingredient_id: int, db: AsyncSession = Depends(get_db)):
    """Remove an ingredient from a recipe."""
    query = select(RecipeIngredient).where(
        RecipeIngredient.id == ingredient_id,
        RecipeIngredient.recipe_id == recipe_id
    )
    result = await db.execute(query)
    ingredient = result.scalar_one_or_none()

    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    await db.delete(ingredient)


# ============ PDF Upload & Parsing ============

@router.post("/upload-pdf", response_model=RecipeDocumentResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a PDF recipe document for parsing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not allowed")

    # Determine file type
    if file.content_type == "application/pdf":
        file_type = "pdf"
        ext = ".pdf"
    else:
        file_type = "image"
        ext = Path(file.filename).suffix or ".jpg"

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Create document record
    doc = RecipeDocument(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_type=file_type,
        file_size_bytes=len(content)
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    return doc


@router.post("/documents/{document_id}/parse", response_model=list[RecipeResponse])
async def parse_document(
    document_id: int,
    use_vision: bool = Query(True, description="Use vision API for better parsing"),
    db: AsyncSession = Depends(get_db)
):
    """Parse a previously uploaded document to extract recipes."""
    # Get document
    query = select(RecipeDocument).where(RecipeDocument.id == document_id)
    result = await db.execute(query)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if already parsed
    if doc.parsed:
        # Return existing recipes from this document
        recipes_query = select(Recipe).options(
            selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product)
        ).where(Recipe.source_document_id == document_id)
        recipes_result = await db.execute(recipes_query)
        return recipes_result.scalars().all()

    # Parse the document
    parser = RecipeParser()

    try:
        if doc.file_type == "pdf":
            parsed = await parser.parse_pdf(doc.file_path, use_vision=use_vision)
        else:
            # Image file
            with open(doc.file_path, "rb") as f:
                image_data = f.read()
            media_type = f"image/{Path(doc.filename).suffix[1:]}"
            parsed = await parser.parse_recipe_from_image(image_data, media_type)

        # Handle error response
        if isinstance(parsed, dict) and "error" in parsed:
            doc.parsed = True
            doc.parsed_at = datetime.utcnow()
            doc.parse_error = parsed["error"]
            await db.flush()
            raise HTTPException(status_code=422, detail=parsed["error"])

        # Normalize to list
        if isinstance(parsed, dict):
            parsed = [parsed]

        created_recipes = []

        for recipe_data in parsed:
            # Create recipe
            db_recipe = Recipe(
                name=recipe_data.get("name", "Untitled Recipe"),
                description=recipe_data.get("description"),
                instructions=recipe_data.get("instructions"),
                prep_time_minutes=recipe_data.get("prep_time_minutes"),
                cook_time_minutes=recipe_data.get("cook_time_minutes"),
                servings=recipe_data.get("servings"),
                source="pdf_import",
                source_document_id=document_id,
                tags=json.dumps(recipe_data.get("tags", [])) if recipe_data.get("tags") else None
            )
            db.add(db_recipe)
            await db.flush()

            # Add ingredients
            for ing_data in recipe_data.get("ingredients", []):
                ingredient = RecipeIngredient(
                    recipe_id=db_recipe.id,
                    ingredient_text=ing_data.get("text", str(ing_data)),
                    quantity=ing_data.get("quantity"),
                    unit=ing_data.get("unit"),
                    is_optional=ing_data.get("is_optional", False)
                )
                db.add(ingredient)

            created_recipes.append(db_recipe)

        # Mark document as parsed
        doc.parsed = True
        doc.parsed_at = datetime.utcnow()
        doc.raw_text = json.dumps(parsed)

        await db.flush()

        # Reload recipes with relationships
        recipe_ids = [r.id for r in created_recipes]
        reload_query = select(Recipe).options(
            selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product),
            selectinload(Recipe.source_document)
        ).where(Recipe.id.in_(recipe_ids))
        reload_result = await db.execute(reload_query)
        return reload_result.scalars().all()

    except Exception as e:
        doc.parsed = True
        doc.parsed_at = datetime.utcnow()
        doc.parse_error = str(e)
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")


@router.get("/documents", response_model=list[RecipeDocumentResponse])
async def list_documents(
    parsed: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List uploaded recipe documents."""
    query = select(RecipeDocument)

    if parsed is not None:
        query = query.where(RecipeDocument.parsed == parsed)

    query = query.order_by(RecipeDocument.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an uploaded document (and optionally its recipes)."""
    query = select(RecipeDocument).where(RecipeDocument.id == document_id)
    result = await db.execute(query)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)




# ============ URL Import ============

class UrlImportRequest(PydanticBaseModel):
    url: str


@router.post("/import-url", response_model=list[RecipeResponse])
async def import_from_url(
    request: UrlImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Import a recipe from a URL (TikTok, Instagram, YouTube, recipe blogs, etc.)."""
    parser = RecipeParser()

    try:
        parsed = await parser.parse_recipe_from_url(request.url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to extract recipe from URL: {str(e)}")

    # Handle error response from AI
    if isinstance(parsed, dict) and "error" in parsed:
        raise HTTPException(status_code=422, detail=parsed["error"])

    # Normalize to list
    if isinstance(parsed, dict):
        parsed = [parsed]

    created_recipes = []

    for recipe_data in parsed:
        db_recipe = Recipe(
            name=recipe_data.get("name", "Untitled Recipe"),
            description=recipe_data.get("description"),
            instructions=recipe_data.get("instructions"),
            prep_time_minutes=recipe_data.get("prep_time_minutes"),
            cook_time_minutes=recipe_data.get("cook_time_minutes"),
            servings=recipe_data.get("servings"),
            source="url_import",
            source_url=request.url,
            tags=json.dumps(recipe_data.get("tags", [])) if recipe_data.get("tags") else None
        )
        db.add(db_recipe)
        await db.flush()

        # Add ingredients
        for ing_data in recipe_data.get("ingredients", []):
            ingredient = RecipeIngredient(
                recipe_id=db_recipe.id,
                ingredient_text=ing_data.get("text", str(ing_data)),
                quantity=ing_data.get("quantity"),
                unit=ing_data.get("unit"),
                is_optional=ing_data.get("is_optional", False)
            )
            db.add(ingredient)

        created_recipes.append(db_recipe)

    await db.flush()

    # Reload recipes with relationships
    recipe_ids = [r.id for r in created_recipes]
    reload_query = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.product),
        selectinload(Recipe.source_document)
    ).where(Recipe.id.in_(recipe_ids))
    reload_result = await db.execute(reload_query)
    return reload_result.scalars().all()


# ============ Recipe Actions ============

@router.post("/{recipe_id}/make")
async def make_recipe(
    recipe_id: int,
    servings: Optional[int] = Query(None, description="Number of servings (scales ingredients)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Log that a recipe was made - decrements inventory for tracked ingredients.
    """
    query = select(Recipe).options(
        selectinload(Recipe.ingredients)
    ).where(Recipe.id == recipe_id)
    result = await db.execute(query)
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Calculate scale factor
    scale = 1.0
    if servings and recipe.servings:
        scale = servings / recipe.servings

    decremented = []
    skipped = []

    for ing in recipe.ingredients:
        if not ing.product_id:
            skipped.append(ing.ingredient_text)
            continue

        # Find inventory for this product
        inv_query = select(Inventory).where(
            Inventory.product_id == ing.product_id,
            Inventory.quantity > 0
        ).order_by(Inventory.quantity.desc())
        inv_result = await db.execute(inv_query)
        inventory = inv_result.scalar_one_or_none()

        if inventory:
            amount_needed = (ing.quantity or 1) * scale
            inventory.quantity = max(0, inventory.quantity - amount_needed)
            decremented.append({
                "ingredient": ing.ingredient_text,
                "amount_used": amount_needed,
                "remaining": inventory.quantity
            })
        else:
            skipped.append(ing.ingredient_text)

    return {
        "status": "ok",
        "recipe": recipe.name,
        "decremented": decremented,
        "skipped": skipped
    }
