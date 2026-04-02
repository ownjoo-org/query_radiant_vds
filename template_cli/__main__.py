"""Entry point for template_cli when invoked as a module."""

import os
import sys

# Add parent directory to path so we can import main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main as cli_main  # noqa: E402

if __name__ == "__main__":
    cli_main()
