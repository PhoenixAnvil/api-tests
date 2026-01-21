"""
API-SUT Test Configuration and Fixtures

This module contains pytest fixtures and configuration for the API-SUT test suite.
"""

import pytest
import httpx
from typing import Generator, Any

# Base URL for the API - can be overridden via environment variable
BASE_URL = "http://127.0.0.1:8081"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the API."""
    return BASE_URL


@pytest.fixture(scope="session")
def client() -> Generator[httpx.Client, None, None]:
    """
    Create an HTTP client for making API requests.
    
    This fixture is session-scoped for efficiency across all tests.
    """
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
def valid_item_payload() -> dict[str, Any]:
    """Return a valid item payload for creating/updating items."""
    return {
        "name": "Test Item",
        "description": "A test item for automated testing",
        "price": 19.99,
        "quantity": 50
    }


@pytest.fixture
def minimal_valid_payload() -> dict[str, Any]:
    """Return a minimal valid payload (only required fields)."""
    return {
        "name": "Minimal Item",
        "price": 1.00,
        "quantity": 0
    }


@pytest.fixture
def create_test_item(client: httpx.Client, valid_item_payload: dict[str, Any]):
    """
    Factory fixture to create a test item and return its data.
    
    Automatically cleans up after the test by deleting the created item.
    """
    created_items = []
    
    def _create_item(payload: dict[str, Any] = None) -> dict[str, Any]:
        data = payload or valid_item_payload
        response = client.post("/items", json=data)
        item = response.json()
        created_items.append(item["id"])
        return item
    
    yield _create_item
    
    # Cleanup: delete all created items
    for item_id in created_items:
        try:
            client.delete(f"/items/{item_id}")
        except Exception:
            pass  # Item may already be deleted by the test


@pytest.fixture
def sample_items() -> list[dict[str, Any]]:
    """Return a list of sample item payloads for batch testing."""
    return [
        {
            "name": "Sample Item 1",
            "description": "First sample item",
            "price": 10.00,
            "quantity": 100
        },
        {
            "name": "Sample Item 2",
            "description": "Second sample item",
            "price": 25.50,
            "quantity": 200
        },
        {
            "name": "Sample Item 3",
            "description": "Third sample item",
            "price": 99.99,
            "quantity": 50
        }
    ]
