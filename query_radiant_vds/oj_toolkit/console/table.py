"""Smart table building with auto-detection and formatting.

Provides the Table class for building ASCII/Unicode tables with automatic
detection of input format (dict, tuple, list, str) and the @tabulated
decorator for wrapping function output as tables.
"""

import sys
from functools import wraps
from typing import Callable, Dict, Iterator, List, Optional

from query_radiant_vds.oj_toolkit.console.terminal import (
    border_chars,
    pad_visible,
    select_style,
    visible_width,
)


class Table:  # pylint: disable=too-many-instance-attributes
    """Smart table builder with auto-detection and multiple styles.

    Automatically detects input format (dict, tuple, list, str) and builds
    formatted tables with configurable borders, alignment, and column widths.

    Attributes:
        headers: Optional column headers.
        style: Border style ('auto', 'ascii', 'rounded', 'double', 'single', 'none').
        columns: Number of columns (auto-detected if None).
        rows: List of row data.
        align: Default alignment ('left', 'right', 'center').
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        headers: Optional[List[str]] = None,
        columns: Optional[int] = None,
        style: str = "auto",
        padding: int = 1,
        align: str = "left",
    ):
        """Initialize Table.

        Args:
            headers: Optional list of column headers.
            columns: Number of columns (auto-detect if None). Default: 1.
            style: Border style ('auto', 'ascii', etc.). Default: 'auto'.
            padding: Space padding inside cells. Default: 1.
            align: Default alignment for all columns. Default: 'left'.
        """
        self.headers = headers or []
        self.columns = columns or 1
        self.style = select_style(style, "ascii", "rounded")
        self.padding = padding
        self.align = align
        self.rows = []
        self._column_widths = {}
        self._column_aligns = {}
        self._detected_headers = False

    def add_row(self, *values) -> "Table":
        """Add a single row to the table.

        Args:
            *values: Column values for the row.

        Returns:
            Self for method chaining.
        """
        self.rows.append([str(v) for v in values])
        return self

    def add_rows(self, iterable: Iterator) -> "Table":  # pylint: disable=too-many-branches
        """Add multiple rows from an iterable.

        Intelligently detects input format:
        - Dict: extracts headers (if not set) and uses values as rows
        - Tuple of (key, value): treats as key-value pairs
        - List/str: treats as single row unless multiple items

        Args:
            iterable: Iterator of rows or dict items.

        Returns:
            Self for method chaining.
        """
        items = list(iterable)
        if not items:
            return self

        first = items[0]

        # Detect format from first item
        if isinstance(first, dict):
            # Dict format: extract headers and build rows
            if not self.headers and not self._detected_headers:
                self.headers = list(first.keys())
                self._detected_headers = True
                self.columns = len(self.headers)

            for item in items:
                row = [str(item.get(h, "")) for h in self.headers]
                self.rows.append(row)

        elif isinstance(first, (tuple, list)) and len(first) == 2:
            # Check if it looks like (key, value) pairs
            if isinstance(first[0], str) and not isinstance(first[1], (list, dict)):
                # Treat as key-value pairs
                if not self.headers:
                    self.headers = ["Key", "Value"]
                    self._detected_headers = True
                    self.columns = 2

                for key, value in items:
                    self.rows.append([str(key), str(value)])
            else:
                # Regular list/tuple rows
                for item in items:
                    row = [str(v) for v in item]
                    self.rows.append(row)
                    self.columns = max(self.columns, len(row))

        else:
            # String or simple items - treat each as a row
            for item in items:
                self.rows.append([str(item)])

        return self

    def set_column_width(self, column: int, width: int) -> "Table":
        """Set fixed width for a column.

        Args:
            column: Column index (0-based).
            width: Width in characters.

        Returns:
            Self for method chaining.
        """
        self._column_widths[column] = width
        return self

    def set_align(self, column: int, align: str) -> "Table":
        """Set alignment for a column.

        Args:
            column: Column index (0-based).
            align: Alignment ('left', 'right', 'center').

        Returns:
            Self for method chaining.
        """
        self._column_aligns[column] = align
        return self

    def _calculate_column_widths(self) -> Dict[int, int]:
        """Calculate optimal width for each column."""
        widths = {}

        # Start with header widths
        for i, header in enumerate(self.headers):
            widths[i] = visible_width(header)

        # Check all rows
        for row in self.rows:
            for i, cell in enumerate(row):
                width = visible_width(cell)
                widths[i] = max(widths.get(i, 0), width)

        # Apply custom widths and padding
        for col, width in self._column_widths.items():
            widths[col] = width

        # Add padding
        for col in widths:
            widths[col] += self.padding * 2

        return widths

    def __str__(self) -> str:  # pylint: disable=too-many-locals
        """Render table as string.

        Returns:
            Multi-line formatted table.
        """
        if not self.rows and not self.headers:
            return ""

        widths = self._calculate_column_widths()
        chars = border_chars(self.style)
        tl, tr, bl, br, top, bot, left, right, _cross, top_cross, sep_left, sep_cross, sep_right, bottom_cross = chars

        lines = []

        # Top border
        top_border = self._make_border_line(tl, tr, top, top_cross, widths)
        lines.append(top_border)

        # Headers
        if self.headers:
            header_line = self._make_data_line(self.headers, widths, left, right, left)
            lines.append(header_line)
            # Header separator with different junction characters
            header_sep = self._make_border_line(sep_left, sep_right, top, sep_cross, widths)
            lines.append(header_sep)

        # Rows
        for row in self.rows:
            data_line = self._make_data_line(row, widths, left, right, left)
            lines.append(data_line)

        # Bottom border
        bottom_border = self._make_border_line(bl, br, bot, bottom_cross, widths)
        lines.append(bottom_border)

        return "\n".join(lines)

    def _make_border_line(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, tl: str, tr: str, fill: str, cross: str, widths: Dict[int, int]
    ) -> str:
        """Create a border line with specified corners and junctions."""
        segments = [tl]
        for i in range(self.columns):
            width = widths.get(i, 10)
            segments.append(fill * width)
            if i < self.columns - 1:
                segments.append(cross)
        segments.append(tr)
        return "".join(segments)

    def _make_data_line(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, row: List[str], widths: Dict[int, int], left: str, right: str, col_sep: str = "│"
    ) -> str:
        """Create a data line with cell values.

        Args:
            row: List of cell values
            widths: Column width dictionary
            left: Left border character
            right: Right border character
            col_sep: Column separator character (vertical)
        """
        segments = [left]
        for i in range(self.columns):
            cell = row[i] if i < len(row) else ""
            width = widths.get(i, 10) - (self.padding * 2)
            align = self._column_aligns.get(i, self.align)

            # Pad cell to width with alignment
            padded = pad_visible(cell, width, align=align)
            cell_content = (" " * self.padding) + padded + (" " * self.padding)
            segments.append(cell_content)

            if i < self.columns - 1:
                segments.append(col_sep)

        segments.append(right)
        return "".join(segments)

    def out(self, sep: str = "", end: str = "\n", flush: bool = False) -> None:
        """Print table to stdout.

        Args:
            sep: Separator (unused). Default: "".
            end: String appended after output. Default: newline.
            flush: Whether to force flush. Default: False.
        """
        print(str(self), sep=sep, end=end, file=sys.stdout, flush=flush)

    def err(self, sep: str = "", end: str = "\n", flush: bool = False) -> None:
        """Print table to stderr.

        Args:
            sep: Separator (unused). Default: "".
            end: String appended after output. Default: newline.
            flush: Whether to force flush. Default: False.
        """
        print(str(self), sep=sep, end=end, file=sys.stderr, flush=flush)


def tabulated(
    headers: Optional[List[str]] = None,
    columns: Optional[int] = None,
    style: str = "auto",
    padding: int = 1,
) -> Callable:
    """Decorator to wrap function output as a formatted table.

    Intelligently formats the function's return value (iterable) as a table.

    Args:
        headers: Optional column headers.
        columns: Number of columns (auto-detect if None).
        style: Border style ('auto', 'ascii', etc.). Default: 'auto'.
        padding: Cell padding. Default: 1.

    Returns:
        Decorator function.

    Example:
        >>> from query_radiant_vds.oj_toolkit.console import tabulated
        >>> @tabulated(headers=["Name", "Status"])
        ... def get_results():
        ...     yield ("Task 1", "OK")
        ...     yield ("Task 2", "FAIL")
        >>> get_results()  # Prints formatted table
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            result = func(*args, **kwargs)

            # Create table and populate
            table = Table(
                headers=headers, columns=columns, style=style, padding=padding
            )

            # Handle different return types
            if result is None:
                pass
            elif isinstance(result, (list, tuple)):
                table.add_rows(result)
            else:
                # Assume it's an iterable
                try:
                    table.add_rows(result)
                except TypeError:
                    # Single value, add as row
                    table.add_row(str(result))

            # Print the table
            table.out()

        return wrapper

    return decorator
