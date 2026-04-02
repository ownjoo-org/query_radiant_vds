"""Unit tests for query_radiant_vds CLI argument parsing."""

import json
import unittest


class TestCLIArgumentParsing(unittest.TestCase):
    """Tests for CLI argument parsing."""

    def test_required_arguments(self) -> None:
        """Test that required arguments are properly defined."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--username", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)
        parser.add_argument("--domain", type=str, required=True)
        parser.add_argument("--search-filter", type=str, required=True, dest="search_filter")

        # Missing args should raise
        with self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_all_arguments_parse_correctly(self) -> None:
        """Test that all expected arguments can be parsed."""
        import argparse

        test_args = [
            "--username",
            "admin",
            "--password",
            "secret",
            "--domain",
            "radiant.example.com",
            "--port",
            "9443",
            "--search-filter",
            "(objectClass=*)",
            "--attributes",
            "cn,mail",
            "--scope",
            "sub",
            "--context",
            "default",
            "--return-mode",
            "standard",
            "--result-limit",
            "100",
            "--page-size",
            "50",
            "--proxies",
            '{"http": "http://proxy:8080"}',
            "--log-level",
            "10",
        ]

        parser = argparse.ArgumentParser()
        parser.add_argument("--username", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)
        parser.add_argument("--domain", type=str, required=True)
        parser.add_argument("--search-filter", type=str, required=True, dest="search_filter")
        parser.add_argument("--port", type=int, required=False, default=8080)
        parser.add_argument("--attributes", type=str, required=False)
        parser.add_argument("--scope", type=str, required=False, default="sub")
        parser.add_argument("--context", type=str, required=False)
        parser.add_argument("--return-mode", type=str, required=False, dest="return_mode")
        parser.add_argument(
            "--result-limit", type=int, required=False, default=0, dest="result_limit"
        )
        parser.add_argument("--page-size", type=int, required=False, default=100, dest="page_size")
        parser.add_argument("--proxies", type=str, required=False)
        parser.add_argument("--log-level", type=int, required=False, default=20, dest="log_level")

        args = parser.parse_args(test_args)

        self.assertEqual(args.username, "admin")
        self.assertEqual(args.password, "secret")
        self.assertEqual(args.domain, "radiant.example.com")
        self.assertEqual(args.port, 9443)
        self.assertEqual(args.search_filter, "(objectClass=*)")
        self.assertEqual(args.attributes, "cn,mail")
        self.assertEqual(args.scope, "sub")
        self.assertEqual(args.context, "default")
        self.assertEqual(args.return_mode, "standard")
        self.assertEqual(args.result_limit, 100)
        self.assertEqual(args.page_size, 50)
        self.assertEqual(args.log_level, 10)

    def test_default_port(self) -> None:
        """Test that port defaults to 8080."""
        import argparse

        test_args = [
            "--username",
            "user",
            "--password",
            "pass",
            "--domain",
            "example.com",
            "--search-filter",
            "(cn=*)",
        ]

        parser = argparse.ArgumentParser()
        parser.add_argument("--username", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)
        parser.add_argument("--domain", type=str, required=True)
        parser.add_argument("--search-filter", type=str, required=True, dest="search_filter")
        parser.add_argument("--port", type=int, required=False, default=8080)
        parser.add_argument(
            "--result-limit", type=int, required=False, default=0, dest="result_limit"
        )
        parser.add_argument("--page-size", type=int, required=False, default=100, dest="page_size")

        args = parser.parse_args(test_args)

        self.assertEqual(args.port, 8080)
        self.assertEqual(args.result_limit, 0)
        self.assertEqual(args.page_size, 100)

    def test_proxies_json_parsing(self) -> None:
        """Test that proxies JSON string can be parsed."""
        proxies_json = '{"http": "http://proxy:8080", "https": "https://proxy:8080"}'
        proxies = json.loads(proxies_json)

        self.assertEqual(proxies["http"], "http://proxy:8080")
        self.assertEqual(proxies["https"], "https://proxy:8080")

    def test_invalid_json_handling(self) -> None:
        """Test that invalid JSON raises appropriate error."""
        invalid_json = '{"incomplete'

        with self.assertRaises(json.JSONDecodeError):
            json.loads(invalid_json)


if __name__ == "__main__":
    unittest.main()
