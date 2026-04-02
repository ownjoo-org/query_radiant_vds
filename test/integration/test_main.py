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


@pytest.mark.asyncio
async def test_main_passes_search_parameters() -> None:
    """Test that main passes all search parameters to search_adap."""
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
                search_filter="(objectClass=*)",
                attributes="cn,mail,uid",
                scope="sub",
                context="default",
                return_mode="standard",
                result_limit=50,
                page_size=10,
                username="test",
                password="test",
                proxies=None,
            )

        # Verify all parameters were passed
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs["search_filter"] == "(objectClass=*)"
        assert call_kwargs["attributes"] == "cn,mail,uid"
        assert call_kwargs["scope"] == "sub"
        assert call_kwargs["context"] == "default"
        assert call_kwargs["return_mode"] == "standard"
        assert call_kwargs["result_limit"] == 50
        assert call_kwargs["page_size"] == 10
