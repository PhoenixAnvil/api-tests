"""
API-SUT Positive Tests

Positive tests verify that the API behaves correctly when given valid input.
These tests cover the happy path scenarios for all CRUD operations.
"""

import pytest
import httpx
from assertpy import assert_that
from typing import Any


class TestGetAllItems:
    """Positive tests for GET /items endpoint."""

    def test_get_all_items_returns_200(self, client: httpx.Client):
        """GET /items should return 200 OK status code."""
        response = client.get("/items")
        
        assert_that(response.status_code).is_equal_to(200)

    def test_get_all_items_returns_list(self, client: httpx.Client):
        """GET /items should return a list of items."""
        response = client.get("/items")
        
        assert_that(response.json()).is_instance_of(list)

    def test_get_all_items_contains_demo_data(self, client: httpx.Client):
        """GET /items should return pre-loaded demo data."""
        response = client.get("/items")
        items = response.json()
        
        assert_that(items).is_not_empty()
        # Verify demo items are present by checking for known item names
        item_names = [item["name"] for item in items]
        assert_that(item_names).contains("Wireless Mouse")

    def test_get_all_items_returns_complete_item_structure(self, client: httpx.Client):
        """Each item should have all required fields."""
        response = client.get("/items")
        items = response.json()
        
        if items:
            item = items[0]
            assert_that(item).contains_key("id")
            assert_that(item).contains_key("name")
            assert_that(item).contains_key("price")
            assert_that(item).contains_key("quantity")
            assert_that(item).contains_key("created_at")
            assert_that(item).contains_key("updated_at")


class TestGetItemById:
    """Positive tests for GET /items/{id} endpoint."""

    def test_get_item_by_id_returns_200(self, client: httpx.Client, create_test_item):
        """GET /items/{id} should return 200 OK for existing item."""
        item = create_test_item()
        
        response = client.get(f"/items/{item['id']}")
        
        assert_that(response.status_code).is_equal_to(200)

    def test_get_item_by_id_returns_correct_item(self, client: httpx.Client, create_test_item):
        """GET /items/{id} should return the correct item data."""
        created_item = create_test_item()
        
        response = client.get(f"/items/{created_item['id']}")
        retrieved_item = response.json()
        
        assert_that(retrieved_item["id"]).is_equal_to(created_item["id"])
        assert_that(retrieved_item["name"]).is_equal_to(created_item["name"])
        assert_that(retrieved_item["price"]).is_equal_to(created_item["price"])

    def test_get_item_returns_all_fields(self, client: httpx.Client, create_test_item):
        """GET /items/{id} should return all item fields."""
        created_item = create_test_item()
        
        response = client.get(f"/items/{created_item['id']}")
        item = response.json()
        
        assert_that(item).contains_key("id")
        assert_that(item).contains_key("name")
        assert_that(item).contains_key("description")
        assert_that(item).contains_key("price")
        assert_that(item).contains_key("quantity")
        assert_that(item).contains_key("created_at")
        assert_that(item).contains_key("updated_at")

    def test_get_item_returns_json_content_type(self, client: httpx.Client, create_test_item):
        """GET /items/{id} should return JSON content type."""
        item = create_test_item()
        
        response = client.get(f"/items/{item['id']}")
        
        assert_that(response.headers["content-type"]).contains("application/json")


