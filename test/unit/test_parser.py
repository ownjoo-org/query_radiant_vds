"""Unit tests for query_radiant_vds.parser module."""

import json
import unittest
from io import StringIO
from unittest.mock import patch

from query_radiant_vds.parser import json_out
from query_radiant_vds.tracker import contributing_tasks


class TestJsonOutput(unittest.IsolatedAsyncioTestCase):
    """Tests for JSON output formatting."""

    async def test_json_out_creates_valid_array_structure(self) -> None:
        """Test that json_out outputs valid JSON array structure."""
        from asyncio import Queue

        entry = {"dn": "cn=test", "cn": "test"}
        q = Queue()
        await q.put(entry)

        contributing_tasks.clear()
        contributing_tasks.append("test_task")

        output = StringIO()

        with patch("sys.stdout", output):
            await json_out(q)

        result = output.getvalue()
        # Should start with [ and end with ]
        self.assertTrue(result.strip().startswith("["), "Output should start with [")
        self.assertTrue(result.strip().endswith("]"), "Output should end with ]")

    async def test_json_out_with_multiple_items(self) -> None:
        """Test JSON output with commas between items."""
        from asyncio import Queue

        entries = [
            {"dn": "cn=user1", "cn": "user1"},
            {"dn": "cn=user2", "cn": "user2"},
        ]
        q = Queue()
        for entry in entries:
            await q.put(entry)

        contributing_tasks.clear()
        contributing_tasks.append("test_task")

        output = StringIO()

        with patch("sys.stdout", output):
            await json_out(q)

        result = output.getvalue()
        # Should have comma separating items
        self.assertIn(",", result)

    async def test_json_out_empty_queue(self) -> None:
        """Test JSON output with empty queue."""
        from asyncio import Queue

        q = Queue()

        contributing_tasks.clear()

        output = StringIO()

        with patch("sys.stdout", output):
            await json_out(q)

        result = output.getvalue()
        # Should output valid empty array
        self.assertIn("[", result)
        self.assertIn("]", result)


class TestJsonFormatting(unittest.TestCase):
    """Tests for JSON formatting utilities."""

    def test_json_serialization(self) -> None:
        """Test that dict can be serialized to JSON."""
        entry = {"dn": "cn=test", "cn": "test", "mail": "test@example.com"}

        json_str = json.dumps(entry, indent=4)

        # Should be valid JSON
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

        # Format as array with proper separators
        json_lines = [json.dumps(entry, indent=4) for entry in entries]
        json_array = "[\n" + ",\n".join(json_lines) + "\n]"

        # Should be valid JSON
        parsed = json.loads(json_array)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["cn"], "user1")
        self.assertEqual(parsed[1]["cn"], "user2")


if __name__ == "__main__":
    unittest.main()
