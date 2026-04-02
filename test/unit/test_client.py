"""Unit tests for template_cli.client module."""
import pytest
from unittest.mock import AsyncMock, patch

from template_cli.client import get_response


@pytest.mark.asyncio
async def test_get_response_success() -> None:
    """Test successful HTTP response."""
    expected_data = {"character": {"id": 1, "name": "Rick Sanchez"}}

    with patch("template_cli.client.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status = AsyncMock()

        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value.request.return_value = mock_response
        mock_async_client.__aexit__.return_value = AsyncMock()

        with patch("template_cli.client.AsyncClient", return_value=mock_async_client):
            result = await get_response(
                url="https://rickandmortyapi.com/api/character/1",
                username="test",
                password="test",
            )

        assert result == expected_data


@pytest.mark.asyncio
async def test_get_response_404_returns_none() -> None:
    """Test 404 response returns None."""
    from httpx import HTTPStatusError, Response, Request

    mock_request = Request("GET", "https://rickandmortyapi.com/api/character/9999")
    mock_response = Response(404, request=mock_request)

    with patch("template_cli.client.AsyncClient") as mock_client:
        mock_async_client = AsyncMock()
        mock_async_client.__aenter__.return_value.request.side_effect = HTTPStatusError(
            "404", request=mock_request, response=mock_response
        )

        with patch("template_cli.client.AsyncClient", return_value=mock_async_client):
            result = await get_response(
                url="https://rickandmortyapi.com/api/character/9999",
                username="test",
                password="test",
            )

        assert result is None
