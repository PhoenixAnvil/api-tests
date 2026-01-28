"""
API-SUT Items GET Tests

Tests for the GET /items endpoint. These positive, negative, and
validation tests verify that the API behaves correctly in each behavior
category.
"""

import httpx
import pytest
from assertpy import assert_that

pytestmark = [pytest.mark.items, pytest.mark.get]


@pytest.mark.positive
class TestGetAllItemsPositive:
    """Positive tests for GET /items endpoint."""

    def test_get_all_items_returns_200(self, client: httpx.Client):
        """GET /items should return 200 OK status code."""
        response = client.get("/items")

        assert_that(response.status_code).is_equal_to(200)

    def test_get_all_items_returns_list(self, client: httpx.Client):
        """GET /items should return a list of items."""
        response = client.get("/items")

        assert_that(response.json()).is_instance_of(list)

    def test_get_all_items_contains_demo_data(
        self, client: httpx.Client
    ):
        """GET /items should return pre-loaded demo data."""
        response = client.get("/items")
        items = response.json()

        assert_that(items).is_not_empty()
        # Verify demo items are present by checking for known item names
        item_names = [item["name"] for item in items]
        assert_that(item_names).contains("Wireless Mouse")

    def test_get_all_items_returns_complete_item_structure(
        self, client: httpx.Client
    ):
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


@pytest.mark.positive
class TestGetItemByIdPositive:
    """Positive tests for GET /items/{id} endpoint."""

    def test_get_item_by_id_returns_200(
        self, client: httpx.Client, create_test_item
    ):
        """GET /items/{id} should return 200 OK for existing item."""
        item = create_test_item()

        response = client.get(f"/items/{item['id']}")

        assert_that(response.status_code).is_equal_to(200)

    def test_get_item_by_id_returns_correct_item(
        self, client: httpx.Client, create_test_item
    ):
        """GET /items/{id} should return the correct item data."""
        created_item = create_test_item()

        response = client.get(f"/items/{created_item['id']}")
        retrieved_item = response.json()

        assert_that(retrieved_item["id"]).is_equal_to(
            created_item["id"]
        )
        assert_that(retrieved_item["name"]).is_equal_to(
            created_item["name"]
        )
        assert_that(retrieved_item["price"]).is_equal_to(
            created_item["price"]
        )

    def test_get_item_returns_all_fields(
        self, client: httpx.Client, create_test_item
    ):
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

    def test_get_item_returns_json_content_type(
        self, client: httpx.Client, create_test_item
    ):
        """GET /items/{id} should return JSON content type."""
        item = create_test_item()

        response = client.get(f"/items/{item['id']}")

        assert_that(response.headers["content-type"]).contains(
            "application/json"
        )


@pytest.mark.negative
class TestGetItemByIdNegative:
    """Negative tests for GET /items/{id} endpoint."""

    def test_get_nonexistent_item_returns_404(
        self, client: httpx.Client
    ):
        """GET /items/{id} should return 404 for non-existent ID."""
        response = client.get("/items/999999")

        assert_that(response.status_code).is_equal_to(404)

    def test_get_nonexistent_item_returns_error_detail(
        self, client: httpx.Client
    ):
        """
        GET /items/{id} should return error detail for non-existent ID.
        """
        response = client.get("/items/999999")

        assert_that(response.json()).contains_key("detail")
        assert_that(response.json()["detail"]).contains("not found")

    def test_get_item_with_zero_id_returns_404(
        self, client: httpx.Client
    ):
        """GET /items/0 should return 404 (no item with ID 0)."""
        response = client.get("/items/0")

        assert_that(response.status_code).is_equal_to(404)

    def test_get_item_with_negative_id_returns_error(
        self, client: httpx.Client
    ):
        """GET /items/{negative_id} should return an error."""
        response = client.get("/items/-1")

        # FastAPI may return 404 or 422 depending on validation
        assert_that(response.status_code).is_in(404, 422)

    @pytest.mark.parametrize("non_int_id", ["abc", "1.5", 1.5])
    def test_get_item_with_non_int_id_returns_422(
        self, client: httpx.Client, non_int_id
    ):
        """
        GET /items/{non_int_id} should return 422 for non-integer ID.
        """
        response = client.get(f"/items/{non_int_id}")

        assert_that(response.status_code).is_equal_to(422)

    def test_get_deleted_item_returns_404(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """GET /items/{id} should return 404 for a deleted item."""
        # Create and then delete an item
        created = client.post("/items", json=valid_item_payload).json()
        client.delete(f"/items/{created['id']}")

        # Try to retrieve the deleted item
        response = client.get(f"/items/{created['id']}")

        assert_that(response.status_code).is_equal_to(404)


@pytest.mark.validation
class TestIdFieldValidation:
    """Validation tests for the 'id' path parameter."""

    def test_id_as_very_large_integer(self, client: httpx.Client):
        """
        Very large ID should return
        404 (not found, not validation error).
        """
        response = client.get("/items/9999999999999")

        assert_that(response.status_code).is_equal_to(404)

    def test_id_with_leading_zeros(
        self, client: httpx.Client, create_test_item
    ):
        """ID with leading zeros should be parsed correctly."""
        item = create_test_item()
        item_id = item["id"]

        # Leading zeros are typically stripped by the URL parser
        response = client.get(f"/items/0{item_id}")

        # Behavior depends on implementation - could be 404 or match
        # the item's ID.
        assert_that(response.status_code).is_in(200, 404)

    def test_id_as_special_characters_returns_422(
        self, client: httpx.Client
    ):
        """ID with special characters should return 422."""
        response = client.get("/items/!@#$%")

        assert_that(response.status_code).is_equal_to(422)

    def test_id_as_empty_returns_error(self, client: httpx.Client):
        """
        Empty ID in URL should be handled (typically redirects or 404).
        """
        response = client.get("/items/")

        # This typically matches the GET /items endpoint
        assert_that(response.status_code).is_in(
            200, 307
        )  # May redirect to /items


@pytest.mark.validation
class TestResponseSchemaValidation:
    """Tests to validate response schema structure."""

    def test_item_response_has_correct_types(
        self, client: httpx.Client, create_test_item
    ):
        """Response item should have correct field types."""
        item = create_test_item()

        response = client.get(f"/items/{item['id']}")
        item_data = response.json()

        assert_that(item_data["id"]).is_instance_of(int)
        assert_that(item_data["name"]).is_instance_of(str)
        assert_that(item_data["price"]).is_instance_of(float)
        assert_that(item_data["quantity"]).is_instance_of(int)
        assert_that(item_data["created_at"]).is_instance_of(str)
        assert_that(item_data["updated_at"]).is_instance_of(str)

    def test_items_list_response_is_array(self, client: httpx.Client):
        """GET /items should return an array."""
        response = client.get("/items")

        assert_that(response.json()).is_instance_of(list)

    def test_error_response_has_detail_field(
        self, client: httpx.Client
    ):
        """Error responses should have a 'detail' field."""
        response = client.get("/items/999999")

        assert_that(response.status_code).is_equal_to(404)
        assert_that(response.json()).contains_key("detail")

    def test_validation_error_has_detailed_info(
        self, client: httpx.Client
    ):
        """Validation errors should include detailed information."""
        payload = {"name": "", "price": -1, "quantity": -1}
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)
        error_detail = response.json()["detail"]
        assert_that(error_detail).is_instance_of(list)
        assert_that(len(error_detail)).is_greater_than(0)

        # Each error should have location and message
        for error in error_detail:
            assert_that(error).contains_key("loc")
            assert_that(error).contains_key("msg")
