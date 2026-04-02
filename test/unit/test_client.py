"""Unit tests for template_cli.client module."""

from asyncio import Queue
from unittest.mock import patch

import pytest

from template_cli.client import search_adap


@pytest.mark.asyncio
async def test_search_adap_puts_results_in_queue() -> None:
    """Test search_adap puts ADAP entries into queue."""
    adap_entry = {"dn": "cn=testuser,ou=users,dc=example,dc=com", "cn": "testuser"}
    adap_response = {
        "results": [adap_entry],
        "info": {"next": None},
    }

    q: Queue = Queue()

    with patch("template_cli.client.get_response") as mock_get_response:
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
        assert result == adap_entry
