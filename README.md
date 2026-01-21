# API-SUT Test Suite

A comprehensive test suite for the API-SUT (API System Under Test) using pytest and assertpy.

## Overview

This test suite is designed to thoroughly test the API-SUT CRUD API, covering:

- **Smoke Tests**: Basic health checks and connectivity tests
- **Positive Tests**: Happy path scenarios for all CRUD operations
- **Negative Tests**: Error handling and edge cases
- **Validation Tests**: Input validation, data types, boundaries, and special characters

## Test Files

All test files are prefixed with `api_sut_tests_` for easy identification when moving to a separate repository:

| File | Description | Test Count |
|------|-------------|------------|
| `api_sut_tests_conftest.py` | Pytest fixtures and configuration | N/A |
| `api_sut_tests_smoke.py` | Smoke tests for basic API health | ~12 tests |
| `api_sut_tests_positive.py` | Positive/happy path tests | ~35 tests |
| `api_sut_tests_negative.py` | Negative/error case tests | ~40 tests |
| `api_sut_tests_validation.py` | Input validation tests | ~55 tests |
| `api_sut_tests_requirements.txt` | Test dependencies | N/A |
| `api_sut_tests_README.md` | This documentation | N/A |

## Requirements

- Python 3.11+
- pytest 8.0.0
- assertpy 1.1
- httpx 0.26.0
- requests 2.31.0

## Installation

1. Install test dependencies:
   ```bash
   pip install -r api_sut_tests_requirements.txt
   ```

2. Ensure the API is running:
   ```bash
   uvicorn main:app --reload
   ```

## Running Tests

### Run All Tests
```bash
pytest api_sut_tests_*.py -v
```

### Run Specific Test Categories
```bash
# Smoke tests only
pytest api_sut_tests_smoke.py -v

# Positive tests only
pytest api_sut_tests_positive.py -v

# Negative tests only
pytest api_sut_tests_negative.py -v

# Validation tests only
pytest api_sut_tests_validation.py -v
```

### Run Tests with HTML Report
```bash
pytest api_sut_tests_*.py -v --html=report.html --self-contained-html
```

### Run Tests by Marker/Class
```bash
# Run all tests in a specific class
pytest api_sut_tests_positive.py::TestCreateItem -v

# Run a specific test
pytest api_sut_tests_positive.py::TestCreateItem::test_create_item_returns_201 -v
```

### Run Tests in Parallel (requires pytest-xdist)
```bash
pip install pytest-xdist
pytest api_sut_tests_*.py -v -n auto
```

## Test Categories Explained

### Smoke Tests (`api_sut_tests_smoke.py`)
Quick tests to verify the API is operational:
- Root endpoint accessibility
- Health check endpoint
- Swagger documentation availability
- Demo data is pre-loaded
- Basic CRUD operations work

### Positive Tests (`api_sut_tests_positive.py`)
Happy path scenarios:
- GET all items returns list
- GET single item by ID
- POST creates item with correct response
- PUT updates item properly
- DELETE removes item
- Correct HTTP status codes (200, 201, 204)
- Response structure validation

### Negative Tests (`api_sut_tests_negative.py`)
Error handling scenarios:
- 404 for non-existent items
- 422 for validation errors
- 405 for invalid HTTP methods
- Missing required fields
- Invalid data types
- Malformed JSON requests
- Double delete attempts

### Validation Tests (`api_sut_tests_validation.py`)
Input validation coverage:

**Name Field:**
- Min length (1 character)
- Max length (100 characters)
- Empty string rejection
- Data type validation
- Special characters
- Unicode/emoji support
- Whitespace handling

**Description Field:**
- Optional/null handling
- Max length (500 characters)
- Special characters

**Price Field:**
- Must be > 0
- Boundary values (0.01, 0, negative)
- Large values
- Decimal precision
- Data type validation

**Quantity Field:**
- Must be >= 0
- Integer validation
- Large values
- Data type validation

**Response Schema:**
- Correct field types
- Error response structure
- Validation error details

## Moving to a Separate Repository

To move these tests to a dedicated test repository:

1. Copy all files prefixed with `api_sut_tests_`:
   ```bash
   # On Windows
   copy api_sut_tests_* path\to\new\repo\
   
   # On macOS/Linux
   cp api_sut_tests_* /path/to/new/repo/
   ```

2. Rename files in the new repo (optional):
   ```bash
   # Remove prefix for cleaner structure
   mv api_sut_tests_requirements.txt requirements.txt
   mv api_sut_tests_conftest.py conftest.py
   mv api_sut_tests_smoke.py test_smoke.py
   mv api_sut_tests_positive.py test_positive.py
   mv api_sut_tests_negative.py test_negative.py
   mv api_sut_tests_validation.py test_validation.py
   mv api_sut_tests_README.md README.md
   ```

3. Update the `BASE_URL` in `conftest.py` to point to your deployed API:
   ```python
   BASE_URL = "https://your-api-url.azurewebsites.net"
   ```

## Configuration

### Changing API Base URL

Edit `api_sut_tests_conftest.py`:

```python
# Default local development
BASE_URL = "http://127.0.0.1:8000"

# Azure deployment
BASE_URL = "https://api-sut.azurewebsites.net"
```

### Environment Variable Support (Optional Enhancement)

You can modify `conftest.py` to use environment variables:

```python
import os
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
```

Then run tests with:
```bash
API_BASE_URL=https://your-api.com pytest api_sut_tests_*.py -v
```

## Test Fixtures

The `api_sut_tests_conftest.py` file provides several reusable fixtures:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `base_url` | session | Returns the API base URL |
| `client` | session | HTTP client for API requests |
| `valid_item_payload` | function | Valid item payload for tests |
| `minimal_valid_payload` | function | Minimal valid payload (required fields only) |
| `create_test_item` | function | Factory to create test items with auto-cleanup |
| `sample_items` | function | List of sample item payloads |

## Assertions Library

This test suite uses **assertpy** for readable and expressive assertions:

```python
from assertpy import assert_that

# Value assertions
assert_that(response.status_code).is_equal_to(200)
assert_that(items).is_not_empty()
assert_that(item["price"]).is_greater_than(0)

# String assertions
assert_that(message).contains("success")
assert_that(name).starts_with("Item")

# Collection assertions
assert_that(response.json()).contains_key("id")
assert_that(items).is_instance_of(list)
```

## License

MIT License - see the main repository LICENSE file.
