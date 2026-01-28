"""
API-SUT Items Smoke/Positive Tests

Smoke tests for items endpoint. These positive tests verify that the
API behaves correctly when given valid input. These tests cover the
happy path scenarios for all CRUD operations.

These should be run first to ensure the API is
healthy before running more comprehensive tests.
"""

import httpx
import pytest
from assertpy import assert_that

pytestmark = [
    pytest.mark.items,
    pytest.mark.smoke,
    pytest.mark.positive,
]


class TestItemsSmoke:
    """Smoke/Positive tests to verify basic API functionality."""

    def test_get_all_items_endpoint_is_accessible(
        self, client: httpx.Client
    ):
        """
        Verify the GET /items endpoint is accessible and returns a list.
        """
        response = client.get("/items")

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.json()).is_instance_of(list)

    def test_demo_data_is_preloaded(self, client: httpx.Client):
        """Verify that demo data is preloaded and available."""
        response = client.get("/items")
        items = response.json()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(items).is_not_empty()
        # Check that at least one demo item exists
        assert_that(len(items)).is_greater_than_or_equal_to(1)

        names = [i.get("name") for i in items]
        assert_that(names).contains("Wireless Mouse")

    def test_single_item_endpoint_is_accessible(
        self, client: httpx.Client
    ):
        """Verify that getting a single item by ID works."""
        # First get all items to find a valid ID
        all_items = client.get("/items").json()
        if all_items:
            item_id = all_items[0]["id"]
            response = client.get(f"/items/{item_id}")

            assert_that(response.status_code).is_equal_to(200)
            assert_that(response.json()).contains_key("id")
            assert_that(response.json()).contains_key("name")

    def test_post_endpoint_accepts_requests(self, client: httpx.Client):
        """Verify the POST /items endpoint accepts valid requests."""
        payload = {
            "name": "Smoke Test Item",
            "description": "Created during smoke testing",
            "price": 9.99,
            "quantity": 10,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        created_item = response.json()
        assert_that(created_item).contains_key("id")

        # Cleanup
        client.delete(f"/items/{created_item['id']}")

    def test_put_endpoint_accepts_requests(self, client: httpx.Client):
        """
        Verify the PUT /items/{id} endpoint accepts valid requests.
        """
        # Create an item first
        create_payload = {
            "name": "Item to Update",
            "price": 15.00,
            "quantity": 5,
        }
        created = client.post("/items", json=create_payload).json()

        # Update it
        update_payload = {
            "name": "Updated Smoke Test Item",
            "price": 20.00,
            "quantity": 10,
        }
        response = client.put(
            f"/items/{created['id']}", json=update_payload
        )

        assert_that(response.status_code).is_equal_to(200)

        # Cleanup
        client.delete(f"/items/{created['id']}")

    def test_delete_endpoint_accepts_requests(
        self, client: httpx.Client
    ):
        """
        Verify the DELETE /items/{id} endpoint accepts valid requests.
        """
        # Create an item first
        payload = {
            "name": "Item to Delete",
            "price": 5.00,
            "quantity": 1,
        }
        created = client.post("/items", json=payload).json()

        # Delete it
        response = client.delete(f"/items/{created['id']}")

        assert_that(response.status_code).is_equal_to(204)

    def test_api_returns_json_content_type(self, client: httpx.Client):
        """
        Verify the API returns JSON content type for data endpoints.
        """
        response = client.get("/items")

        assert_that(response.headers["content-type"]).contains(
            "application/json"
        )

    def test_items_list_contains_created_item(
        self, client: httpx.Client, create_test_item
    ):
        created = create_test_item()

        response = client.get("/items")
        assert_that(response.status_code).is_equal_to(200)

        items = response.json()
        assert_that([i["id"] for i in items]).contains(created["id"])
