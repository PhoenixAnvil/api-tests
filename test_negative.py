"""
API-SUT Negative Tests

Negative tests verify that the API handles error cases correctly,
returning appropriate error status codes and messages.
"""

import pytest
import httpx
from assertpy import assert_that


class TestGetItemByIdNegative:
    """Negative tests for GET /items/{id} endpoint."""

    def test_get_nonexistent_item_returns_404(self, client: httpx.Client):
        """GET /items/{id} should return 404 for non-existent ID."""
        response = client.get("/items/999999")
        
        assert_that(response.status_code).is_equal_to(404)

    def test_get_nonexistent_item_returns_error_detail(self, client: httpx.Client):
        """GET /items/{id} should return error detail for non-existent ID."""
        response = client.get("/items/999999")
        
        assert_that(response.json()).contains_key("detail")
        assert_that(response.json()["detail"]).contains("not found")

    def test_get_item_with_zero_id_returns_404(self, client: httpx.Client):
        """GET /items/0 should return 404 (no item with ID 0)."""
        response = client.get("/items/0")
        
        assert_that(response.status_code).is_equal_to(404)

    def test_get_item_with_negative_id_returns_error(self, client: httpx.Client):
        """GET /items/{negative_id} should return an error."""
        response = client.get("/items/-1")
        
        # FastAPI may return 404 or 422 depending on validation
        assert_that(response.status_code).is_in(404, 422)

    def test_get_item_with_string_id_returns_422(self, client: httpx.Client):
        """GET /items/{string_id} should return 422 for non-integer ID."""
        response = client.get("/items/abc")
        
        assert_that(response.status_code).is_equal_to(422)

    def test_get_item_with_float_id_returns_422(self, client: httpx.Client):
        """GET /items/{float_id} should return 422 for float ID."""
        response = client.get("/items/1.5")
        
        assert_that(response.status_code).is_equal_to(422)

    def test_get_deleted_item_returns_404(self, client: httpx.Client, valid_item_payload: dict):
        """GET /items/{id} should return 404 for a deleted item."""
        # Create and then delete an item
        created = client.post("/items", json=valid_item_payload).json()
        client.delete(f"/items/{created['id']}")
        
        # Try to retrieve the deleted item
        response = client.get(f"/items/{created['id']}")
        
        assert_that(response.status_code).is_equal_to(404)


