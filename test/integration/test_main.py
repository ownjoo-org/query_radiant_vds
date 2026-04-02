"""Integration tests for query_radiant_vds.main module.

These tests demonstrate integration testing patterns with real or near-real dependencies.
Following ownjoo-org principles: prefer integration tests hitting real dependencies
over mocks that diverge from production behavior.
"""

from unittest.mock import AsyncMock, patch

import pytest

from query_radiant_vds.main import main


@pytest.mark.asyncio
async def test_main_constructs_adap_url() -> None:
    """Test that main constructs the correct ADAP URL.

    This is a simplified test showing the pattern. In production, you might:
    - Use a test RadiantOne instance
    - Mock at the AsyncClient level (boundary)
    - Test actual ADAP pagination logic
    """
    with (
        patch("query_radiant_vds.main.search_adap") as mock_search,
        patch("query_radiant_vds.main.json_out") as mock_output,
    ):

        mock_search = AsyncMock()
        mock_output = AsyncMock()

        with (
            patch("query_radiant_vds.main.search_adap", mock_search),
            patch("query_radiant_vds.main.json_out", mock_output),
        ):

            await main(
                domain="radiant.example.com",
                port=8080,
                search_filter="(cn=*)",
                username="test",
                password="test",
                proxies=None,
            )

        # Verify search_adap was called with correct URL and filter
        mock_search.assert_called_once()
        call_args = mock_search.call_args
        assert "https://radiant.example.com:8080/adap" in str(call_args)
        assert "(cn=*)" in str(call_args)
