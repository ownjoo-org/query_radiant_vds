"""Unit tests for query_radiant_vds.client module."""

import unittest
from asyncio import Queue
from unittest.mock import patch

from query_radiant_vds.client import list_results_paginated, search_adap


class TestSearchADAP(unittest.IsolatedAsyncioTestCase):
    """Tests for ADAP search functionality."""

    async def test_search_adap_puts_results_in_queue(self) -> None:
        """Test search_adap puts ADAP entries into queue."""
        adap_entry = {"dn": "cn=testuser,ou=users,dc=example,dc=com", "cn": "testuser"}
        adap_response = {
            "results": [adap_entry],
            "info": {"next": None},
        }

        q: Queue = Queue()

        with patch("query_radiant_vds.client.get_response") as mock_get_response:
            mock_get_response.return_value = adap_response

            await search_adap(
                url="https://radiant.example.com:8080/adap",
                search_filter="(cn=testuser)",
                username="test",
                password="test",
                q=q,
            )

            # Verify entry was put in queue
            result = await q.get()
            self.assertEqual(result, adap_entry)


class TestPagination(unittest.IsolatedAsyncioTestCase):
    """Tests for pagination with result limiting."""

    async def test_pagination_respects_result_limit(self) -> None:
        """Test that pagination stops at result_limit."""
        # Create 30 entries (3 pages of 10)
        entries = [{"dn": f"cn=user{i}", "cn": f"user{i}"} for i in range(30)]

        # Mock responses for 3 pages
        def mock_get_response_side_effect(*args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if page == 1:
                return {"results": entries[0:10], "info": {"next": "page2"}}
            elif page == 2:
                return {"results": entries[10:20], "info": {"next": "page3"}}
            elif page == 3:
                return {"results": entries[20:30], "info": {"next": None}}
            return {"results": [], "info": {}}

        with patch(
            "query_radiant_vds.client.get_response",
            side_effect=mock_get_response_side_effect,
        ):
            results = []
            async for result in list_results_paginated(
                url="https://radiant.example.com:8080/adap",
                search_filter="(objectClass=*)",
                result_limit=15,
                page_size=10,
            ):
                results.append(result)

            # Should stop at 15 results, not fetch all 30
            self.assertEqual(len(results), 15)

    async def test_pagination_no_limit_returns_all(self) -> None:
        """Test that pagination returns all results when result_limit=0."""
        entries = [{"dn": f"cn=user{i}", "cn": f"user{i}"} for i in range(25)]

        def mock_get_response_side_effect(*args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if page == 1:
                return {"results": entries[0:10], "info": {"next": "page2"}}
            elif page == 2:
                return {"results": entries[10:20], "info": {"next": "page3"}}
            elif page == 3:
                return {"results": entries[20:25], "info": {"next": None}}
            return {"results": [], "info": {}}

        with patch(
            "query_radiant_vds.client.get_response",
            side_effect=mock_get_response_side_effect,
        ):
            results = []
            async for result in list_results_paginated(
                url="https://radiant.example.com:8080/adap",
                search_filter="(objectClass=*)",
                result_limit=0,
                page_size=10,
            ):
                results.append(result)

            # Should return all 25 results
            self.assertEqual(len(results), 25)

    async def test_page_size_optimization(self) -> None:
        """Test that page_size is optimized when > result_limit."""
        adap_entry = {"dn": "cn=test", "cn": "test"}
        adap_response = {"results": [adap_entry], "info": {"next": None}}

        with patch(
            "query_radiant_vds.client.get_response", return_value=adap_response
        ) as mock_response:
            results = []
            async for result in list_results_paginated(
                url="https://radiant.example.com:8080/adap",
                search_filter="(cn=*)",
                result_limit=5,
                page_size=100,
            ):
                results.append(result)

            # Verify that pageSize in params was set to 5 (optimized)
            call_args = mock_response.call_args
            self.assertEqual(call_args[1]["params"]["pageSize"], 5)


if __name__ == "__main__":
    unittest.main()
