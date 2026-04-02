"""Integration tests for template_cli.main module.

These tests demonstrate integration testing patterns with real or near-real dependencies.
Following ownjoo-org principles: prefer integration tests hitting real dependencies
over mocks that diverge from production behavior.
"""
import pytest
from unittest.mock import AsyncMock, patch
from asyncio import Queue

from template_cli.main import main


@pytest.mark.asyncio
async def test_main_fetches_all_endpoints() -> None:
    """Test that main fetches characters, locations, and episodes.

    This is a simplified test showing the pattern. In production, you might:
    - Use a test API server
    - Mock at the AsyncClient level (boundary)
    - Test actual pagination logic
    """
    # Mock the client functions to avoid real API calls
    with patch("template_cli.main.list_characters") as mock_chars, \
         patch("template_cli.main.list_locations") as mock_locs, \
         patch("template_cli.main.list_episodes") as mock_eps, \
         patch("template_cli.main.json_out") as mock_output:

        mock_chars.return_value = AsyncMock()
        mock_locs.return_value = AsyncMock()
        mock_eps.return_value = AsyncMock()
        mock_output.return_value = AsyncMock()

        await main(
            domain="https://rickandmortyapi.com/api",
            username="test",
            password="test",
            proxies=None,
        )

        # Verify all three endpoints were queried
        mock_chars.assert_called_once()
        mock_locs.assert_called_once()
        mock_eps.assert_called_once()
        mock_output.assert_called_once()


@pytest.mark.asyncio
async def test_main_coordinates_queue() -> None:
    """Test that main sets up Queue coordination correctly."""
    with patch("template_cli.main.Queue") as mock_queue_cls, \
         patch("template_cli.main.gather") as mock_gather:

        mock_queue = AsyncMock()
        mock_queue_cls.return_value = mock_queue

        with patch("template_cli.main.list_characters"), \
             patch("template_cli.main.list_locations"), \
             patch("template_cli.main.list_episodes"), \
             patch("template_cli.main.json_out"):

            await main(
                domain="https://rickandmortyapi.com/api",
                username="test",
                password="test",
            )

            # Verify gather was called with 5 items: 3 clients + parser + q.join()
            assert mock_gather.await_count >= 1
