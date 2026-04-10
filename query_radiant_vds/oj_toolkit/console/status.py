"""Status indicators and progress display utilities.

Provides simple utilities for displaying status information, progress bars,
and status badges with optional colors.
"""

import sys
from functools import wraps
from typing import Callable, Optional

from oj_toolkit.console.colors import Color


def status_line(
    label: str, value: str, color: Optional[str] = None, sep: str = ": "
) -> str:
    """Format a label-value status line with optional color.

    Args:
        label: The label (e.g., "Status", "Error").
        value: The value to display.
        color: Optional ANSI color code to apply to the value.
        sep: Separator between label and value (default: ": ").

    Returns:
        Formatted status line string.

    Example:
        >>> from oj_toolkit.console import status_line, Color
        >>> status_line("Status", "OK", Color.GREEN)
        'Status: OK'  (with green color on OK)
    """
    value_str = str(value)
    if color:
        value_str = color + value_str + Color.RESET
    return f"{label}{sep}{value_str}"


def progress_bar(
    percent: float,
    width: int = 20,
    filled: str = "█",
    empty: str = "░",
    label: Optional[str] = None,
) -> str:
    """Create a text-based progress bar.

    Args:
        percent: Progress percentage (0-100).
        width: Width of the bar in characters (default: 20).
        filled: Character for filled portion (default: "█").
        empty: Character for empty portion (default: "░").
        label: Optional label prefix (e.g., "Loading").

    Returns:
        Progress bar string.

    Example:
        >>> progress_bar(75)
        '█████████████░░░░░░░░░░░░'
        >>> progress_bar(50, width=10, label="Progress")
        'Progress: █████░░░░░░  50%'
    """
    # Clamp percent to 0-100
    percent = max(0, min(100, percent))

    # Calculate filled and empty portions
    filled_count = int((percent / 100) * width)
    empty_count = width - filled_count

    progress_str = filled * filled_count + empty * empty_count

    if label:
        return f"{label}: {progress_str}  {percent:>3.0f}%"
    return f"{progress_str}  {percent:>3.0f}%"


def status_badge(text: str, status: str = "info") -> str:
    """Format a status badge with semantic coloring.

    Args:
        text: Text to display in the badge.
        status: Badge status type ('ok', 'error', 'warning', 'info').
            Default: 'info'.

    Returns:
        Colored status badge string.

    Example:
        >>> status_badge("READY", "ok")
        '[OK] READY'  (in green)
        >>> status_badge("FAILED", "error")
        '[ERROR] FAILED'  (in red)
    """
    status_upper = status.upper()

    # Map status to color
    colors = {
        "ok": Color.GREEN,
        "error": Color.RED,
        "warning": Color.YELLOW,
        "info": Color.CYAN,
    }
    color = colors.get(status.lower(), Color.CYAN)

    badge = f"[{status_upper}]"
    colored_badge = color + badge + Color.RESET

    return f"{colored_badge} {text}"


def status_wrapped(status: str = "info") -> Callable:
    """Decorator to prepend a status badge to function output.

    Wraps a function and prepends a status badge (with color) to its output.
    The function should return a string.

    Args:
        status: Badge status type ('ok', 'error', 'warning', 'info').
            Default: 'info'.

    Returns:
        Decorator function.

    Example:
        >>> from oj_toolkit.console import status_wrapped
        >>> @status_wrapped(status='ok')
        ... def operation():
        ...     return "Operation complete"
        >>> operation()
        # Prints: [OK] Operation complete (in green)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            output = status_badge(str(result), status)
            print(output, file=sys.stdout)

        return wrapper

    return decorator
