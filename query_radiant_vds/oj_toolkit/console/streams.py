"""Stream output utilities for writing to stdout and stderr.

Provides a simple Output class for writing messages to standard output and error streams,
with support for colored output using ANSI escape codes and chainable colored text builder.
"""

import sys
from typing import Optional, TextIO

from oj_toolkit.console.colors import Color
from oj_toolkit.console.colored_text import ColoredText


class Output:
    """Simple wrapper for writing to stdout and stderr streams.

    Provides convenient methods for writing to standard output and error streams
    with optional file redirection.

    Attributes:
        stdout: The standard output stream (default: sys.stdout)
        stderr: The standard error stream (default: sys.stderr)
    """

    def __init__(
        self,
        stdout: Optional[TextIO] = None,
        stderr: Optional[TextIO] = None,
    ):
        """Initialize Output with optional custom streams.

        Args:
            stdout: The output stream for normal output. Default: sys.stdout
            stderr: The output stream for error messages. Default: sys.stderr
        """
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def out(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write to standard output stream.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> output = Output()
            >>> output.out("Hello", "World")
            Hello World
            >>> output.out("Status:", "OK", end=" - done\n")
            Status: OK - done
        """
        print(*args, sep=sep, end=end, file=self.stdout, flush=flush)

    def err(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write to standard error stream.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> output = Output()
            >>> output.err("Error:", "File not found")
            Error: File not found
            >>> output.err("Status code: 404", flush=True)
            Status code: 404
        """
        print(*args, sep=sep, end=end, file=self.stderr, flush=flush)

    def out_colored(
        self,
        *args,
        color: str = "",
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write colored output to stdout.

        Args:
            *args: Values to write (converted to strings via str()).
            color: ANSI color code to apply (e.g., Color.RED, Color.BOLD + Color.GREEN).
                   Default: no color.
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> from oj_toolkit.console import Output, Color
            >>> output = Output()
            >>> output.out_colored("Success", color=Color.GREEN)
            >>> output.out_colored("Warning", color=Color.BOLD + Color.YELLOW)
        """
        if color:
            colored_text = color + sep.join(str(arg) for arg in args) + Color.RESET
            print(colored_text, sep="", end=end, file=self.stdout, flush=flush)
        else:
            print(*args, sep=sep, end=end, file=self.stdout, flush=flush)

    def err_colored(
        self,
        *args,
        color: str = "",
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write colored output to stderr.

        Args:
            *args: Values to write (converted to strings via str()).
            color: ANSI color code to apply (e.g., Color.RED, Color.BOLD + Color.YELLOW).
                   Default: no color.
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).

        Example:
            >>> from oj_toolkit.console import Output, Color
            >>> output = Output()
            >>> output.err_colored("Error", color=Color.RED)
            >>> output.err_colored("Fatal", color=Color.BOLD + Color.RED)
        """
        if color:
            colored_text = color + sep.join(str(arg) for arg in args) + Color.RESET
            print(colored_text, sep="", end=end, file=self.stderr, flush=flush)
        else:
            print(*args, sep=sep, end=end, file=self.stderr, flush=flush)

    def out_red(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write red text to stdout.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).
        """
        self.out_colored(*args, color=Color.RED, sep=sep, end=end, flush=flush)

    def out_green(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write green text to stdout.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).
        """
        self.out_colored(*args, color=Color.GREEN, sep=sep, end=end, flush=flush)

    def out_yellow(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write yellow text to stdout.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).
        """
        self.out_colored(*args, color=Color.YELLOW, sep=sep, end=end, flush=flush)

    def out_blue(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write blue text to stdout.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).
        """
        self.out_colored(*args, color=Color.BLUE, sep=sep, end=end, flush=flush)

    def err_red(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write red text to stderr.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).
        """
        self.err_colored(*args, color=Color.RED, sep=sep, end=end, flush=flush)

    def err_green(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write green text to stderr.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).
        """
        self.err_colored(*args, color=Color.GREEN, sep=sep, end=end, flush=flush)

    def err_yellow(
        self,
        *args,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Write yellow text to stderr.

        Args:
            *args: Values to write (converted to strings via str()).
            sep: Separator between args (default: space).
            end: String appended after the last value (default: newline).
            flush: Whether to force flush the stream (default: False).
        """
        self.err_colored(*args, color=Color.YELLOW, sep=sep, end=end, flush=flush)

    def segment(self) -> ColoredText:
        """Create a new chainable ColoredText builder bound to this output.

        Returns a ColoredText instance that outputs to this Output's streams
        when .out() or .err() is called.

        Returns:
            A new ColoredText instance.

        Example:
            >>> output = Output()
            >>> output.segment().red("ERROR: ").white("critical failure").out()
            >>> output.segment().yellow("WARNING").cyan(" - deprecated").err()

            Can also chain and build complex multi-color lines:
            >>> (output.segment()
            ...     .bold("Status: ")
            ...     .green("OK")
            ...     .reset(" (")
            ...     .cyan("2.5s")
            ...     .reset(")")
            ...     .out())
        """
        return ColoredText(stdout=self.stdout, stderr=self.stderr)
