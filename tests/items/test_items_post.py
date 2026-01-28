"""
API-SUT Items POST Tests

Tests for the POST /items endpoint. These positive, negative, and
validation tests verify that the API behaves correctly in each behavior
category.
"""

import httpx
import pytest
from assertpy import assert_that

pytestmark = [pytest.mark.items, pytest.mark.post]


@pytest.mark.positive
class TestCreateItemPositive:
    """Positive tests for POST /items endpoint."""

    def test_create_item_returns_201(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """POST /items should return 201 Created for valid payload."""
        response = client.post("/items", json=valid_item_payload)

        assert_that(response.status_code).is_equal_to(201)

        # Cleanup
        client.delete(f"/items/{response.json()['id']}")

    def test_create_item_returns_created_item(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """POST /items should return the created item with ID."""
        response = client.post("/items", json=valid_item_payload)
        created_item = response.json()

        assert_that(created_item).contains_key("id")
        assert_that(created_item["name"]).is_equal_to(
            valid_item_payload["name"]
        )
        assert_that(created_item["price"]).is_equal_to(
            valid_item_payload["price"]
        )

        # Cleanup
        client.delete(f"/items/{created_item['id']}")

    def test_create_item_with_minimal_payload(
        self, client: httpx.Client, minimal_valid_payload: dict
    ):
        """POST /items should succeed with only required fields."""
        response = client.post("/items", json=minimal_valid_payload)

        assert_that(response.status_code).is_equal_to(201)
        created_item = response.json()
        assert_that(created_item["description"]).is_none()

        # Cleanup
        client.delete(f"/items/{created_item['id']}")

    def test_create_item_generates_timestamps(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """
        POST /items should auto-generate created_at and updated_at.
        """
        response = client.post("/items", json=valid_item_payload)
        created_item = response.json()

        assert_that(created_item).contains_key("created_at")
        assert_that(created_item).contains_key("updated_at")
        assert_that(created_item["created_at"]).is_not_none()
        assert_that(created_item["updated_at"]).is_not_none()

        # Cleanup
        client.delete(f"/items/{created_item['id']}")

    def test_create_item_generates_unique_id(
        self, client: httpx.Client, valid_item_payload: dict
    ):
        """POST /items should generate unique IDs for each item."""
        response1 = client.post("/items", json=valid_item_payload)
        response2 = client.post("/items", json=valid_item_payload)

        item1 = response1.json()
        item2 = response2.json()

        assert_that(item1["id"]).is_not_equal_to(item2["id"])

        # Cleanup
        client.delete(f"/items/{item1['id']}")
        client.delete(f"/items/{item2['id']}")

    def test_create_item_with_null_description(
        self, client: httpx.Client
    ):
        """POST /items should accept null description."""
        payload = {
            "name": "Item with null description",
            "description": None,
            "price": 10.00,
            "quantity": 5,
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
            "quantity": 0,
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
            "quantity": 10,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["price"]).is_equal_to(19.99)

        # Cleanup
        client.delete(f"/items/{response.json()['id']}")


@pytest.mark.negative
class TestCreateItemNegative:
    """Negative tests for POST /items endpoint."""

    def test_create_item_without_body_returns_422(
        self, client: httpx.Client
    ):
        """POST /items without body should return 422."""
        response = client.post("/items")

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_empty_body_returns_422(
        self, client: httpx.Client
    ):
        """POST /items with empty body should return 422."""
        response = client.post("/items", json={})

        assert_that(response.status_code).is_equal_to(422)

    @pytest.mark.parametrize(
        "missing_field", ["name", "price", "quantity"]
    )
    def test_create_item_missing_required_field_returns_422(
        self, client: httpx.Client, valid_item_payload, missing_field
    ):
        payload = dict(valid_item_payload)
        payload.pop(missing_field, None)

        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_zero_price_returns_422(
        self, client: httpx.Client
    ):
        """
        POST /items with price of 0 should return
        422 (price must be > 0).
        """
        payload = {
            "name": "Zero Price Item",
            "price": 0,
            "quantity": 10,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_negative_price_returns_422(
        self, client: httpx.Client
    ):
        """POST /items with negative price should return 422."""
        payload = {
            "name": "Negative Price Item",
            "price": -10.00,
            "quantity": 10,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_negative_quantity_returns_422(
        self, client: httpx.Client
    ):
        """POST /items with negative quantity should return 422."""
        payload = {
            "name": "Negative Quantity Item",
            "price": 10.00,
            "quantity": -5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_string_price_returns_422(
        self, client: httpx.Client
    ):
        """POST /items with string price should return 422."""
        payload = {
            "name": "String Price Item",
            "price": "ten dollars",
            "quantity": 10,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_string_quantity_returns_422(
        self, client: httpx.Client
    ):
        """POST /items with string quantity should return 422."""
        payload = {
            "name": "String Quantity Item",
            "price": 10.00,
            "quantity": "five",
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_array_name_returns_422(
        self, client: httpx.Client
    ):
        """POST /items with array as name should return 422."""
        payload = {
            "name": ["Item1", "Item2"],
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_with_object_name_returns_422(
        self, client: httpx.Client
    ):
        """POST /items with object as name should return 422."""
        payload = {
            "name": {"first": "Item"},
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_create_item_returns_validation_error_details(
        self, client: httpx.Client
    ):
        """
        POST /items should return detailed validation error information.
        """
        payload = {}
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)
        error_response = response.json()
        assert_that(error_response).contains_key("detail")
        assert_that(error_response["detail"]).is_instance_of(list)


@pytest.mark.validation
class TestNameFieldValidation:
    """Validation tests for the 'name' field."""

    # Minimum length tests
    def test_name_with_single_character_is_valid(
        self, client: httpx.Client
    ):
        """Name with 1 character (minimum) should be accepted."""
        payload = {"name": "A", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_empty_string_returns_422(
        self, client: httpx.Client
    ):
        """Empty name should return 422 (min_length=1)."""
        payload = {"name": "", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    # Maximum length tests
    def test_name_with_100_characters_is_valid(
        self, client: httpx.Client
    ):
        """
        Name with exactly 100 characters (maximum) should be accepted.
        """
        long_name = "A" * 100
        payload = {"name": long_name, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["name"]).is_equal_to(long_name)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_101_characters_returns_422(
        self, client: httpx.Client
    ):
        """Name with 101 characters (exceeds max) should return 422."""
        long_name = "A" * 101
        payload = {"name": long_name, "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_name_with_200_characters_returns_422(
        self, client: httpx.Client
    ):
        """Name significantly over max length should return 422."""
        very_long_name = "A" * 200
        payload = {
            "name": very_long_name,
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    # Data type tests
    @pytest.mark.parametrize(
        "non_string_name",
        [
            pytest.param(12345, id="name=int"),
            pytest.param(True, id="name=bool"),
            pytest.param(None, id="name=null"),
            pytest.param(123.45, id="name=float"),
        ],
    )
    def test_name_as_non_string_type_returns_422(
        self, client: httpx.Client, non_string_name
    ):
        """Name as non-string type should return 422."""
        payload = {
            "name": non_string_name,
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    # Special characters tests
    def test_name_with_special_characters_is_valid(
        self, client: httpx.Client
    ):
        """Name with special characters should be accepted."""
        payload = {
            "name": "Item!@#$%^&*()",
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["name"]).is_equal_to(
            "Item!@#$%^&*()"
        )
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_unicode_characters_is_valid(
        self, client: httpx.Client
    ):
        """Name with unicode characters should be accepted."""
        payload = {
            "name": "Café élégant 日本語",
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_emojis_is_valid(self, client: httpx.Client):
        """Name with emojis should be accepted."""
        payload = {
            "name": "Cool Item 🎉🚀",
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_leading_spaces_is_preserved(
        self, client: httpx.Client
    ):
        """Name with leading spaces should be preserved."""
        payload = {
            "name": "  Leading Spaces",
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["name"]).starts_with("  ")
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_trailing_spaces_is_preserved(
        self, client: httpx.Client
    ):
        """Name with trailing spaces should be preserved."""
        payload = {
            "name": "Trailing Spaces  ",
            "price": 10.00,
            "quantity": 5,
        }
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

    def test_name_with_newline_character_is_valid(
        self, client: httpx.Client
    ):
        """Name with newline character should be accepted."""
        payload = {
            "name": "Line1\nLine2",
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_name_with_tab_character_is_valid(
        self, client: httpx.Client
    ):
        """Name with tab character should be accepted."""
        payload = {"name": "Col1\tCol2", "price": 10.00, "quantity": 5}
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")


@pytest.mark.validation
class TestDescriptionFieldValidation:
    """Validation tests for the 'description' field."""

    def test_description_can_be_null(self, client: httpx.Client):
        """Description can be null (optional field)."""
        payload = {
            "name": "Item",
            "description": None,
            "price": 10.00,
            "quantity": 5,
        }
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

    def test_description_can_be_empty_string(
        self, client: httpx.Client
    ):
        """Description can be an empty string."""
        payload = {
            "name": "Item",
            "description": "",
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_description_with_500_characters_is_valid(
        self, client: httpx.Client
    ):
        """
        Description with exactly 500 characters should be accepted.
        """
        long_desc = "D" * 500
        payload = {
            "name": "Item",
            "description": long_desc,
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["description"]).is_equal_to(
            long_desc
        )
        client.delete(f"/items/{response.json()['id']}")

    def test_description_with_501_characters_returns_422(
        self, client: httpx.Client
    ):
        """Description exceeding 500 characters should return 422."""
        long_desc = "D" * 501
        payload = {
            "name": "Item",
            "description": long_desc,
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_description_with_special_characters_is_valid(
        self, client: httpx.Client
    ):
        """Description with special characters should be accepted."""
        special = '<script>alert("xss")</script> & "quotes" \'single\''
        payload = {
            "name": "Item",
            "description": special,
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_description_as_integer_returns_422(
        self, client: httpx.Client
    ):
        """Description as integer should return 422."""
        payload = {
            "name": "Item",
            "description": 12345,
            "price": 10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)


@pytest.mark.validation
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
        payload = {
            "name": "Refund Item",
            "price": -10.00,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_price_very_large_value_is_valid(
        self, client: httpx.Client
    ):
        """Very large price should be accepted."""
        payload = {
            "name": "Luxury Item",
            "price": 999999999.99,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    def test_price_with_many_decimal_places(self, client: httpx.Client):
        """Price with many decimal places should be accepted."""
        payload = {
            "name": "Precise Item",
            "price": 10.123456789,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    # Data type tests
    def test_price_as_integer_is_valid(self, client: httpx.Client):
        """Price as integer should be accepted (coerced to float)."""
        payload = {
            "name": "Whole Price Item",
            "price": 100,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    @pytest.mark.parametrize(
        "non_numeric_price",
        [
            pytest.param("10.00", id="price=string"),
            pytest.param(None, id="price=null"),
            pytest.param(True, id="price=bool"),
            pytest.param([10.00], id="price=array"),
        ],
    )
    def test_price_as_non_numeric_type_returns_422(
        self, client: httpx.Client, non_numeric_price
    ):
        """Price as non-numeric type should return 422."""
        payload = {
            "name": "Invalid Price Type",
            "price": non_numeric_price,
            "quantity": 5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)


@pytest.mark.validation
class TestQuantityFieldValidation:
    """Validation tests for the 'quantity' field."""

    # Boundary value tests
    def test_quantity_at_zero_is_valid(self, client: httpx.Client):
        """Quantity of 0 should be accepted (ge=0)."""
        payload = {
            "name": "Out of Stock",
            "price": 10.00,
            "quantity": 0,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        assert_that(response.json()["quantity"]).is_equal_to(0)
        client.delete(f"/items/{response.json()['id']}")

    def test_quantity_negative_returns_422(self, client: httpx.Client):
        """Negative quantity should return 422."""
        payload = {
            "name": "Negative Stock",
            "price": 10.00,
            "quantity": -1,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_very_large_value_is_valid(
        self, client: httpx.Client
    ):
        """Very large quantity should be accepted."""
        payload = {
            "name": "Bulk Item",
            "price": 10.00,
            "quantity": 999999999,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(201)
        client.delete(f"/items/{response.json()['id']}")

    # Data type tests
    def test_quantity_as_float_returns_422(self, client: httpx.Client):
        """Quantity as float should return 422 (must be integer)."""
        payload = {
            "name": "Float Qty Item",
            "price": 10.00,
            "quantity": 5.5,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_as_string_returns_422(self, client: httpx.Client):
        """Quantity as string should return 422."""
        payload = {
            "name": "String Qty Item",
            "price": 10.00,
            "quantity": "5",
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_as_null_returns_422(self, client: httpx.Client):
        """Quantity as null should return 422 (required field)."""
        payload = {
            "name": "Null Qty Item",
            "price": 10.00,
            "quantity": None,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)

    def test_quantity_as_boolean_returns_422(
        self, client: httpx.Client
    ):
        """Quantity as boolean should return 422."""
        payload = {
            "name": "Bool Qty Item",
            "price": 10.00,
            "quantity": True,
        }
        response = client.post("/items", json=payload)

        assert_that(response.status_code).is_equal_to(422)


@pytest.mark.validation
class TestConcurrentOperations:
    """Tests for handling concurrent operations."""

    def test_create_multiple_items_with_same_name(
        self, client: httpx.Client
    ):
        """
        Creating items with the same name should
        succeed (no unique constraint).
        """
        payload = {
            "name": "Duplicate Name",
            "price": 10.00,
            "quantity": 5,
        }

        response1 = client.post("/items", json=payload)
        response2 = client.post("/items", json=payload)

        assert_that(response1.status_code).is_equal_to(201)
        assert_that(response2.status_code).is_equal_to(201)
        assert_that(response1.json()["id"]).is_not_equal_to(
            response2.json()["id"]
        )

        # Cleanup
        client.delete(f"/items/{response1.json()['id']}")
        client.delete(f"/items/{response2.json()['id']}")
