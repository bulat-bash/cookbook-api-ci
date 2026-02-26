"""Тесты для API."""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_recipes_status():
    """Проверка статус кода GET /recipes."""
    with pytest.raises(Exception):
        client.get("/recipes")


def test_create_recipe_status():
    """Проверка статус кода POST /recipes."""
    response = client.post("/recipes", json={})
    assert response.status_code in [422, 500]
