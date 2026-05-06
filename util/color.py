"""
ANSI escape code helpers for coloured CLI output.

The sample I/O in the assessment uses several colours to highlight
different kinds of messages, so we group the codes into semantic
categories instead of just exposing raw escape codes.

Colour palette derived from the sample:
    cyan    -> menu prompts (e.g. "Admin System (c/g/p/r/s/x): ")
    green   -> sub-menu titles ("Student Sign In", "Student Sign Up")
    yellow  -> status / action messages ("Updating Password", ...)
    red     -> errors and warning prompts
"""

# Reset sequence
RESET = "\033[0m"

# Foreground colours
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"


def cyan(text: str) -> str:
    """Wrap ``text`` in cyan – used for interactive menu prompts."""
    return f"{CYAN}{text}{RESET}"


def green(text: str) -> str:
    """Wrap ``text`` in green – used for screen titles like 'Student Sign Up'."""
    return f"{GREEN}{text}{RESET}"


def yellow(text: str) -> str:
    """Wrap ``text`` in yellow – used for status updates / acceptance notices."""
    return f"{YELLOW}{text}{RESET}"


def red(text: str) -> str:
    """Wrap ``text`` in red – used for errors or destructive confirmations."""
    return f"{RED}{text}{RESET}"


def magenta(text: str) -> str:
    """Optional accent colour – kept available for future use."""
    return f"{MAGENTA}{text}{RESET}"
