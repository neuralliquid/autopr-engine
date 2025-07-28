"""Unit tests for the Linear API client."""

import json
import os
from unittest import TestCase, mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientResponseError, ClientSession

from autopr.clients.linear_client import LinearClient


class TestLinearClient(TestCase):
    """Test cases for the Linear API client."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.client = LinearClient(api_key=self.api_key)
        self.mock_response = {"data": {"test": "success"}}

    def test_init_without_api_key(self):
        """Test initialization without an API key falls back to environment variable."""
        with mock.patch.dict(os.environ, {"LINEAR_API_KEY": "env_api_key"}):
            client = LinearClient()
            self.assertEqual(client.headers["Authorization"], "Bearer env_api_key")

    def test_init_with_api_key(self):
        """Test initialization with an explicit API key."""
        self.assertEqual(self.client.headers["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(self.client.base_url, "https://api.linear.app/graphql")
        self.assertEqual(self.client.headers["Content-Type"], "application/json")

    @pytest.mark.asyncio
    async def test_query_success(self):
        """Test successful GraphQL query."""
        query = """
        query {
            issues {
                nodes {
                    id
                    title
                }
            }
        }
        """

        with patch("aiohttp.ClientSession.post") as mock_post:
            # Set up the mock response
            mock_resp = AsyncMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = self.mock_response
            mock_post.return_value.__aenter__.return_value = mock_resp

            # Make the request
            result = await self.client.query(query)

            # Verify the request was made correctly
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs["url"], self.client.base_url)
            self.assertEqual(kwargs["headers"], self.client.headers)
            self.assertEqual(json.loads(kwargs["json"]["query"]), query.strip())

            # Verify the response was handled correctly
            self.assertEqual(result, self.mock_response["data"])

    @pytest.mark.asyncio
    async def test_query_with_variables(self):
        """Test query with variables."""
        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                title
            }
        }
        """
        variables = {"id": "test-123"}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_resp = AsyncMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = self.mock_response
            mock_post.return_value.__aenter__.return_value = mock_resp

            result = await self.client.query(query, variables=variables)

            # Verify variables were included in the request
            request_data = json.loads(mock_post.call_args[1]["json"])
            self.assertEqual(request_data["variables"], variables)
            self.assertEqual(result, self.mock_response["data"])

    @pytest.mark.asyncio
    async def test_query_http_error(self):
        """Test handling of HTTP errors."""
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_resp = AsyncMock()
            mock_resp.raise_for_status.side_effect = ClientResponseError(
                request_info=None, history=None, status=500, message="Internal Server Error"
            )
            mock_post.return_value.__aenter__.return_value = mock_resp

            with self.assertRaises(ClientResponseError):
                await self.client.query("query { test }")

    @pytest.mark.asyncio
    async def test_query_graphql_errors(self):
        """Test handling of GraphQL errors."""
        error_response = {"errors": [{"message": "Unauthorized"}, {"message": "Invalid query"}]}

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_resp = AsyncMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = error_response
            mock_post.return_value.__aenter__.return_value = mock_resp

            with self.assertRaises(Exception) as context:
                await self.client.query("query { invalid }")

            self.assertIn("Linear API error: Unauthorized, Invalid query", str(context.exception))

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client can be used as a context manager."""
        async with LinearClient(api_key=self.api_key) as client:
            self.assertIsInstance(client, LinearClient)
            self.assertIsInstance(client.session, ClientSession)
        # Session should be closed after context manager exits
        self.assertTrue(client.session.closed)