class TestCreateItemNegative:
    """Negative tests for POST /items endpoint."""

    def test_create_item_without_body_returns_422(self, client: httpx.Client):
        """POST /items without body should return 422."""
        response = client.post("/items")
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_empty_body_returns_422(self, client: httpx.Client):
        """POST /items with empty body should return 422."""
        response = client.post("/items", json={})
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_missing_name_returns_422(self, client: httpx.Client):
        """POST /items missing required 'name' field should return 422."""
        payload = {"price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_missing_price_returns_422(self, client: httpx.Client):
        """POST /items missing required 'price' field should return 422."""
        payload = {"name": "Test Item", "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_missing_quantity_returns_422(self, client: httpx.Client):
        """POST /items missing required 'quantity' field should return 422."""
        payload = {"name": "Test Item", "price": 10.00}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_zero_price_returns_422(self, client: httpx.Client):
        """POST /items with price of 0 should return 422 (price must be > 0)."""
        payload = {"name": "Zero Price Item", "price": 0, "quantity": 10}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_negative_price_returns_422(self, client: httpx.Client):
        """POST /items with negative price should return 422."""
        payload = {"name": "Negative Price Item", "price": -10.00, "quantity": 10}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_negative_quantity_returns_422(self, client: httpx.Client):
        """POST /items with negative quantity should return 422."""
        payload = {"name": "Negative Quantity Item", "price": 10.00, "quantity": -5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_string_price_returns_422(self, client: httpx.Client):
        """POST /items with string price should return 422."""
        payload = {"name": "String Price Item", "price": "ten dollars", "quantity": 10}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_string_quantity_returns_422(self, client: httpx.Client):
        """POST /items with string quantity should return 422."""
        payload = {"name": "String Quantity Item", "price": 10.00, "quantity": "five"}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_array_name_returns_422(self, client: httpx.Client):
        """POST /items with array as name should return 422."""
        payload = {"name": ["Item1", "Item2"], "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_object_name_returns_422(self, client: httpx.Client):
        """POST /items with object as name should return 422."""
        payload = {"name": {"first": "Item"}, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_returns_validation_error_details(self, client: httpx.Client):
        """POST /items should return detailed validation error information."""
        payload = {}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)
        error_response = response.json()
        assert_that(error_response).contains_key("detail")
        assert_that(error_response["detail"]).is_instance_of(list)


class TestUpdateItemNegative:
    """Negative tests for PUT /items/{id} endpoint."""

    def test_update_nonexistent_item_returns_404(self, client: httpx.Client, valid_item_payload: dict):
        """PUT /items/{id} should return 404 for non-existent ID."""
        response = client.put("/items/999999", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(404)

    def test_update_item_without_body_returns_422(self, client: httpx.Client, create_test_item):
        """PUT /items/{id} without body should return 422."""
        item = create_test_item()
        
        response = client.put(f"/items/{item['id']}")
        
        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_with_empty_body_returns_422(self, client: httpx.Client, create_test_item):
        """PUT /items/{id} with empty body should return 422."""
        item = create_test_item()
        
        response = client.put(f"/items/{item['id']}", json={})
        
        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_missing_required_field_returns_422(self, client: httpx.Client, create_test_item):
        """PUT /items/{id} missing required field should return 422."""
        item = create_test_item()
        incomplete_payload = {"name": "Updated Name", "price": 20.00}  # Missing quantity
        
        response = client.put(f"/items/{item['id']}", json=incomplete_payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_with_invalid_price_returns_422(self, client: httpx.Client, create_test_item):
        """PUT /items/{id} with invalid price should return 422."""
        item = create_test_item()
        invalid_payload = {"name": "Test", "price": -10.00, "quantity": 5}
        
        response = client.put(f"/items/{item['id']}", json=invalid_payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_update_item_with_string_id_returns_422(self, client: httpx.Client, valid_item_payload: dict):
        """PUT /items/{string_id} should return 422 for non-integer ID."""
        response = client.put("/items/abc", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_update_deleted_item_returns_404(self, client: httpx.Client, valid_item_payload: dict):
        """PUT /items/{id} should return 404 for a deleted item."""
        # Create and delete an item
        created = client.post("/items", json=valid_item_payload).json()
        client.delete(f"/items/{created['id']}")
        
        # Try to update the deleted item
        response = client.put(f"/items/{created['id']}", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(404)


class TestDeleteItemNegative:
    """Negative tests for DELETE /items/{id} endpoint."""

    def test_delete_nonexistent_item_returns_404(self, client: httpx.Client):
        """DELETE /items/{id} should return 404 for non-existent ID."""
        response = client.delete("/items/999999")
        
        assert_that(response.status_code).is_equal_to(404)

    def test_delete_item_with_string_id_returns_422(self, client: httpx.Client):
        """DELETE /items/{string_id} should return 422 for non-integer ID."""
        response = client.delete("/items/abc")
        
        assert_that(response.status_code).is_equal_to(422)

    def test_delete_item_twice_returns_404(self, client: httpx.Client, valid_item_payload: dict):
        """DELETE /items/{id} twice should return 404 on second attempt."""
        # Create an item
        created = client.post("/items", json=valid_item_payload).json()
        
        # Delete it once - should succeed
        first_delete = client.delete(f"/items/{created['id']}")
        assert_that(first_delete.status_code).is_equal_to(204)
        
        # Delete it again - should return 404
        second_delete = client.delete(f"/items/{created['id']}")
        assert_that(second_delete.status_code).is_equal_to(404)

    def test_delete_item_with_zero_id_returns_404(self, client: httpx.Client):
        """DELETE /items/0 should return 404."""
        response = client.delete("/items/0")
        
        assert_that(response.status_code).is_equal_to(404)

    def test_delete_item_with_negative_id_returns_error(self, client: httpx.Client):
        """DELETE /items/{negative_id} should return an error."""
        response = client.delete("/items/-1")
        
        assert_that(response.status_code).is_in(404, 422)


class TestInvalidHTTPMethods:
    """Tests for invalid HTTP methods on endpoints."""

    def test_patch_items_returns_405(self, client: httpx.Client, create_test_item, valid_item_payload: dict):
        """PATCH /items/{id} should return 405 Method Not Allowed."""
        item = create_test_item()
        
        response = client.patch(f"/items/{item['id']}", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(405)

    def test_put_on_items_collection_returns_405(self, client: httpx.Client, valid_item_payload: dict):
        """PUT /items (without ID) should return 405 Method Not Allowed."""
        response = client.put("/items", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(405)

    def test_delete_on_items_collection_returns_405(self, client: httpx.Client):
        """DELETE /items (without ID) should return 405 Method Not Allowed."""
        response = client.delete("/items")
        
        assert_that(response.status_code).is_equal_to(405)

    def test_post_on_specific_item_returns_405(self, client: httpx.Client, create_test_item, valid_item_payload: dict):
        """POST /items/{id} should return 405 Method Not Allowed."""
        item = create_test_item()
        
        response = client.post(f"/items/{item['id']}", json=valid_item_payload)
        
        assert_that(response.status_code).is_equal_to(405)


class TestInvalidEndpoints:
    """Tests for invalid/non-existent endpoints."""

    def test_nonexistent_endpoint_returns_404(self, client: httpx.Client):
        """Request to non-existent endpoint should return 404."""
        response = client.get("/nonexistent")
        
        assert_that(response.status_code).is_equal_to(404)

    def test_misspelled_items_endpoint_returns_404(self, client: httpx.Client):
        """Request to misspelled endpoint should return 404."""
        response = client.get("/item")  # Missing 's'
        
        assert_that(response.status_code).is_equal_to(404)

    def test_nested_nonexistent_endpoint_returns_404(self, client: httpx.Client):
        """Request to nested non-existent endpoint should return 404."""
        response = client.get("/items/1/details")
        
        assert_that(response.status_code).is_equal_to(404)


class TestMalformedRequests:
    """Tests for malformed request handling."""

    def test_invalid_json_body_returns_422(self, client: httpx.Client):
        """POST /items with invalid JSON should return 422."""
        response = client.post(
            "/items",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert_that(response.status_code).is_equal_to(422)

    def test_wrong_content_type_returns_422(self, client: httpx.Client, valid_item_payload: dict):
        """POST /items with wrong content type should return 422."""
        import json
        response = client.post(
            "/items",
            content=json.dumps(valid_item_payload),
            headers={"Content-Type": "text/plain"}
        )
        
        assert_that(response.status_code).is_equal_to(422)
