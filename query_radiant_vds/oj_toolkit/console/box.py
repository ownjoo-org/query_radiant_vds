"""Box and frame building utilities.

Provides the Box class for wrapping text in decorative boxes with multiple
border styles, and the @in_box decorator for wrapping function output.
"""

import sys
from functools import wraps
from typing import Callable, Optional

from query_radiant_vds.oj_toolkit.console.terminal import (
    border_chars,
    pad_visible,
    select_style,
    visible_width,
)


class Box:
    """Builder for wrapping text in decorative boxes.

    Accumulates lines of text and renders them in a decorative box with
    configurable borders, padding, and optional title.

    Attributes:
        style: Border style ('auto', 'ascii', 'rounded', 'double', 'single', 'solid', 'none').
        padding: Number of spaces inside the box.
        width: Optional fixed box width (auto-calculates if None).
        title: Optional title displayed in the top border.
    """

    def __init__(
        self,
        style: str = "auto",
        padding: int = 1,
        width: Optional[int] = None,
        title: Optional[str] = None,
    ):
        """Initialize Box with style and configuration.

        Args:
            style: Border style. Default: 'auto' (detects terminal capabilities).
            padding: Inner padding in spaces. Default: 1.
            width: Optional fixed width. Default: None (auto-calculate).
            title: Optional title for top border. Default: None.
        """
        self.style = select_style(style, "ascii", "rounded")
        self.padding = padding
        self.width = width
        self.title = title
        self.lines = []

    def add_line(self, text: str) -> "Box":
        """Add a line of text to the box.

        Args:
            text: Text to add (may contain ANSI codes).

        Returns:
            Self for method chaining.
        """
        self.lines.append(str(text))
        return self

    def add_lines(self, lines: list[str]) -> "Box":
        """Add multiple lines to the box.

        Args:
            lines: List of text strings.

        Returns:
            Self for method chaining.
        """
        for line in lines:
            self.add_line(line)
        return self

    def _calculate_content_width(self) -> int:
        """Calculate the maximum content width from all lines."""
        if not self.lines:
            return 0
        return max(visible_width(line) for line in self.lines)

    def _get_box_width(self) -> int:
        """Get the total box width including borders and padding."""
        if self.width:
            return self.width

        # Content width + padding on both sides + borders
        content_width = self._calculate_content_width()
        return content_width + (self.padding * 2) + 2

    def __str__(self) -> str:  # pylint: disable=too-many-locals
        """Render box as string with borders.

        Returns:
            Multi-line string with box drawn around content.
        """
        chars = border_chars(self.style)
        tl, tr, bl, br, top, bot, left, right, _cross = chars[:9]  # Use first 9 chars for box rendering

        box_width = self._get_box_width()
        inner_width = box_width - 2  # Account for left/right borders

        lines = []

        # Top border with optional title
        # Note: Titles work best with Unicode styles, ASCII may not have space
        if self.title and tl != "+" and tl != " ":
            # Unicode title box: [TL] Title [TR]
            # For ASCII, just skip the title
            title_space = inner_width - len(self.title) - 4
            if title_space > 0:
                top_line = (
                    tl + " " + self.title + " " + (top * title_space) + tr
                )
            else:
                top_line = tl + (top * inner_width) + tr
        else:
            top_line = tl + (top * inner_width) + tr

        lines.append(top_line)

        # Content lines
        if self.lines:
            for line in self.lines:
                padded = pad_visible(
                    line, inner_width - (self.padding * 2), align="left"
                )
                content = (
                    left
                    + (" " * self.padding)
                    + padded
                    + (" " * self.padding)
                    + right
                )
                lines.append(content)
        else:
            # Empty box with just padding
            padding_line = (
                left + (" " * inner_width) + right
            )
            lines.append(padding_line)

        # Bottom border
        bottom_line = bl + (bot * inner_width) + br
        lines.append(bottom_line)

        return "\n".join(lines)

    def out(self, sep: str = "", end: str = "\n", flush: bool = False) -> None:
        """Print box to stdout.

        Args:
            sep: Separator (unused, for compatibility). Default: "".
            end: String appended after output (default: newline).
            flush: Whether to force flush (default: False).
        """
        print(str(self), sep=sep, end=end, file=sys.stdout, flush=flush)

    def err(self, sep: str = "", end: str = "\n", flush: bool = False) -> None:
        """Print box to stderr.

        Args:
            sep: Separator (unused, for compatibility). Default: "".
            end: String appended after output (default: newline).
            flush: Whether to force flush (default: False).
        """
        print(str(self), sep=sep, end=end, file=sys.stderr, flush=flush)


def in_box(
    style: str = "auto",
    padding: int = 1,
    width: Optional[int] = None,
    title: Optional[str] = None,
) -> Callable:
    """Decorator to wrap function output in a box.

    Wraps a function's return value in a decorative box.
    The function should return a string or list of strings.

    Args:
        style: Box style ('auto', 'ascii', 'rounded', 'double', 'single', 'solid', 'none').
            'auto' detects terminal capabilities. Default: 'auto'.
        padding: Number of spaces to pad inside the box. Default: 1.
        width: Optional box width. If None, auto-calculates based on content.
        title: Optional title to display in the top border.

    Returns:
        Decorator function.

    Example:
        >>> from query_radiant_vds.oj_toolkit.console import in_box
        >>> @in_box(style='double', title="Result")
        ... def show_result():
        ...     return "Success!"
        >>> show_result()  # Prints in double-line box with title
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            result = func(*args, **kwargs)

            # Handle different return types
            if result is None:
                lines = []
            elif isinstance(result, str):
                lines = [result]
            elif isinstance(result, (list, tuple)):
                lines = [str(item) for item in result]
            else:
                lines = [str(result)]

            # Create and populate box
            box = Box(style=style, padding=padding, width=width, title=title)
            for line in lines:
                box.add_line(line)

            # Print the box
            box.out()

        return wrapper

    return decorator
