"""Unit tests for the GitHub API client with retry logic and rate limiting."""

import asyncio
import os
import time
from datetime import datetime, timedelta, timezone
from unittest import TestCase, mock
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from aiohttp import ClientError, ClientResponseError, ClientSession, ClientTimeout

from autopr.clients.github_client import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    GitHubClient,
    GitHubConfig,
    GitHubError,
    RateLimitExceeded,
)


class TestGitHubClient(TestCase):
    """Test cases for the GitHub API client with retry logic and rate limiting."""

    def setUp(self):
        """Set up test fixtures."""
        self.token = "test_token"
        self.config = GitHubConfig(
            token=self.token,
            base_url="https://api.github.com",
            timeout=30,
            max_retries=3,
            backoff_factor=0.1,  # Shorter backoff for testing
            user_agent="Test-Agent/1.0",
        )
        self.client = GitHubClient(config=self.config)
        self.base_url = "https://api.github.com"
        self.mock_response = {"test": "success"}
        self.rate_limit_headers = {
            "X-RateLimit-Limit": "5000",
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": str(int(time.time()) + 3600),
        }

    def test_init_with_config(self):
        """Test initialization with a config object."""
        self.assertEqual(self.client.config.token, self.token)
        self.assertEqual(self.client.config.base_url, "https://api.github.com")
        self.assertEqual(self.client.config.timeout, 30)
        self.assertEqual(self.client.config.max_retries, 3)
        self.assertEqual(self.client.config.backoff_factor, 0.1)
        self.assertEqual(self.client.config.user_agent, "Test-Agent/1.0")

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful request with retry logic."""
        endpoint = "/test/endpoint"
        params = {"param1": "value1"}

        # Create a mock session with a successful response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = self.rate_limit_headers
        mock_response.json.return_value = self.mock_response

        # Set up the session mock to return our mock response
        mock_session.request.return_value.__aenter__.return_value = mock_response

        # Patch _get_session to return our mock session
        with patch.object(
            self.client, "_get_session", return_value=mock_session
        ) as mock_get_session:
            # Make the request
            result = await self.client._request("GET", endpoint, params=params)

            # Verify the request was made correctly
            mock_session.request.assert_called_once()
            args, kwargs = mock_session.request.call_args
            self.assertEqual(args[0], "GET")
            self.assertTrue(args[1].endswith(endpoint))
            self.assertEqual(kwargs["params"], params)

            # Verify the response was handled correctly
            self.assertEqual(result, self.mock_response)

            # Verify rate limit info was updated
            self.assertEqual(self.client.rate_limit_remaining, 4999)

            # Verify session was used properly
            mock_get_session.assert_called_once()
            mock_response.json.assert_called_once()
            mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self):
        """Test that the client retries on transient failures."""
        endpoint = "/test/endpoint"

        # Create a mock session that fails once then succeeds
        mock_session = AsyncMock()

        # First request fails with a connection error
        error_response = ClientError("Connection error")
        success_response = AsyncMock()
        success_response.status = 200
        success_response.headers = self.rate_limit_headers
        success_response.json.return_value = self.mock_response

        # Set up side effect to fail once then succeed
        mock_session.request.side_effect = [error_response, success_response]

        # Patch _get_session and sleep
        with patch.object(self.client, "_get_session", return_value=mock_session):
            with patch("asyncio.sleep") as mock_sleep:
                # Make the request
                result = await self.client.get(endpoint)

                # Verify it retried
                self.assertEqual(mock_session.request.call_count, 2)
                mock_sleep.assert_called_once()
                self.assertEqual(result, self.mock_response)

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test that the client handles rate limits properly."""
        endpoint = "/test/endpoint"
        reset_time = int(time.time()) + 1  # 1 second in future

        # Create a mock session
        mock_session = AsyncMock()

        # First response is rate limited
        rate_limit_response = AsyncMock()
        rate_limit_response.status = 403
        rate_limit_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_time),
            "Retry-After": "1",
        }
        rate_limit_response.raise_for_status.side_effect = ClientResponseError(
            request_info=None, history=None, status=403, message="API rate limit exceeded"
        )

        # Second response is successful
        success_response = AsyncMock()
        success_response.status = 200
        success_response.headers = self.rate_limit_headers
        success_response.json.return_value = self.mock_response

        # Set up side effects
        mock_session.request.side_effect = [rate_limit_response, success_response]

        # Patch _get_session and sleep
        with patch.object(self.client, "_get_session", return_value=mock_session):
            with patch("asyncio.sleep") as mock_sleep:
                # Make the request
                result = await self.client.get(endpoint)

                # Verify it waited for rate limit and retried
                self.assertEqual(mock_session.request.call_count, 2)
                mock_sleep.assert_called_once()
                self.assertEqual(result, self.mock_response)

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that the client gives up after max retries."""
        endpoint = "/test/endpoint"

        # Create a mock session that always fails
        mock_session = AsyncMock()
        error = ClientError("Connection error")
        mock_session.request.side_effect = error

        # Patch _get_session
        with patch.object(self.client, "_get_session", return_value=mock_session):
            with patch("asyncio.sleep"):
                # Make the request and expect it to fail
                with self.assertRaises(ClientError):
                    await self.client.get(endpoint)

                # Verify it retried the correct number of times
                self.assertEqual(mock_session.request.call_count, self.config.max_retries + 1)

    @pytest.mark.asyncio
    async def test_graphql_query(self):
        """Test GraphQL query execution."""
        query = """
        query {
            repository(owner:"test", name:"repo") {
                id
                name
            }
        }
        """

        expected_response = {"data": {"repository": {"id": "R_123", "name": "repo"}}}

        # Mock the post method
        with patch.object(self.client, "post", return_value=expected_response) as mock_post:
            # Execute the GraphQL query
            result = await self.client.graphql(query)

            # Verify the request was made correctly
            mock_post.assert_called_once_with("/graphql", data={"query": query, "variables": None})

            # Verify the result
            self.assertEqual(result, expected_response["data"])

    @pytest.mark.asyncio
    async def test_graphql_errors(self):
        """Test GraphQL query with errors."""
        query = "INVALID_QUERY"
        error_response = {"errors": [{"message": "Syntax Error: Expected Name, found '}'"}]}

        # Mock the post method to return an error
        with patch.object(self.client, "post", return_value=error_response):
            # Execute the GraphQL query and expect an error
            with self.assertRaises(GitHubError) as context:
                await self.client.graphql(query)

            # Verify the error message
            self.assertIn("Syntax Error", str(context.exception))

    @pytest.mark.asyncio
    async def test_post_success(self):
        """Test successful POST request."""
        endpoint = "/test/endpoint"
        data = {"key": "value"}

        with patch("aiohttp.ClientSession.post") as mock_post:
            # Set up the mock response
            mock_resp = AsyncMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = self.mock_response
            mock_post.return_value.__aenter__.return_value = mock_resp

            # Make the request
            result = await self.client._post(endpoint, data=data)

            # Verify the request was made correctly
            mock_post.assert_called_once_with(
                f"{self.base_url}{endpoint}", headers=self.client.headers, json=data
            )

            # Verify the response was handled correctly
            self.assertEqual(result, self.mock_response)

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test handling of HTTP errors."""
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_resp = AsyncMock()
            mock_resp.raise_for_status.side_effect = ClientResponseError(
                request_info=None, history=None, status=404, message="Not Found"
            )
            mock_get.return_value.__aenter__.return_value = mock_resp

            with self.assertRaises(ClientResponseError) as context:
                await self.client._get("/nonexistent")
            self.assertEqual(context.exception.status, 404)

    @pytest.mark.asyncio
    async def test_get_repo(self):
        """Test getting repository information."""
        owner = "testowner"
        repo = "testrepo"
        expected_url = f"/repos/{owner}/{repo}"

        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = self.mock_response

            result = await self.client.get_repo(owner, repo)

            mock_get.assert_called_once_with(expected_url)
            self.assertEqual(result, self.mock_response)

    @pytest.mark.asyncio
    async def test_create_issue(self):
        """Test creating an issue."""
        owner = "testowner"
        repo = "testrepo"
        title = "Test Issue"
        body = "Test body"
        labels = ["bug"]
        assignees = ["user1"]

        expected_url = f"/repos/{owner}/{repo}/issues"
        expected_data = {"title": title, "body": body, "labels": labels, "assignees": assignees}

        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = self.mock_response

            result = await self.client.create_issue(owner, repo, title, body, labels, assignees)

            mock_post.assert_called_once_with(expected_url, data=expected_data)
            self.assertEqual(result, self.mock_response)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client can be used as a context manager."""
        async with GitHubClient(token=self.token) as client:
            self.assertIsInstance(client, GitHubClient)
            self.assertIsInstance(client.session, ClientSession)
        # Session should be closed after context manager exits
        self.assertTrue(client.session.closed)

    @pytest.mark.asyncio
    async def test_put_request(self):
        """Test successful PUT request."""
        endpoint = "/test/endpoint/123"
        data = {"key": "updated_value"}

        # Create a mock session with a successful response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = self.rate_limit_headers
        mock_response.json.return_value = self.mock_response
        mock_session.request.return_value.__aenter__.return_value = mock_response

        # Patch _get_session
        with patch.object(self.client, "_get_session", return_value=mock_session):
            # Make the request
            result = await self.client.put(endpoint, data=data)

            # Verify the request was made correctly
            mock_session.request.assert_called_once()
            args, kwargs = mock_session.request.call_args
            self.assertEqual(args[0], "PUT")
            self.assertTrue(args[1].endswith(endpoint))
            self.assertEqual(kwargs["json"], data)

            # Verify the response was handled correctly
            self.assertEqual(result, self.mock_response)

    @pytest.mark.asyncio
    async def test_patch_request(self):
        """Test successful PATCH request."""
        endpoint = "/test/endpoint/123"
        data = {"key": "patched_value"}

        # Create a mock session with a successful response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = self.rate_limit_headers
        mock_response.json.return_value = self.mock_response
        mock_session.request.return_value.__aenter__.return_value = mock_response

        # Patch _get_session
        with patch.object(self.client, "_get_session", return_value=mock_session):
            # Make the request
            result = await self.client.patch(endpoint, data=data)

            # Verify the request was made correctly
            mock_session.request.assert_called_once()
            args, kwargs = mock_session.request.call_args
            self.assertEqual(args[0], "PATCH")
            self.assertTrue(args[1].endswith(endpoint))
            self.assertEqual(kwargs["json"], data)

            # Verify the response was handled correctly
            self.assertEqual(result, self.mock_response)

    @pytest.mark.asyncio
    async def test_delete_request(self):
        """Test successful DELETE request."""
        endpoint = "/test/endpoint/123"

        # Create a mock session with a successful response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 204  # No content
        mock_response.headers = self.rate_limit_headers
        mock_response.json.return_value = None
        mock_session.request.return_value.__aenter__.return_value = mock_response

        # Patch _get_session
        with patch.object(self.client, "_get_session", return_value=mock_session):
            # Make the request
            result = await self.client.delete(endpoint)

            # Verify the request was made correctly
            mock_session.request.assert_called_once()
            args, _ = mock_session.request.call_args
            self.assertEqual(args[0], "DELETE")
            self.assertTrue(args[1].endswith(endpoint))

            # Verify the response was handled correctly
            self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_request_with_timeout(self):
        """Test that the request times out after the specified timeout."""
        endpoint = "/test/endpoint"

        # Create a mock session that never responds
        mock_session = AsyncMock()
        mock_session.request.side_effect = asyncio.TimeoutError("Request timed out")

        # Patch _get_session
        with patch.object(self.client, "_get_session", return_value=mock_session):
            # Make the request and expect it to raise TimeoutError
            with self.assertRaises(asyncio.TimeoutError):
                await self.client.get(endpoint, timeout=0.1)

            # Verify it didn't retry on timeout
            self.assertEqual(mock_session.request.call_count, 1)

    @pytest.mark.asyncio
    async def test_custom_headers(self):
        """Test that custom headers are properly included in requests."""
        endpoint = "/test/endpoint"
        custom_headers = {
            "X-Custom-Header": "custom-value",
            "Accept": "application/vnd.github.v4+json",  # Override default Accept
        }

        # Create a mock session with a successful response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = self.rate_limit_headers
        mock_response.json.return_value = self.mock_response
        mock_session.request.return_value.__aenter__.return_value = mock_response

        # Patch _get_session
        with patch.object(self.client, "_get_session", return_value=mock_session):
            # Make the request with custom headers
            result = await self.client.get(endpoint, headers=custom_headers)

            # Verify the request was made with merged headers
            mock_session.request.assert_called_once()
            _, kwargs = mock_session.request.call_args

            # Check that custom headers are included
            self.assertEqual(kwargs["headers"]["X-Custom-Header"], "custom-value")
            # Check that default headers are still there
            self.assertIn("Authorization", kwargs["headers"])
            # Check that custom Accept header overrode the default
            self.assertEqual(kwargs["headers"]["Accept"], "application/vnd.github.v4+json")

            # Verify the response was handled correctly
            self.assertEqual(result, self.mock_response)
