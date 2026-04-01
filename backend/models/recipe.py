from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from database import Base


class Recipe(Base):
    """Recipe storage."""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    servings = Column(Integer, nullable=True)
    source = Column(String(50), nullable=True)  # 'manual', 'pdf_import', 'url_import'
    source_url = Column(Text, nullable=True)
    source_document_id = Column(Integer, ForeignKey("recipe_documents.id"), nullable=True)
    image_url = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    source_document = relationship("RecipeDocument", lazy="joined")


class RecipeIngredient(Base):
    """Recipe ingredients linked to products."""
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    ingredient_text = Column(String(255), nullable=False)  # Original text
    quantity = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    is_optional = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    recipe = relationship("Recipe", back_populates="ingredients")
    product = relationship("Product", lazy="joined")


class RecipeDocument(Base):
    """Uploaded recipe documents (PDFs, images)."""
    __tablename__ = "recipe_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50), nullable=False)  # 'pdf', 'image'
    file_size_bytes = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)  # For PDFs
    parsed = Column(Boolean, default=False)
    parsed_at = Column(DateTime, nullable=True)
    parse_error = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)  # Extracted text
    created_at = Column(DateTime, server_default=func.now())


# Pydantic Schemas

class RecipeIngredientBase(BaseModel):
    ingredient_text: str
    product_id: Optional[int] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_optional: bool = False
    notes: Optional[str] = None


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredientUpdate(BaseModel):
    ingredient_text: Optional[str] = None
    product_id: Optional[int] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_optional: Optional[bool] = None
    notes: Optional[str] = None


class ProductInRecipe(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    default_unit: str

    class Config:
        from_attributes = True


class RecipeIngredientResponse(RecipeIngredientBase):
    id: int
    recipe_id: int
    product: Optional[ProductInRecipe] = None

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    source: Optional[str] = "manual"
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[str] = None  # JSON string


class RecipeCreate(RecipeBase):
    ingredients: Optional[List[RecipeIngredientCreate]] = None


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[str] = None


class RecipeDocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    parsed: bool
    parsed_at: Optional[datetime] = None
    parse_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeResponse(RecipeBase):
    id: int
    source_document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    ingredients: List[RecipeIngredientResponse] = []
    source_document: Optional[RecipeDocumentResponse] = None

    class Config:
        from_attributes = True


class RecipeSuggestion(BaseModel):
    recipe: RecipeResponse
    score: float  # 0-100+
    missing_required: List[RecipeIngredientResponse] = []
    missing_optional: List[RecipeIngredientResponse] = []
    status: str  # 'ready', 'almost_ready', 'need_items', 'need_shopping'


class ParsedRecipeFromPDF(BaseModel):
    """Structure returned from Claude PDF parsing."""
    name: str
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    ingredients: List[dict]  # [{text, quantity, unit, is_optional}]
    instructions: Optional[str] = None
    tags: Optional[List[str]] = None
