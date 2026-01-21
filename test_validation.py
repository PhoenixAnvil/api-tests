"""
API-SUT Validation Tests

Comprehensive tests for input validation including:
- Data type validation
- Min/max character limits
- Boundary value testing
- Special character handling
- Edge cases
"""

import pytest
import httpx
from assertpy import assert_that


class TestNameFieldValidation:
    """Validation tests for the 'name' field."""

    # Minimum length tests
    def test_name_with_single_character_is_valid(self, client: httpx.Client):
        """Name with 1 character (minimum) should be accepted."""
        payload = {"name": "A", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_empty_string_returns_422(self, client: httpx.Client):
        """Empty name should return 422 (min_length=1)."""
        payload = {"name": "", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    # Maximum length tests
    def test_name_with_100_characters_is_valid(self, client: httpx.Client):
        """Name with exactly 100 characters (maximum) should be accepted."""
        long_name = "A" * 100
        payload = {"name": long_name, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["name"]).is_equal_to(long_name)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_101_characters_returns_422(self, client: httpx.Client):
        """Name with 101 characters (exceeds max) should return 422."""
        long_name = "A" * 101
        payload = {"name": long_name, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_name_with_200_characters_returns_422(self, client: httpx.Client):
        """Name significantly over max length should return 422."""
        very_long_name = "A" * 200
        payload = {"name": very_long_name, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    # Data type tests
    def test_name_as_integer_returns_422(self, client: httpx.Client):
        """Name as integer should return 422."""
        payload = {"name": 12345, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_name_as_boolean_returns_422(self, client: httpx.Client):
        """Name as boolean should return 422."""
        payload = {"name": True, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_name_as_null_returns_422(self, client: httpx.Client):
        """Name as null should return 422 (required field)."""
        payload = {"name": None, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_name_as_float_returns_422(self, client: httpx.Client):
        """Name as float should return 422."""
        payload = {"name": 123.45, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    # Special characters tests
    def test_name_with_special_characters_is_valid(self, client: httpx.Client):
        """Name with special characters should be accepted."""
        payload = {"name": "Item!@#$%^&*()", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["name"]).is_equal_to("Item!@#$%^&*()")
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_unicode_characters_is_valid(self, client: httpx.Client):
        """Name with unicode characters should be accepted."""
        payload = {"name": "Café élégant 日本語", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_emojis_is_valid(self, client: httpx.Client):
        """Name with emojis should be accepted."""
        payload = {"name": "Cool Item 🎉🚀", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_leading_spaces_is_preserved(self, client: httpx.Client):
        """Name with leading spaces should be preserved."""
        payload = {"name": "  Leading Spaces", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["name"]).starts_with("  ")
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_trailing_spaces_is_preserved(self, client: httpx.Client):
        """Name with trailing spaces should be preserved."""
        payload = {"name": "Trailing Spaces  ", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["name"]).ends_with("  ")
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_only_spaces_is_valid(self, client: httpx.Client):
        """Name with only spaces should be valid (length >= 1)."""
        payload = {"name": "   ", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_newline_character_is_valid(self, client: httpx.Client):
        """Name with newline character should be accepted."""
        payload = {"name": "Line1\nLine2", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_tab_character_is_valid(self, client: httpx.Client):
        """Name with tab character should be accepted."""
        payload = {"name": "Col1\tCol2", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")


class TestDescriptionFieldValidation:
    """Validation tests for the 'description' field."""

    def test_description_can_be_null(self, client: httpx.Client):
        """Description can be null (optional field)."""
        payload = {"name": "Item", "description": None, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["description"]).is_none()
        client.delete(f"/items/{response.json()['id']}")

    def test_description_can_be_omitted(self, client: httpx.Client):
        """Description can be omitted entirely."""
        payload = {"name": "Item", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_description_can_be_empty_string(self, client: httpx.Client):
        """Description can be an empty string."""
        payload = {"name": "Item", "description": "", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_description_with_500_characters_is_valid(self, client: httpx.Client):
        """Description with exactly 500 characters should be accepted."""
        long_desc = "D" * 500
        payload = {"name": "Item", "description": long_desc, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["description"]).is_equal_to(long_desc)
        client.delete(f"/items/{response.json()['id']}")

    def test_description_with_501_characters_returns_422(self, client: httpx.Client):
        """Description exceeding 500 characters should return 422."""
        long_desc = "D" * 501
        payload = {"name": "Item", "description": long_desc, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_description_with_special_characters_is_valid(self, client: httpx.Client):
        """Description with special characters should be accepted."""
        payload = {
            "name": "Item",
            "description": "<script>alert('xss')</script> & \"quotes\" 'single'",
            "price": 10.00,
            "quantity": 5
        }
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_description_as_integer_returns_422(self, client: httpx.Client):
        """Description as integer should return 422."""
        payload = {"name": "Item", "description": 12345, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)


class TestPriceFieldValidation:
    """Validation tests for the 'price' field."""

    # Boundary value tests
    def test_price_at_minimum_valid_value(self, client: httpx.Client):
        """Price just above 0 should be accepted."""
        payload = {"name": "Cheap Item", "price": 0.01, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["price"]).is_equal_to(0.01)
        client.delete(f"/items/{response.json()['id']}")

    def test_price_at_zero_returns_422(self, client: httpx.Client):
        """Price of exactly 0 should return 422 (must be > 0)."""
        payload = {"name": "Free Item", "price": 0, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_price_negative_returns_422(self, client: httpx.Client):
        """Negative price should return 422."""
        payload = {"name": "Refund Item", "price": -10.00, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_price_very_large_value_is_valid(self, client: httpx.Client):
        """Very large price should be accepted."""
        payload = {"name": "Luxury Item", "price": 999999999.99, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_price_with_many_decimal_places(self, client: httpx.Client):
        """Price with many decimal places should be accepted."""
        payload = {"name": "Precise Item", "price": 10.123456789, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    # Data type tests
    def test_price_as_integer_is_valid(self, client: httpx.Client):
        """Price as integer should be accepted (coerced to float)."""
        payload = {"name": "Whole Price Item", "price": 100, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_price_as_string_returns_422(self, client: httpx.Client):
        """Price as string should return 422."""
        payload = {"name": "String Price Item", "price": "10.00", "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_price_as_null_returns_422(self, client: httpx.Client):
        """Price as null should return 422 (required field)."""
        payload = {"name": "Null Price Item", "price": None, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_price_as_boolean_returns_422(self, client: httpx.Client):
        """Price as boolean should return 422."""
        payload = {"name": "Bool Price Item", "price": True, "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_price_as_array_returns_422(self, client: httpx.Client):
        """Price as array should return 422."""
        payload = {"name": "Array Price Item", "price": [10.00], "quantity": 5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)


class TestQuantityFieldValidation:
    """Validation tests for the 'quantity' field."""

    # Boundary value tests
    def test_quantity_at_zero_is_valid(self, client: httpx.Client):
        """Quantity of 0 should be accepted (ge=0)."""
        payload = {"name": "Out of Stock", "price": 10.00, "quantity": 0}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["quantity"]).is_equal_to(0)
        client.delete(f"/items/{response.json()['id']}")

    def test_quantity_negative_returns_422(self, client: httpx.Client):
        """Negative quantity should return 422."""
        payload = {"name": "Negative Stock", "price": 10.00, "quantity": -1}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_very_large_value_is_valid(self, client: httpx.Client):
        """Very large quantity should be accepted."""
        payload = {"name": "Bulk Item", "price": 10.00, "quantity": 999999999}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    # Data type tests
    def test_quantity_as_float_returns_422(self, client: httpx.Client):
        """Quantity as float should return 422 (must be integer)."""
        payload = {"name": "Float Qty Item", "price": 10.00, "quantity": 5.5}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_as_string_returns_422(self, client: httpx.Client):
        """Quantity as string should return 422."""
        payload = {"name": "String Qty Item", "price": 10.00, "quantity": "5"}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_as_null_returns_422(self, client: httpx.Client):
        """Quantity as null should return 422 (required field)."""
        payload = {"name": "Null Qty Item", "price": 10.00, "quantity": None}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_as_boolean_returns_422(self, client: httpx.Client):
        """Quantity as boolean should return 422."""
        payload = {"name": "Bool Qty Item", "price": 10.00, "quantity": True}
        response = client.post("/items", json=payload)
        
        assert_that(response.status_code).is_equal_to(422)


class TestIdFieldValidation:
    """Validation tests for the 'id' path parameter."""

    def test_id_as_very_large_integer(self, client: httpx.Client):
        """Very large ID should return 404 (not found, not validation error)."""
        response = client.get("/items/9999999999999")
        
        assert_that(response.status_code).is_equal_to(404)

    def test_id_with_leading_zeros(self, client: httpx.Client, create_test_item):
        """ID with leading zeros should be parsed correctly."""
        item = create_test_item()
        item_id = item["id"]
        
        # Leading zeros are typically stripped by the URL parser
        response = client.get(f"/items/0{item_id}")
        
        # Behavior depends on implementation - could be 404 or match the item
        assert_that(response.status_code).is_in(200, 404)

    def test_id_as_special_characters_returns_422(self, client: httpx.Client):
        """ID with special characters should return 422."""
        response = client.get("/items/!@#$%")
        
        assert_that(response.status_code).is_equal_to(422)

    def test_id_as_empty_returns_error(self, client: httpx.Client):
        """Empty ID in URL should be handled (typically redirects or 404)."""
        response = client.get("/items/")
        
        # This typically matches the GET /items endpoint
        assert_that(response.status_code).is_in(200, 307)  # May redirect to /items


class TestUpdateValidation:
    """Validation tests specific to PUT /items/{id} endpoint."""

    def test_update_preserves_id_even_if_provided_in_body(self, client: httpx.Client, create_test_item):
        """ID in request body should be ignored; path ID is used."""
        item = create_test_item()
        original_id = item["id"]
        
        # Try to change ID via body (should be ignored)
        update_payload = {
            "id": 99999,  # Should be ignored
            "name": "Updated Item",
            "price": 20.00,
            "quantity": 10
        }
        
        response = client.put(f"/items/{original_id}", json=update_payload)
        
        # Request might succeed (extra field ignored) or fail (422)
        if response.status_code == 200:
            assert_that(response.json()["id"]).is_equal_to(original_id)

    def test_update_with_extra_fields_in_body(self, client: httpx.Client, create_test_item):
        """Extra fields in request body should be ignored."""
        item = create_test_item()
        
        update_payload = {
            "name": "Updated Item",
            "price": 20.00,
            "quantity": 10,
            "extra_field": "should be ignored",
            "another_extra": 12345
        }
        
        response = client.put(f"/items/{item['id']}", json=update_payload)
        
        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.json()).does_not_contain_key("extra_field")


class TestResponseSchemaValidation:
    """Tests to validate response schema structure."""

    def test_item_response_has_correct_types(self, client: httpx.Client, create_test_item):
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

    def test_error_response_has_detail_field(self, client: httpx.Client):
        """Error responses should have a 'detail' field."""
        response = client.get("/items/999999")
        
        assert_that(response.status_code).is_equal_to(404)
        assert_that(response.json()).contains_key("detail")

    def test_validation_error_has_detailed_info(self, client: httpx.Client):
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


class TestConcurrentOperations:
    """Tests for handling concurrent operations."""

    def test_create_multiple_items_with_same_name(self, client: httpx.Client):
        """Creating items with the same name should succeed (no unique constraint)."""
        payload = {"name": "Duplicate Name", "price": 10.00, "quantity": 5}
        
        response1 = client.post("/items", json=payload)
        response2 = client.post("/items", json=payload)
        
        assert_that(response1.status_code).is_equal_to(201)
        assert_that(response2.status_code).is_equal_to(201)
        assert_that(response1.json()["id"]).is_not_equal_to(response2.json()["id"])
        
        # Cleanup
        client.delete(f"/items/{response1.json()['id']}")
        client.delete(f"/items/{response2.json()['id']}")
