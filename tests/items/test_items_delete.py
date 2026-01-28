"""
API-SUT Items DELETE Tests

Tests for the DELETE /items endpoint. These positive and negative
tests verify that the API behaves correctly in each behavior category.
"""

import httpx
import pytest
from assertpy import assert_that

pytestmark = [pytest.mark.items, pytest.mark.delete]


@pytest.mark.positive
class TestDeleteItemPositive:
    """Positive tests for DELETE /items/{id} endpoint."""

    def test_delete_item_returns_204(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """DELETE /items/{id} should return 204 No Content."""
        # Create an item to delete
        created = client.post("/items", json=valid_item_payload).json()

        response = client.delete(f"/items/{created['id']}")

        assert_that(response.status_code).is_equal_to(204)

    def test_delete_item_returns_empty_body(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """DELETE /items/{id} should return an empty response body."""
        created = client.post("/items", json=valid_item_payload).json()

        response = client.delete(f"/items/{created['id']}")

        assert_that(response.text).is_empty()

    def test_delete_item_removes_from_store(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """
        DELETE /items/{id} should remove the item from the data store.
        """
        created = client.post("/items", json=valid_item_payload).json()
        item_id = created["id"]

        client.delete(f"/items/{item_id}")

        # Verify item no longer exists
        get_response = client.get(f"/items/{item_id}")
        assert_that(get_response.status_code).is_equal_to(404)

    def test_delete_item_does_not_affect_other_items(
        self, client: httpx.Client, valid_item_payload: dict
    ):
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


@pytest.mark.negative
class TestDeleteItemNegative:
    """Negative tests for DELETE /items/{id} endpoint."""

    def test_delete_nonexistent_item_returns_404(
        self, client: httpx.Client
    ):
        """DELETE /items/{id} should return 404 for non-existent ID."""
        response = client.delete("/items/999999")

        assert_that(response.status_code).is_equal_to(404)

    @pytest.mark.parametrize("non_int_id", ["abc", "1.5", 1.5])
    def test_delete_item_with_non_int_id_returns_422(
        self, client: httpx.Client, non_int_id
    ):
        """
        DELETE /items/{non_int_id} should return 422 for non-integer ID.
        """
        response = client.delete(f"/items/{non_int_id}")

        assert_that(response.status_code).is_equal_to(422)

    def test_delete_item_with_string_id_returns_422(
        self, client: httpx.Client
    ):
        """
        DELETE /items/{string_id} should return 422 for non-integer ID.
        """
        response = client.delete("/items/abc")

        assert_that(response.status_code).is_equal_to(422)

    def test_delete_item_twice_returns_404(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """
        DELETE /items/{id} twice should return 404 on second attempt.
        """
        # Create an item
        created = client.post("/items", json=valid_item_payload).json()

        # Delete it once - should succeed
        first_delete = client.delete(f"/items/{created['id']}")
        assert_that(first_delete.status_code).is_equal_to(204)

        # Delete it again - should return 404
        second_delete = client.delete(f"/items/{created['id']}")
        assert_that(second_delete.status_code).is_equal_to(404)

    def test_delete_item_with_zero_id_returns_404(
        self, client: httpx.Client
    ):
        """DELETE /items/0 should return 404."""
        response = client.delete("/items/0")

        assert_that(response.status_code).is_equal_to(404)

    def test_delete_item_with_negative_id_returns_error(
        self, client: httpx.Client
    ):
        """DELETE /items/{negative_id} should return an error."""
        response = client.delete("/items/-1")

        assert_that(response.status_code).is_in(404, 422)
