"""
API-SUT Routing Smoke/Negative Tests

Smoke tests for routing endpoints. These negative tests
verify that endpoint routing handles invalid requests and
return the expected responses.

These tests should be run first to ensure the API is healthy
before running more comprehensive tests.
"""

import json

import httpx
import pytest
from assertpy import assert_that

pytestmark = [
    pytest.mark.routing,
    pytest.mark.smoke,
    pytest.mark.negative,
]


class TestInvalidHTTPMethods:
    """Tests for invalid HTTP methods on endpoints."""

    def test_patch_items_returns_405(
        self,
        client: httpx.Client,
        create_test_item,
        valid_item_payload: dict,
    ):
        """PATCH /items/{id} should return 405 Method Not Allowed."""
        item = create_test_item()

        response = client.patch(
            f"/items/{item['id']}", json=valid_item_payload
        )

        assert_that(response.status_code).is_equal_to(405)

    def test_put_on_items_collection_returns_405(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """
        PUT /items (without ID) should return 405 Method Not Allowed.
        """
        response = client.put("/items", json=valid_item_payload)

        assert_that(response.status_code).is_equal_to(405)

    def test_delete_on_items_collection_returns_405(
        self, client: httpx.Client
    ):
        """
        DELETE /items (without ID) should return 405 Method Not Allowed.
        """
        response = client.delete("/items")

        assert_that(response.status_code).is_equal_to(405)

    def test_post_on_specific_item_returns_405(
        self,
        client: httpx.Client,
        create_test_item,
        valid_item_payload: dict,
    ):
        """POST /items/{id} should return 405 Method Not Allowed."""
        item = create_test_item()

        response = client.post(
            f"/items/{item['id']}", json=valid_item_payload
        )

        assert_that(response.status_code).is_equal_to(405)


class TestInvalidEndpoints:
    """Tests for invalid/non-existent endpoints."""

    def test_nonexistent_endpoint_returns_404(
        self, client: httpx.Client
    ):
        """Request to non-existent endpoint should return 404."""
        response = client.get("/nonexistent")

        assert_that(response.status_code).is_equal_to(404)

    def test_misspelled_items_endpoint_returns_404(
        self, client: httpx.Client
    ):
        """Request to misspelled endpoint should return 404."""
        response = client.get("/item")  # Missing 's'

        assert_that(response.status_code).is_equal_to(404)

    def test_nested_nonexistent_endpoint_returns_404(
        self, client: httpx.Client
    ):
        """Request to nested non-existent endpoint should return 404."""
        response = client.get("/items/1/details")

        assert_that(response.status_code).is_equal_to(404)


class TestMalformedRequests:
    """Tests for malformed request handling."""

    def test_invalid_json_body_returns_422(self, client: httpx.Client):
        """
        POST /items with invalid JSON should return 422.
        Note: FastAPI returns 422 instead of 400 in this scenario.
        """
        response = client.post(
            "/items",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )

        assert_that(response.status_code).is_equal_to(422)

    def test_wrong_content_type_returns_422(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """
        POST /items with wrong content type should return 422.
        Note: FastAPI returns 422 instead of 415 in this scenario.
        """
        response = client.post(
            "/items",
            content=json.dumps(valid_item_payload),
            headers={"Content-Type": "text/plain"},
        )

        assert_that(response.status_code).is_equal_to(422)
