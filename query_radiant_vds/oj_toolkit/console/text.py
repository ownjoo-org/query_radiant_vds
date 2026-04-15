# pylint: disable=duplicate-code
"""Text formatting utilities and decorators.

Provides functions for text alignment, padding, truncation, and the @boxed
decorator for wrapping function output in decorative boxes.
"""

from functools import wraps
from typing import Callable, Optional

from query_radiant_vds.oj_toolkit.console.box import Box
from query_radiant_vds.oj_toolkit.console.terminal import pad_visible, truncate_visible


def pad_left(text: str, width: int, fill: str = " ") -> str:
    """Left-pad text to width.

    Args:
        text: Text to pad.
        width: Target width.
        fill: Character to use for padding (default: space).

    Returns:
        Left-padded text.

    Example:
        >>> pad_left("Hi", 5)
        '   Hi'
    """
    return pad_visible(text, width, align="right", fill=fill)


def pad_right(text: str, width: int, fill: str = " ") -> str:
    """Right-pad text to width.

    Args:
        text: Text to pad.
        width: Target width.
        fill: Character to use for padding (default: space).

    Returns:
        Right-padded text.

    Example:
        >>> pad_right("Hi", 5)
        'Hi   '
    """
    return pad_visible(text, width, align="left", fill=fill)


def center(text: str, width: int, fill: str = " ") -> str:
    """Center text within width.

    Args:
        text: Text to center.
        width: Target width.
        fill: Character to use for padding (default: space).

    Returns:
        Centered text.

    Example:
        >>> center("Hi", 5)
        ' Hi  '
    """
    return pad_visible(text, width, align="center", fill=fill)


def truncate(text: str, width: int, suffix: str = "...") -> str:
    """Truncate text to width with suffix.

    Args:
        text: Text to truncate.
        width: Maximum visible width.
        suffix: Suffix to append if truncated (default: "...").

    Returns:
        Truncated text.

    Example:
        >>> truncate("Hello World", 8)
        'Hello...'
    """
    return truncate_visible(text, width, suffix=suffix)


def repeat(text: str, count: int) -> str:
    """Repeat text count times.

    Useful for creating horizontal lines or patterns.

    Args:
        text: Text to repeat.
        count: Number of repetitions.

    Returns:
        Repeated text.

    Example:
        >>> repeat("=", 10)
        '=========='
        >>> repeat("ab", 3)
        'ababab'
    """
    return text * count


def boxed(
    style: str = "auto",
    padding: int = 1,
    width: Optional[int] = None,
    title: Optional[str] = None,
) -> Callable:
    """Decorator to wrap function output in a decorative box.

    Wraps a function's return value in a box with specified style and options.
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
        >>> from query_radiant_vds.oj_toolkit.console import boxed
        >>> @boxed(style='rounded')
        ... def greeting():
        ...     return "Hello from a box"
        >>> greeting()  # Prints: ╭─────────────────╮
                             │ Hello from a box │
                             ╰─────────────────╯

        >>> @boxed(style='double', title="Status")
        ... def show_status():
        ...     return ["Item 1", "Item 2"]
        >>> show_status()  # Prints items in a double-line box with title
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
