"""Chainable colored text builder for composing multi-color output.

Provides ColoredText class for building colorized strings with fluent API,
supporting iterables and convenient color methods.
"""

import sys
from typing import Iterator, Optional, TextIO, Tuple

from query_radiant_vds.oj_toolkit.console.colors import Color


class ColoredText:
    """Chainable builder for colorized text segments.

    Accumulates text segments with associated colors, supporting:
    - Fluent chaining API for adding colored segments
    - Consumption of iterables of (text, color) tuples
    - Iteration over segments
    - ANSI-coded string rendering
    - Direct output to stdout/stderr

    Example:
        >>> text = (ColoredText()
        ...     .red("ERROR: ")
        ...     .white("something went wrong")
        ...     .cyan(" (code: 500)")
        ... )
        >>> print(text)  # Prints with colors
        >>> for segment_text, color in text:
        ...     print(f"{color}{segment_text}", end="")
    """

    def __init__(self, stdout: Optional[TextIO] = None, stderr: Optional[TextIO] = None):
        """Initialize empty ColoredText.

        Args:
            stdout: Output stream for .out() method (default: sys.stdout).
            stderr: Error stream for .err() method (default: sys.stderr).
        """
        self.segments: list[Tuple[str, str]] = []
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def add(self, text: str, color: str = "") -> "ColoredText":
        """Add a segment with optional color.

        Args:
            text: The text to add.
            color: The color code to apply (default: no color).

        Returns:
            Self for method chaining.
        """
        self.segments.append((str(text), color))
        return self

    def red(self, text: str) -> "ColoredText":
        """Add red text. Shorthand for add(text, Color.RED)."""
        return self.add(text, Color.RED)

    def green(self, text: str) -> "ColoredText":
        """Add green text. Shorthand for add(text, Color.GREEN)."""
        return self.add(text, Color.GREEN)

    def yellow(self, text: str) -> "ColoredText":
        """Add yellow text. Shorthand for add(text, Color.YELLOW)."""
        return self.add(text, Color.YELLOW)

    def blue(self, text: str) -> "ColoredText":
        """Add blue text. Shorthand for add(text, Color.BLUE)."""
        return self.add(text, Color.BLUE)

    def magenta(self, text: str) -> "ColoredText":
        """Add magenta text. Shorthand for add(text, Color.MAGENTA)."""
        return self.add(text, Color.MAGENTA)

    def cyan(self, text: str) -> "ColoredText":
        """Add cyan text. Shorthand for add(text, Color.CYAN)."""
        return self.add(text, Color.CYAN)

    def white(self, text: str) -> "ColoredText":
        """Add white text. Shorthand for add(text, Color.WHITE)."""
        return self.add(text, Color.WHITE)

    def bold(self, text: str) -> "ColoredText":
        """Add bold text. Shorthand for add(text, Color.BOLD)."""
        return self.add(text, Color.BOLD)

    def dim(self, text: str) -> "ColoredText":
        """Add dim text. Shorthand for add(text, Color.DIM)."""
        return self.add(text, Color.DIM)

    def reset(self, text: str) -> "ColoredText":
        """Add text with reset color. Shorthand for add(text, Color.RESET)."""
        return self.add(text, Color.RESET)

    def from_iter(self, iterable: Iterator[Tuple[str, str]]) -> "ColoredText":
        """Consume an iterable of (text, color) tuples.

        Args:
            iterable: Iterator yielding (text, color) tuples.

        Returns:
            Self for method chaining.

        Example:
            >>> def color_gen():
            ...     yield ("Status: ", Color.BOLD)
            ...     yield ("OK", Color.GREEN)
            >>> text = ColoredText().from_iter(color_gen())
            >>> print(text)
        """
        for text, color in iterable:
            self.add(text, color)
        return self

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        """Iterate over (text, color) segments.

        Yields:
            Tuples of (text, color_code) for each segment.

        Example:
            >>> text = ColoredText().red("ERROR").white(": failed")
            >>> for segment_text, color in text:
            ...     print(f"{color}{segment_text}\033[0m", end="")
        """
        return iter(self.segments)

    def __str__(self) -> str:
        """Render as ANSI-coded string.

        Returns:
            The complete string with all color codes applied.
            Each colored segment is wrapped with its color code and reset.

        Example:
            >>> text = ColoredText().red("ERROR").white(": failed")
            >>> print(str(text))  # Renders with ANSI codes
        """
        result = []
        for text, color in self.segments:
            if color:
                result.append(color + text + Color.RESET)
            else:
                result.append(text)
        return "".join(result)

    def out(
        self,
        sep: str = "",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Print to stdout.

        Args:
            sep: Separator between segments (default: empty, segments concatenated).
            end: String appended after output (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> from oj_toolkit import Output
            >>> o = Output()
            >>> o.segment().red("ERROR").white(": failed").out()
        """
        print(str(self), sep=sep, end=end, file=self._stdout, flush=flush)

    def err(
        self,
        sep: str = "",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Print to stderr.

        Args:
            sep: Separator between segments (default: empty, segments concatenated).
            end: String appended after output (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> from oj_toolkit import Output
            >>> o = Output()
            >>> o.segment().red("ERROR").white(": critical").err()
        """
        print(str(self), sep=sep, end=end, file=self._stderr, flush=flush)
