"""
API-SUT Meta Smoke/Positive Tests

Smoke tests for meta endpoints. These positive tests verify that the
meta endpoints are accessible and return the expected responses.

These tests should be run first to ensure the API is healthy before
running more comprehensive tests.
"""

import httpx
import pytest
from assertpy import assert_that

pytestmark = [pytest.mark.meta, pytest.mark.smoke, pytest.mark.positive]


class TestMetaSmoke:
    """Smoke/Positive tests for meta endpoints."""

    def test_api_root_endpoint_is_accessible(
        self, client: httpx.Client
    ):
        """
        Verify the root endpoint is accessible and returns
        expected response.
        """
        response = client.get("/")

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.json()).contains_key("message")
        assert_that(response.json()["message"]).contains("API-SUT")

    def test_api_health_endpoint_returns_healthy(
        self, client: httpx.Client
    ):
        """Verify the health endpoint indicates the API is healthy."""
        response = client.get("/health")

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.json()).contains_key("message")
        assert_that(response.json()["message"]).contains("healthy")

    def test_api_docs_endpoint_is_accessible(
        self, client: httpx.Client
    ):
        """Verify the Swagger documentation endpoint is accessible."""
        response = client.get("/docs")

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.headers["content-type"]).contains(
            "text/html"
        )

    def test_api_openapi_json_is_accessible(self, client: httpx.Client):
        """Verify the OpenAPI JSON specification is accessible."""
        response = client.get("/openapi.json")

        assert_that(response.status_code).is_equal_to(200)
        openapi_spec = response.json()
        assert_that(openapi_spec).contains_key("openapi")
        assert_that(openapi_spec).contains_key("info")
        assert_that(openapi_spec["info"]["title"]).is_equal_to(
            "API-SUT"
        )


class TestHealthEndpoint:
    """Smoke/Positive tests for GET /health endpoint."""

    def test_health_returns_200(self, client: httpx.Client):
        """GET /health should return 200 OK."""
        response = client.get("/health")

        assert_that(response.status_code).is_equal_to(200)

    def test_health_returns_message(self, client: httpx.Client):
        """
        GET /health should return a message indicating health status.
        """
        response = client.get("/health")

        assert_that(response.json()).contains_key("message")
        assert_that(response.json()["message"]).is_not_empty()


class TestRootEndpoint:
    """Smoke/Positive tests for GET / endpoint."""

    def test_root_returns_200(self, client: httpx.Client):
        """GET / should return 200 OK."""
        response = client.get("/")

        assert_that(response.status_code).is_equal_to(200)

    def test_root_returns_welcome_message(self, client: httpx.Client):
        """GET / should return a welcome message."""
        response = client.get("/")

        assert_that(response.json()).contains_key("message")
        assert_that(response.json()["message"]).contains("Welcome")
