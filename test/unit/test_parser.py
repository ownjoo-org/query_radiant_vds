"""Unit tests for query_radiant_vds.parser module."""

import json
import unittest
from asyncio import Queue
from io import StringIO
from unittest.mock import patch

from query_radiant_vds.parser import json_out


class TestJsonOutput(unittest.IsolatedAsyncioTestCase):
    """Tests for JSON output formatting."""

    async def test_json_out_single_item(self) -> None:
        """Test that json_out outputs valid JSON array structure."""
        entry = {"dn": "cn=test", "cn": "test"}
        q = Queue()
        await q.put(entry)
        await q.put(None)  # sentinel

        output = StringIO()
        with patch("sys.stdout", output):
            await json_out(q)

        result = output.getvalue()
        self.assertTrue(result.strip().startswith("["), "Output should start with [")
        self.assertTrue(result.strip().endswith("]"), "Output should end with ]")

    async def test_json_out_with_multiple_items(self) -> None:
        """Test JSON output with commas between items."""
        entries = [
            {"dn": "cn=user1", "cn": "user1"},
            {"dn": "cn=user2", "cn": "user2"},
        ]
        q = Queue()
        for entry in entries:
            await q.put(entry)
        await q.put(None)  # sentinel

        output = StringIO()
        with patch("sys.stdout", output):
            await json_out(q)

        result = output.getvalue()
        self.assertIn(",", result)

    async def test_json_out_empty_queue(self) -> None:
        """Test JSON output with no items (sentinel only)."""
        q = Queue()
        await q.put(None)  # sentinel only

        output = StringIO()
        with patch("sys.stdout", output):
            await json_out(q)

        result = output.getvalue()
        self.assertIn("[", result)
        self.assertIn("]", result)

    async def test_json_out_task_done_called_per_item(self) -> None:
        """Test that task_done is called for each item so q.join() can complete."""
        entries = [{"cn": "user1"}, {"cn": "user2"}]
        q = Queue()
        for entry in entries:
            await q.put(entry)
        await q.put(None)  # sentinel

        with patch("sys.stdout", StringIO()):
            await json_out(q)

        # q.join() should return immediately (all task_done() calls made)
        await q.join()


class TestJsonFormatting(unittest.TestCase):
    """Tests for JSON formatting utilities."""

    def test_json_serialization(self) -> None:
        """Test that dict can be serialized to JSON."""
        entry = {"dn": "cn=test", "cn": "test", "mail": "test@example.com"}

        json_str = json.dumps(entry, indent=4)

        parsed = json.loads(json_str)
        self.assertEqual(parsed["cn"], "test")

    def test_json_with_nested_objects(self) -> None:
        """Test JSON formatting with nested structures."""
        entry = {
            "dn": "cn=test",
            "cn": "test",
            "nested": {"key": "value", "number": 123},
        }

        json_str = json.dumps(entry, indent=4)
        parsed = json.loads(json_str)

        self.assertEqual(parsed["nested"]["key"], "value")
        self.assertEqual(parsed["nested"]["number"], 123)

    def test_json_array_formatting(self) -> None:
        """Test formatting of JSON arrays."""
        entries = [
            {"cn": "user1"},
            {"cn": "user2"},
        ]

        json_lines = [json.dumps(entry, indent=4) for entry in entries]
        json_array = "[\n" + ",\n".join(json_lines) + "\n]"

        parsed = json.loads(json_array)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["cn"], "user1")
        self.assertEqual(parsed[1]["cn"], "user2")


if __name__ == "__main__":
    unittest.main()
