"""Terminal capability detection and shared formatting utilities.

Provides functions for detecting terminal capabilities (Unicode support, colors)
and utility functions shared across all formatting modules (width calculation,
style selection, etc.).
"""

import os
import re
import sys
from typing import Optional, Tuple


def detect_unicode_support() -> bool:
    """Detect if terminal supports Unicode characters.

    Checks environment variables and terminal type to determine if the terminal
    can display Unicode characters (for pretty borders, etc.).

    Environment checks:
    - NO_COLOR: If set, disables colors/Unicode for accessibility
    - TERM: Terminal type (vt100, xterm, etc.)
    - CI: If in CI environment, assume Unicode support
    - Platform: Windows console has limited Unicode, *nix terminals usually support it

    Returns:
        True if terminal likely supports Unicode, False otherwise.

    Example:
        >>> if detect_unicode_support():
        ...     style = 'rounded'  # Use Unicode borders
        ... else:
        ...     style = 'ascii'    # Use ASCII borders
    """
    # Respect NO_COLOR environment variable (accessibility/compliance)
    if os.environ.get("NO_COLOR"):
        return False

    # CI environments usually support Unicode
    if os.environ.get("CI"):
        return True

    # Check TERM environment variable
    term = os.environ.get("TERM", "").lower()
    if term in ("dumb", "vt100", "vt220"):
        return False

    # Windows console (cmd.exe, PowerShell) has limited Unicode support
    # but modern versions and Windows Terminal support it
    if sys.platform == "win32":
        # Assume modern Windows (10+) or Windows Terminal supports Unicode
        # Could be more conservative here if needed
        return True

    # *nix terminals typically support Unicode
    if sys.platform in ("linux", "darwin"):
        return True

    # Default: attempt Unicode
    return True


def select_style(
    style: str,
    ascii_fallback: str,
    unicode_primary: str,
) -> str:
    """Select between ASCII and Unicode style based on terminal capabilities.

    Args:
        style: The requested style ('auto', 'ascii', or a Unicode style name).
        ascii_fallback: ASCII style to use if Unicode not supported (e.g., 'ascii').
        unicode_primary: Unicode style to use if supported (e.g., 'rounded').

    Returns:
        The selected style string.

    Example:
        >>> style = select_style('auto', 'ascii', 'rounded')
        >>> # Returns 'rounded' on Unicode terminals, 'ascii' otherwise
    """
    if style == "auto":
        if detect_unicode_support():
            return unicode_primary
        return ascii_fallback
    return style


def visible_width(text: str) -> int:
    """Calculate visible width of text, excluding ANSI color codes.

    ANSI escape sequences (color codes) don't take up visible space but
    would normally be counted by len(). This function strips them and
    returns only the visible character width.

    Args:
        text: Text that may contain ANSI escape sequences.

    Returns:
        The number of visible characters (excluding ANSI codes).

    Example:
        >>> from query_radiant_vds.oj_toolkit.console import Color
        >>> colored = f"{Color.RED}Error{Color.RESET}"
        >>> visible_width(colored)  # Returns 5, not 20+
        5
    """
    # ANSI escape sequence pattern: ESC [ ... (letter)
    # Matches: \033[...m or \x1b[...m patterns
    ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
    stripped = ansi_pattern.sub("", text)
    return len(stripped)


def pad_visible(text: str, width: int, align: str = "left", fill: str = " ") -> str:
    """Pad text to visible width, accounting for ANSI codes.

    Pads text to the specified visible width while preserving any ANSI
    color codes in the output. Useful for aligning colored text in tables.

    Args:
        text: Text to pad (may contain ANSI codes).
        width: Target visible width.
        align: Alignment: 'left', 'right', or 'center'.
        fill: Character to use for padding (default: space).

    Returns:
        Padded text with correct visible width.

    Example:
        >>> from query_radiant_vds.oj_toolkit.console import Color
        >>> colored = f"{Color.RED}Hi{Color.RESET}"
        >>> padded = pad_visible(colored, 10, align='left')
        >>> visible_width(padded)  # Returns 10
        10
    """
    current_width = visible_width(text)
    if current_width >= width:
        return text

    padding_needed = width - current_width

    if align == "left":
        return text + (fill * padding_needed)
    if align == "right":
        return (fill * padding_needed) + text
    if align == "center":
        left_pad = padding_needed // 2
        right_pad = padding_needed - left_pad
        return (fill * left_pad) + text + (fill * right_pad)

    return text


