"""Acceptance tests for query_radiant_vds CLI — invokes main.py as a subprocess."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
MAIN_PY = str(PROJECT_ROOT / "main.py")

REQUIRED_ARGS = [
    "--username", "testuser",
    "--password", "testpass",
    "--url", "http://localhost:8080",
    "--base-dn", "ou=People,o=SOMEORG",
    "--search-filter", "(cn=*)",
]


def run_cli(*args: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, MAIN_PY, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


class TestCLIArgValidation(unittest.TestCase):
    """Tests that the CLI rejects bad invocations before making any network calls."""

    def test_no_args_exits_with_error(self) -> None:
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error", result.stderr.lower())

    def test_missing_username_exits_with_error(self) -> None:
        args = [a for a in REQUIRED_ARGS if a not in ("--username", "testuser")]
        result = run_cli(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--username", result.stderr)

    def test_missing_password_exits_with_error(self) -> None:
        args = [a for a in REQUIRED_ARGS if a not in ("--password", "testpass")]
        result = run_cli(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--password", result.stderr)

    def test_missing_url_exits_with_error(self) -> None:
        args = [a for a in REQUIRED_ARGS if a not in ("--url", "http://localhost:8080")]
        result = run_cli(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--url", result.stderr)

    def test_missing_base_dn_exits_with_error(self) -> None:
        args = [a for a in REQUIRED_ARGS if a not in ("--base-dn", "ou=People,o=SOMEORG")]
        result = run_cli(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--base-dn", result.stderr)

    def test_missing_search_filter_exits_with_error(self) -> None:
        args = [a for a in REQUIRED_ARGS if a not in ("--search-filter", "(cn=*)")]
        result = run_cli(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--search-filter", result.stderr)

    def test_invalid_port_type_exits_with_error(self) -> None:
        result = run_cli(*REQUIRED_ARGS, "--port", "notanumber")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--port", result.stderr)

    def test_invalid_log_level_type_exits_with_error(self) -> None:
        result = run_cli(*REQUIRED_ARGS, "--log-level", "notanumber")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--log-level", result.stderr)


class TestCLIWithMockServer(unittest.TestCase):
    """Acceptance tests against a running mockoon server on localhost:8080.

    These tests are skipped automatically when no server is reachable.
    Start mockoon with: mockoon-cli start --data test/integration/mock.json
    """

    MOCKOON_URL = "http://localhost"
    MOCKOON_PORT = "8080"

    @classmethod
    def setUpClass(cls) -> None:
        import urllib.request
        import urllib.error

        try:
            urllib.request.urlopen(
                f"{cls.MOCKOON_URL}:{cls.MOCKOON_PORT}/adap/ou=People,o=SOMEORG"
                "?filter=(cn=*)&scope=sub&sizeLimit=0&count=1&startIndex=0",
                timeout=2,
            )
        except (urllib.error.URLError, OSError):
            raise unittest.SkipTest("mockoon server not reachable on localhost:8080")

    def _run_against_mock(self, *extra_args: str) -> subprocess.CompletedProcess:
        return run_cli(
            "--username", "testuser",
            "--password", "testpass",
            "--url", self.MOCKOON_URL,
            "--port", self.MOCKOON_PORT,
            "--base-dn", "ou=People,o=SOMEORG",
            "--search-filter", "(objectclass=person)",
            "--result-limit", "2",
            *extra_args,
        )

    def test_successful_query_exits_zero(self) -> None:
        result = self._run_against_mock()
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_successful_query_outputs_json(self) -> None:
        result = self._run_against_mock()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        # stdout should be valid JSON lines (one object per line or a JSON array)
        self.assertTrue(result.stdout.strip(), "expected non-empty stdout")
        # Each line should parse as JSON
        for line in result.stdout.strip().splitlines():
            json.loads(line)  # raises if invalid

    def test_proxies_flag_accepted(self) -> None:
        result = self._run_against_mock("--proxies", "{}")
        self.assertEqual(result.returncode, 0, msg=result.stderr)


if __name__ == "__main__":
    unittest.main()
