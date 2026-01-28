"""
API-SUT Items PUT Tests

Tests for the PUT /items/{id} endpoint. These positive, negative, and
validation tests verify that the API behaves correctly in each behavior
category.
"""

import httpx
import pytest
from assertpy import assert_that

pytestmark = [pytest.mark.items, pytest.mark.put]


@pytest.mark.positive
class TestUpdateItem:
    """Positive tests for PUT /items/{id} endpoint."""

    def test_update_item_returns_200(
        self,
        client: httpx.Client,
        create_test_item,
        valid_item_payload: dict,
    ):
        """PUT /items/{id} should return 200 OK for valid update."""
        item = create_test_item()

        response = client.put(
            f"/items/{item['id']}", json=valid_item_payload
        )

        assert_that(response.status_code).is_equal_to(200)

    def test_update_item_returns_updated_data(
        self, client: httpx.Client, create_test_item
    ):
        """PUT /items/{id} should return the updated item data."""
        item = create_test_item()
        update_payload = {
            "name": "Updated Name",
            "description": "Updated description",
            "price": 99.99,
            "quantity": 999,
        }

        response = client.put(
            f"/items/{item['id']}", json=update_payload
        )
        updated_item = response.json()

        assert_that(updated_item["name"]).is_equal_to("Updated Name")
        assert_that(updated_item["description"]).is_equal_to(
            "Updated description"
        )
        assert_that(updated_item["price"]).is_equal_to(99.99)
        assert_that(updated_item["quantity"]).is_equal_to(999)

    def test_update_item_preserves_id(
        self,
        client: httpx.Client,
        create_test_item,
        valid_item_payload: dict,
    ):
        """PUT /items/{id} should preserve the original item ID."""
        item = create_test_item()
        original_id = item["id"]

        response = client.put(
            f"/items/{item['id']}", json=valid_item_payload
        )
        updated_item = response.json()

        assert_that(updated_item["id"]).is_equal_to(original_id)

    def test_update_item_preserves_created_at(
        self,
        client: httpx.Client,
        create_test_item,
        valid_item_payload: dict,
    ):
        """
        PUT /items/{id} should preserve the original
        created_at timestamp.
        """
        item = create_test_item()
        original_created_at = item["created_at"]

        response = client.put(
            f"/items/{item['id']}", json=valid_item_payload
        )
        updated_item = response.json()

        assert_that(updated_item["created_at"]).is_equal_to(
            original_created_at
        )

    def test_update_item_updates_updated_at(
        self,
        client: httpx.Client,
        create_test_item,
        valid_item_payload: dict,
    ):
        """PUT /items/{id} should update the updated_at timestamp."""
        import time

        item = create_test_item()
        original_updated_at = item["updated_at"]

        time.sleep(0.1)  # Small delay to ensure timestamp difference

        response = client.put(
            f"/items/{item['id']}", json=valid_item_payload
        )
        updated_item = response.json()

        assert_that(updated_item["updated_at"]).is_not_equal_to(
            original_updated_at
        )

    def test_update_item_persists_changes(
        self, client: httpx.Client, create_test_item
    ):
        """
        PUT /items/{id} changes should persist when retrieved again.
        """
        item = create_test_item()
        update_payload = {
            "name": "Persisted Update",
            "price": 77.77,
            "quantity": 77,
        }

        client.put(f"/items/{item['id']}", json=update_payload)

        # Retrieve the item again
        get_response = client.get(f"/items/{item['id']}")
        retrieved_item = get_response.json()

        assert_that(retrieved_item["name"]).is_equal_to(
            "Persisted Update"
        )
        assert_that(retrieved_item["price"]).is_equal_to(77.77)


@pytest.mark.negative
class TestUpdateItemNegative:
    """Negative tests for PUT /items/{id} endpoint."""

    def test_update_nonexistent_item_returns_404(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """PUT /items/{id} should return 404 for non-existent ID."""
        response = client.put("/items/999999", json=valid_item_payload)

        assert_that(response.status_code).is_equal_to(404)

    def test_update_item_without_body_returns_422(
        self, client: httpx.Client, create_test_item
    ):
        """PUT /items/{id} without body should return 422."""
        item = create_test_item()

        response = client.put(f"/items/{item['id']}")

        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_with_empty_body_returns_422(
        self, client: httpx.Client, create_test_item
    ):
        """PUT /items/{id} with empty body should return 422."""
        item = create_test_item()

        response = client.put(f"/items/{item['id']}", json={})

        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_missing_required_field_returns_422(
        self, client: httpx.Client, create_test_item
    ):
        """PUT /items/{id} missing required field should return 422."""
        item = create_test_item()
        incomplete_payload = {
            "name": "Updated Name",
            "price": 20.00,
        }  # Missing quantity

        response = client.put(
            f"/items/{item['id']}", json=incomplete_payload
        )

        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_with_invalid_price_returns_422(
        self, client: httpx.Client, create_test_item
    ):
        """PUT /items/{id} with invalid price should return 422."""
        item = create_test_item()
        invalid_payload = {
            "name": "Test",
            "price": -10.00,
            "quantity": 5,
        }

        response = client.put(
            f"/items/{item['id']}", json=invalid_payload
        )

        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_with_string_id_returns_422(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """
        PUT /items/{string_id} should return 422 for non-integer ID.
        """
        response = client.put("/items/abc", json=valid_item_payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_update_deleted_item_returns_404(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """PUT /items/{id} should return 404 for a deleted item."""
        # Create and delete an item
        created = client.post("/items", json=valid_item_payload).json()
        client.delete(f"/items/{created['id']}")

        # Try to update the deleted item
        response = client.put(
            f"/items/{created['id']}", json=valid_item_payload
        )

        assert_that(response.status_code).is_equal_to(404)


@pytest.mark.validation
class TestUpdateValidation:
    """Validation tests specific to PUT /items/{id} endpoint."""

    def test_update_preserves_id_even_if_provided_in_body(
        self, client: httpx.Client, create_test_item
    ):
        """ID in request body should be ignored; path ID is used."""
        item = create_test_item()
        original_id = item["id"]

        # Try to change ID via body (should be ignored)
        update_payload = {
            "id": 99999,  # Should be ignored
            "name": "Updated Item",
            "price": 20.00,
            "quantity": 10,
        }

        response = client.put(
            f"/items/{original_id}", json=update_payload
        )

        # Request might succeed (extra field ignored) or fail (422)
        if response.status_code == 200:
            assert_that(response.json()["id"]).is_equal_to(original_id)

    def test_update_with_extra_fields_in_body(
        self, client: httpx.Client, create_test_item
    ):
        """Extra fields in request body should be ignored."""
        item = create_test_item()

        update_payload = {
            "name": "Updated Item",
            "price": 20.00,
            "quantity": 10,
            "extra_field": "should be ignored",
            "another_extra": 12345,
        }

        response = client.put(
            f"/items/{item['id']}", json=update_payload
        )

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.json()).does_not_contain_key("extra_field")
