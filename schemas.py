# Pydantic-модели для валидации
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str

    model_config = {"extra": "forbid"}  # запрещает лишние поля в запросах


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int
    recipe_id: int  # важно: возвращаем связь с рецептом

    model_config = {"from_attributes": True}


class RecipeBase(BaseModel):
    title: str
    cooking_time: int
    description: Optional[str] = None

    model_config = {"extra": "forbid"}


class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]


class RecipeResponse(RecipeBase):
    id: int
    views: int
    created_at: datetime
    ingredients: List[IngredientResponse]

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    id: int
    title: str
    views: int
    cooking_time: int

    model_config = {"from_attributes": True}
