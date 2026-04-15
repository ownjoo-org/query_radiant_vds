"""Terminal and console output utilities.

Provides simple, efficient classes for writing to standard output and error streams,
with support for colored output using ANSI escape codes, chainable colored text builders,
and formatting utilities for tables, boxes, and status displays.
"""

from query_radiant_vds.oj_toolkit.console.box import Box, in_box
from query_radiant_vds.oj_toolkit.console.colored_text import ColoredText
from query_radiant_vds.oj_toolkit.console.colors import Color
from query_radiant_vds.oj_toolkit.console.status import (
    progress_bar,
    status_badge,
    status_line,
    status_wrapped,
)
from query_radiant_vds.oj_toolkit.console.streams import Output
from query_radiant_vds.oj_toolkit.console.table import Table, tabulated

__all__ = [
    "Output",
    "Color",
    "ColoredText",
    "Table",
    "tabulated",
    "Box",
    "in_box",
    "status_line",
    "progress_bar",
    "status_badge",
    "status_wrapped",
]