class TestCreateItem:
    """Positive tests for POST /items endpoint."""

    def test_create_item_returns_201(self, client: httpx.Client, valid_item_payload: dict):
        """POST /items should return 201 Created for valid payload."""
        response = client.post("/items", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(201)
        
        # Cleanup
        client.delete(f"/items/{response.json()['id']}")

    def test_create_item_returns_created_item(self, client: httpx.Client, valid_item_payload: dict):
        """POST /items should return the created item with ID."""
        response = client.post("/items", json=valid_item_payload)
        created_item = response.json()
        
        assert_that(created_item).contains_key("id")
        assert_that(created_item["name"]).is_equal_to(valid_item_payload["name"])
        assert_that(created_item["price"]).is_equal_to(valid_item_payload["price"])
        
        # Cleanup
        client.delete(f"/items/{created_item['id']}")

    def test_create_item_with_minimal_payload(self, client: httpx.Client, minimal_valid_payload: dict):
        """POST /items should succeed with only required fields."""
        response = client.post("/items", json=minimal_valid_payload)
        
        assert_that(response.status_code).is_equal_to(201)
        created_item = response.json()
        assert_that(created_item["description"]).is_none()
        
        # Cleanup
        client.delete(f"/items/{created_item['id']}")

    def test_create_item_generates_timestamps(self, client: httpx.Client, valid_item_payload: dict):
        """POST /items should auto-generate created_at and updated_at."""
        response = client.post("/items", json=valid_item_payload)
        created_item = response.json()
        
        assert_that(created_item).contains_key("created_at")
        assert_that(created_item).contains_key("updated_at")
        assert_that(created_item["created_at"]).is_not_none()
        assert_that(created_item["updated_at"]).is_not_none()
        
        # Cleanup
        client.delete(f"/items/{created_item['id']}")

    def test_create_item_generates_unique_id(self, client: httpx.Client, valid_item_payload: dict):
        """POST /items should generate unique IDs for each item."""
        response1 = client.post("/items", json=valid_item_payload)
        response2 = client.post("/items", json=valid_item_payload)
        
        item1 = response1.json()
        item2 = response2.json()
        
        assert_that(item1["id"]).is_not_equal_to(item2["id"])
        
        # Cleanup
        client.delete(f"/items/{item1['id']}")
        client.delete(f"/items/{item2['id']}")

    def test_create_item_with_null_description(self, client: httpx.Client):
        """POST /items should accept null description."""
        payload = {
            "name": "Item with null description",
            "description": None,
            "price": 10.00,
            "quantity": 5
        }
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        
        # Cleanup
        client.delete(f"/items/{response.json()['id']}")

    def test_create_item_with_zero_quantity(self, client: httpx.Client):
        """POST /items should accept quantity of 0."""
        payload = {
            "name": "Out of stock item",
            "price": 50.00,
            "quantity": 0
        }
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["quantity"]).is_equal_to(0)
        
        # Cleanup
        client.delete(f"/items/{response.json()['id']}")

    def test_create_item_with_decimal_price(self, client: httpx.Client):
        """POST /items should accept prices with decimal values."""
        payload = {
            "name": "Precise price item",
            "price": 19.99,
            "quantity": 10
        }
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["price"]).is_equal_to(19.99)
        
        # Cleanup
        client.delete(f"/items/{response.json()['id']}")


