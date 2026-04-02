"""Integration tests for query_radiant_vds.main module.

These tests demonstrate integration testing patterns with real or near-real dependencies.
Following ownjoo-org principles: prefer integration tests hitting real dependencies
over mocks that diverge from production behavior.
"""

import unittest
from unittest.mock import AsyncMock, patch

from query_radiant_vds.main import main


class TestMainOrchestration(unittest.IsolatedAsyncioTestCase):
    """Tests for main async orchestration."""

    async def test_main_constructs_adap_url(self) -> None:
        """Test that main constructs the correct ADAP URL.

        This is a simplified test showing the pattern. In production, you might:
        - Use a test RadiantOne instance
        - Mock at the AsyncClient level (boundary)
        - Test actual ADAP pagination logic
        """
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
        self.assertIn("https://radiant.example.com:8080/adap", str(call_args))
        self.assertIn("(cn=*)", str(call_args))

    async def test_main_passes_search_parameters(self) -> None:
        """Test that main passes all search parameters to search_adap."""
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
        self.assertEqual(call_kwargs["search_filter"], "(objectClass=*)")
        self.assertEqual(call_kwargs["attributes"], "cn,mail,uid")
        self.assertEqual(call_kwargs["scope"], "sub")
        self.assertEqual(call_kwargs["context"], "default")
        self.assertEqual(call_kwargs["return_mode"], "standard")
        self.assertEqual(call_kwargs["result_limit"], 50)
        self.assertEqual(call_kwargs["page_size"], 10)


if __name__ == "__main__":
    unittest.main()