def truncate_visible(text: str, width: int, suffix: str = "...") -> str:
    """Truncate text to visible width, preserving ANSI codes.

    Truncates text to fit within the specified visible width, accounting
    for ANSI color codes. Appends suffix if truncation occurs.

    Args:
        text: Text to truncate (may contain ANSI codes).
        width: Maximum visible width.
        suffix: String to append if truncated (default: "...").

    Returns:
        Truncated text, or original if already within width.

    Example:
        >>> text = "Hello World"
        >>> truncate_visible(text, 8)
        'Hello...'
    """
    current_width = visible_width(text)
    if current_width <= width:
        return text

    # Need to truncate - strip ANSI codes, truncate, and reapply
    # This is approximate since we lose the color info
    ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
    stripped = ansi_pattern.sub("", text)

    target_length = width - len(suffix)
    if target_length < 1:
        return suffix[: width]

    return stripped[:target_length] + suffix


def border_chars(style: str) -> Tuple[str, str, str, str, str, str, str, str, str, str, str, str, str]:
    """Get border characters for a given style.

    Returns the 13 border characters needed for a table:
    (tl, tr, bl, br, top, bottom, left, right, cross, top_cross, sep_left, sep_cross, sep_right, bottom_cross)

    The first 9 are for boxes (top-left, top-right, bottom-left, bottom-right, top, bottom, left, right, cross).
    The last 4 are for table header separators (top_cross, sep_left, sep_cross, sep_right, bottom_cross).

    Args:
        style: Border style ('ascii', 'rounded', 'double', 'single', 'none', etc.).

    Returns:
        Tuple of (tl, tr, bl, br, top, bottom, left, right, cross,
        top_cross, sep_left, sep_cross, sep_right, bottom_cross).

    Example:
        >>> chars = border_chars('rounded')
        >>> print(f"{chars[0]}{chars[4]}{chars[1]}")  # ╭─╮
    """
    styles = {
        # Format: (tl, tr, bl, br, top, bottom, left, right, cross,
        #          top_cross, sep_left, sep_cross, sep_right, bottom_cross)
        "ascii": ("+", "+", "+", "+", "-", "-", "|", "|", "+", "+", "+", "+", "+", "+"),
        "rounded": ("╭", "╮", "╰", "╯", "─", "─", "│", "│", "┼", "┬", "├", "┼", "┤", "┴"),
        "double": ("╔", "╗", "╚", "╝", "═", "═", "║", "║", "╬", "╦", "╠", "╬", "╣", "╩"),
        "single": ("┌", "┐", "└", "┘", "─", "─", "│", "│", "┼", "┬", "├", "┼", "┤", "┴"),
        "solid": ("█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"),
        "none": (" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "),
    }

    return styles.get(style, styles["ascii"])


def horizontal_line(width: int, style: str = "ascii", char: Optional[str] = None) -> str:
    """Create a horizontal line of specified width.

    Args:
        width: Width of the line.
        style: Border style for character selection.
        char: Override character (use instead of style's character).

    Returns:
        A horizontal line string.

    Example:
        >>> line = horizontal_line(10, style='rounded')
        >>> print(line)  # ──────────
    """
    if char:
        return char * width

    chars = border_chars(style)
    line_char = chars[4]  # 5th element is the top/horizontal line character
    return line_char * width
