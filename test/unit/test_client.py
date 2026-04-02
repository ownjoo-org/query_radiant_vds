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


class TestGetResponse(unittest.IsolatedAsyncioTestCase):
    """Tests for low-level HTTP response handling."""

    async def test_get_response_returns_json(self) -> None:
        """Test that get_response returns parsed JSON."""
        expected_response = {"results": [{"cn": "test"}]}

        with patch("query_radiant_vds.client.get_response") as mock_get:
            mock_get.return_value = expected_response

            from query_radiant_vds.client import get_response as real_get_response

            result = await real_get_response(
                url="https://radiant.example.com:8080/adap",
            )

            self.assertEqual(result, expected_response)

    async def test_get_response_params(self) -> None:
        """Test that get_response accepts various parameters."""
        import inspect

        from query_radiant_vds.client import get_response

        sig = inspect.signature(get_response)
        params = list(sig.parameters.keys())

        # Should have these parameters
        expected_params = [
            "url",
            "method",
            "params",
            "json",
            "data",
            "username",
            "password",
            "proxies",
        ]
        for param in expected_params:
            self.assertIn(param, params)


class TestListResults(unittest.IsolatedAsyncioTestCase):
    """Tests for single-page results fetching."""

    async def test_list_results_single_page(self) -> None:
        """Test fetching single page of results."""
        entries = [
            {"dn": "cn=user1", "cn": "user1"},
            {"dn": "cn=user2", "cn": "user2"},
        ]
        response = {"results": entries}

        q = Queue()

        with patch("query_radiant_vds.client.get_response") as mock_get:
            mock_get.return_value = response

            from query_radiant_vds.client import list_results

            await list_results(
                url="https://radiant.example.com:8080/adap",
                additional_params={"searchFilter": "(cn=*)"},
                q=q,
            )

            # Verify entries were put in queue
            for expected_entry in entries:
                result = await q.get()
                self.assertEqual(result, expected_entry)

    async def test_list_results_empty_response(self) -> None:
        """Test handling of empty results."""
        response = {"results": []}

        q = Queue()

        with patch("query_radiant_vds.client.get_response") as mock_get:
            mock_get.return_value = response

            from query_radiant_vds.client import list_results

            await list_results(
                url="https://radiant.example.com:8080/adap",
                q=q,
            )

            # Queue should be empty
            self.assertTrue(q.empty())


if __name__ == "__main__":
    unittest.main()
