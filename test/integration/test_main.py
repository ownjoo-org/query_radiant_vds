"""Integration tests for query_radiant_vds.main module."""

import unittest
from unittest.mock import AsyncMock, patch

from query_radiant_vds.main import main


class TestMainOrchestration(unittest.IsolatedAsyncioTestCase):
    """Tests for main async orchestration."""

    async def test_main_constructs_adap_url(self) -> None:
        """Test that main constructs the correct ADAP URL from url, port, and base_dn."""
        mock_search = AsyncMock()
        mock_output = AsyncMock()

        with (
            patch("query_radiant_vds.main.search_adap", mock_search),
            patch("query_radiant_vds.main.json_out", mock_output),
        ):
            await main(
                url="http://radiant.example.com",
                port=8080,
                base_dn="ou=People,o=SOMEORG",
                search_filter="(cn=*)",
                username="test",
                password="test",
                proxies=None,
            )

        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        self.assertEqual(
            call_kwargs["url"],
            "http://radiant.example.com:8080/adap/ou=People,o=SOMEORG",
        )
        self.assertEqual(call_kwargs["search_filter"], "(cn=*)")

    async def test_main_passes_search_parameters(self) -> None:
        """Test that main passes all search parameters to search_adap."""
        mock_search = AsyncMock()
        mock_output = AsyncMock()

        with (
            patch("query_radiant_vds.main.search_adap", mock_search),
            patch("query_radiant_vds.main.json_out", mock_output),
        ):
            await main(
                url="http://radiant.example.com",
                port=8080,
                base_dn="ou=People,o=SOMEORG",
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
