"""ANSI color codes for terminal output.

Provides color constants and utilities for colored terminal output using ANSI escape codes.
Supports standard colors and text styles (bold, dim, etc.).
"""


class Color:  # pylint: disable=too-few-public-methods
    """ANSI color codes for terminal output.

    Standard ANSI color codes for use with terminal emulators that support color.
    Works on modern terminals (Linux, macOS, Windows 10+).

    Attributes:
        RESET: Reset to default terminal color
        BOLD: Bold text
        DIM: Dim/faint text
        RED: Red text
        GREEN: Green text
        YELLOW: Yellow text
        BLUE: Blue text
        MAGENTA: Magenta text
        CYAN: Cyan text
        WHITE: White text
    """

    # Reset
    RESET = "\033[0m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @staticmethod
    def colorize(text: str, color: str = "", reset: bool = True) -> str:
        """Apply a color code to text.

        Args:
            text: The text to colorize.
            color: The color code to apply (e.g., Color.RED, Color.BOLD, etc.).
                   Can be combined with + (e.g., Color.BOLD + Color.RED).
            reset: Whether to append Color.RESET at the end (default: True).

        Returns:
            The text wrapped in color codes.

        Example:
            >>> colored = Color.colorize("Warning", Color.YELLOW)
            >>> print(colored)
            # Output appears in yellow on supported terminals

            >>> bold_red = Color.colorize("Error", Color.BOLD + Color.RED)
            >>> print(bold_red)
            # Output appears in bold red
        """
        if not color:
            return text
        return color + text + (Color.RESET if reset else "")
