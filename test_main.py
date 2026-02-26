"""Тесты для API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from main import app, get_db
from database import engine, Base, AsyncSessionLocal


@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_get_recipes_empty(client):
    response = client.get("/recipes")
    assert response.status_code == 200
    assert response.json() == []


def test_create_recipe(client):
    recipe_data = {
        "title": "Тестовый рецепт",
        "cooking_time": 30,
        "description": "Тест",
        "ingredients": [{"name": "Мука"}],
    }

    response = client.post("/recipes", json=recipe_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестовый рецепт"