class TestUpdateItem:
    """Positive tests for PUT /items/{id} endpoint."""

    def test_update_item_returns_200(self, client: httpx.Client, create_test_item, valid_item_payload: dict):
        """PUT /items/{id} should return 200 OK for valid update."""
        item = create_test_item()
        
        response = client.put(f"/items/{item['id']}", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(200)

    def test_update_item_returns_updated_data(self, client: httpx.Client, create_test_item):
        """PUT /items/{id} should return the updated item data."""
        item = create_test_item()
        update_payload = {
            "name": "Updated Name",
            "description": "Updated description",
            "price": 99.99,
            "quantity": 999
        }
        
        response = client.put(f"/items/{item['id']}", json=update_payload)
        updated_item = response.json()
        
        assert_that(updated_item["name"]).is_equal_to("Updated Name")
        assert_that(updated_item["description"]).is_equal_to("Updated description")
        assert_that(updated_item["price"]).is_equal_to(99.99)
        assert_that(updated_item["quantity"]).is_equal_to(999)

    def test_update_item_preserves_id(self, client: httpx.Client, create_test_item, valid_item_payload: dict):
        """PUT /items/{id} should preserve the original item ID."""
        item = create_test_item()
        original_id = item["id"]
        
        response = client.put(f"/items/{item['id']}", json=valid_item_payload)
        updated_item = response.json()
        
        assert_that(updated_item["id"]).is_equal_to(original_id)

    def test_update_item_preserves_created_at(self, client: httpx.Client, create_test_item, valid_item_payload: dict):
        """PUT /items/{id} should preserve the original created_at timestamp."""
        item = create_test_item()
        original_created_at = item["created_at"]
        
        response = client.put(f"/items/{item['id']}", json=valid_item_payload)
        updated_item = response.json()
        
        assert_that(updated_item["created_at"]).is_equal_to(original_created_at)

    def test_update_item_updates_updated_at(self, client: httpx.Client, create_test_item, valid_item_payload: dict):
        """PUT /items/{id} should update the updated_at timestamp."""
        import time
        
        item = create_test_item()
        original_updated_at = item["updated_at"]
        
        time.sleep(0.1)  # Small delay to ensure timestamp difference
        
        response = client.put(f"/items/{item['id']}", json=valid_item_payload)
        updated_item = response.json()
        
        assert_that(updated_item["updated_at"]).is_not_equal_to(original_updated_at)

    def test_update_item_persists_changes(self, client: httpx.Client, create_test_item):
        """PUT /items/{id} changes should persist when retrieved again."""
        item = create_test_item()
        update_payload = {
            "name": "Persisted Update",
            "price": 77.77,
            "quantity": 77
        }
        
        client.put(f"/items/{item['id']}", json=update_payload)
        
        # Retrieve the item again
        get_response = client.get(f"/items/{item['id']}")
        retrieved_item = get_response.json()
        
        assert_that(retrieved_item["name"]).is_equal_to("Persisted Update")
        assert_that(retrieved_item["price"]).is_equal_to(77.77)


class TestDeleteItem:
    """Positive tests for DELETE /items/{id} endpoint."""

    def test_delete_item_returns_204(self, client: httpx.Client, valid_item_payload: dict):
        """DELETE /items/{id} should return 204 No Content."""
        # Create an item to delete
        created = client.post("/items", json=valid_item_payload).json()
        
        response = client.delete(f"/items/{created['id']}")
        
        assert_that(response.status_code).is_equal_to(204)

    def test_delete_item_returns_empty_body(self, client: httpx.Client, valid_item_payload: dict):
        """DELETE /items/{id} should return an empty response body."""
        created = client.post("/items", json=valid_item_payload).json()
        
        response = client.delete(f"/items/{created['id']}")
        
        assert_that(response.text).is_empty()

    def test_delete_item_removes_from_store(self, client: httpx.Client, valid_item_payload: dict):
        """DELETE /items/{id} should remove the item from the data store."""
        created = client.post("/items", json=valid_item_payload).json()
        item_id = created["id"]
        
        client.delete(f"/items/{item_id}")
        
        # Verify item no longer exists
        get_response = client.get(f"/items/{item_id}")
        assert_that(get_response.status_code).is_equal_to(404)

    def test_delete_item_does_not_affect_other_items(self, client: httpx.Client, valid_item_payload: dict):
        """DELETE /items/{id} should not affect other items."""
        # Create two items
        item1 = client.post("/items", json=valid_item_payload).json()
        item2 = client.post("/items", json=valid_item_payload).json()
        
        # Delete the first one
        client.delete(f"/items/{item1['id']}")
        
        # Verify second item still exists
        get_response = client.get(f"/items/{item2['id']}")
        assert_that(get_response.status_code).is_equal_to(200)
        
        # Cleanup
        client.delete(f"/items/{item2['id']}")


class TestHealthEndpoint:
    """Positive tests for GET /health endpoint."""

    def test_health_returns_200(self, client: httpx.Client):
        """GET /health should return 200 OK."""
        response = client.get("/health")
        
        assert_that(response.status_code).is_equal_to(200)

    def test_health_returns_message(self, client: httpx.Client):
        """GET /health should return a message indicating health status."""
        response = client.get("/health")
        
        assert_that(response.json()).contains_key("message")
        assert_that(response.json()["message"]).is_not_empty()


class TestRootEndpoint:
    """Positive tests for GET / endpoint."""

    def test_root_returns_200(self, client: httpx.Client):
        """GET / should return 200 OK."""
        response = client.get("/")
        
        assert_that(response.status_code).is_equal_to(200)

    def test_root_returns_welcome_message(self, client: httpx.Client):
        """GET / should return a welcome message."""
        response = client.get("/")
        
        assert_that(response.json()).contains_key("message")
        assert_that(response.json()["message"]).contains("Welcome")
