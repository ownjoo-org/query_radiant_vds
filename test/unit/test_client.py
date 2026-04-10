"""Unit tests for query_radiant_vds.client module."""

import unittest
from asyncio import Queue
from unittest.mock import AsyncMock, MagicMock, patch

from query_radiant_vds.client import get_response, list_results_paginated, search_adap


class TestSearchADAP(unittest.IsolatedAsyncioTestCase):
    """Tests for ADAP search functionality."""

    async def test_search_adap_puts_results_in_queue(self) -> None:
        """Test search_adap puts ADAP entries into queue then sends sentinel."""
        adap_entry = {"dn": "cn=testuser,ou=users,dc=example,dc=com", "cn": "testuser"}
        adap_response = {
            "resources": [adap_entry],
            "cookie": None,
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

        result = await q.get()
        self.assertEqual(result, adap_entry)

        sentinel = await q.get()
        self.assertIsNone(sentinel)


class TestPagination(unittest.IsolatedAsyncioTestCase):
    """Tests for pagination with result limiting."""

    async def test_pagination_respects_result_limit(self) -> None:
        """Test that pagination stops at result_limit."""
        entries = [{"dn": f"cn=user{i}", "cn": f"user{i}"} for i in range(30)]
        call_count = [0]

        def mock_get_response_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {"resources": entries[0:10], "cookie": "cursor1"}
            elif call_count[0] == 2:
                return {"resources": entries[10:20], "cookie": "cursor2"}
            return {"resources": entries[20:30], "cookie": None}

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

            self.assertEqual(len(results), 15)

    async def test_pagination_no_limit_returns_all(self) -> None:
        """Test that pagination returns all results when result_limit=0."""
        entries = [{"dn": f"cn=user{i}", "cn": f"user{i}"} for i in range(25)]
        call_count = [0]

        def mock_get_response_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {"resources": entries[0:10], "cookie": "cursor1"}
            elif call_count[0] == 2:
                return {"resources": entries[10:20], "cookie": "cursor2"}
            return {"resources": entries[20:25], "cookie": None}

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

            self.assertEqual(len(results), 25)

    async def test_page_size_optimization(self) -> None:
        """Test that page_size is optimized when > result_limit."""
        adap_entry = {"dn": "cn=test", "cn": "test"}
        adap_response = {"resources": [adap_entry], "cookie": None}

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

            call_args = mock_response.call_args
            self.assertEqual(call_args[1]["params"]["count"], 5)


class TestGetResponse(unittest.IsolatedAsyncioTestCase):
    """Tests for low-level HTTP response handling."""

    async def test_get_response_returns_json(self) -> None:
        """Test that get_response returns parsed JSON from the httpx response."""
        expected_response = {"resources": [{"cn": "test"}]}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_response.raise_for_status = MagicMock()

        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_response)
        mock_session.headers = MagicMock()
        mock_session.verify = True

        with patch("query_radiant_vds.client.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await get_response(url="https://radiant.example.com:8080/adap")

        self.assertEqual(result, expected_response)

    async def test_get_response_params(self) -> None:
        """Test that get_response accepts the expected parameters."""
        import inspect

        sig = inspect.signature(get_response)
        params = list(sig.parameters.keys())

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


class TestListResultsPaginated(unittest.IsolatedAsyncioTestCase):
    """Tests for paginated results fetching."""

    async def test_list_results_single_page(self) -> None:
        """Test fetching a single page of results."""
        entries = [
            {"dn": "cn=user1", "cn": "user1"},
            {"dn": "cn=user2", "cn": "user2"},
        ]
        response = {"resources": entries, "cookie": None}

        with patch("query_radiant_vds.client.get_response") as mock_get:
            mock_get.return_value = response

            results = []
            async for result in list_results_paginated(
                url="https://radiant.example.com:8080/adap",
                search_filter="(cn=*)",
            ):
                results.append(result)

            self.assertEqual(results, entries)

    async def test_list_results_empty_response(self) -> None:
        """Test handling of empty results."""
        response = {"resources": [], "cookie": None}

        with patch("query_radiant_vds.client.get_response") as mock_get:
            mock_get.return_value = response

            results = []
            async for result in list_results_paginated(
                url="https://radiant.example.com:8080/adap",
                search_filter="(cn=*)",
            ):
                results.append(result)

            self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
