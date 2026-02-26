"""FastAPI приложение для кулинарной книги."""


from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

import database
import models
import schemas


app = FastAPI(
    title="Кулинарная книга API",
    description="API для управления рецептами кулинарной книги",
    version="1.0.0",
)


async def get_db() -> AsyncSession:
    """Получить сессию БД."""
    async with database.AsyncSessionLocal() as session:
        yield session


@app.get(
    "/recipes",
    response_model=List[schemas.RecipeListResponse],
)
async def get_recipes(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех рецептов, отсортированных по популярности и времени готовки.

    - **Сортировка**: сначала по количеству просмотров (убывание),
      затем по времени готовки (возрастание).
    - **Поля в ответе**: id, title, views, cooking_time.
    """
    result = await db.execute(
        select(models.Recipe).order_by(
            desc(models.Recipe.views),
            models.Recipe.cooking_time,
        ),
    )
    recipes = result.scalars().all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить детальную информацию о конкретном рецепте.

    - **Увеличивает счётчик просмотров** на 1 при каждом запросе.
    - **Возвращает**: название, время готовки, описание, список ингредиентов.
    """
    recipe = await db.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    # Увеличиваем счётчик просмотров
    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)  # Обновляем объект после коммита

    return recipe


@app.post("/recipes", response_model=schemas.RecipeResponse, status_code=201)
async def create_recipe(
    recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)
):
    """
    Создать новый рецепт.

    **Тело запроса**:
    - **title**: название рецепта (строка, обязат.)
    - **cooking_time**: время готовки в минутах (число, обязат.)
    - **description**: описание (строка, опционально)
    - **ingredients**: список ингредиентов, каждый с полем `name` (обязат.)

    **Возвращает** полный объект рецепта с ID и списком ингредиентов.
    """
    db_recipe = models.Recipe(
        title=recipe.title,
        cooking_time=recipe.cooking_time,
        description=recipe.description,
    )
    db.add(db_recipe)
    await db.flush()  # Получаем ID рецепта до создания ингредиентов

    for ingredient in recipe.ingredients:
        db_ingredient = models.Ingredient(
            name=ingredient.name, recipe_id=db_recipe.id
        )
        db.add(db_ingredient)

    await db.commit()
    await db.refresh(db_recipe)  # Обновляем объект с актуальными данными из БД
    return db_recipe
