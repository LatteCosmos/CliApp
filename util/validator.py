"""
Validation helpers for email addresses and passwords.

Both rules are taken straight from the project brief and are expressed
as compiled regular expressions so they can be reused without paying
the compile cost on every call.

Email rule
    firstname.lastname@university.com
    -> only lowercase letters allowed in the local part to keep it
       consistent with the sample I/O ("alen.jones@university.com").

Password rule
    1) starts with an upper-case letter
    2) contains at least five letters in total
    3) is followed by three or more digits at the end
"""

import re


# Email: lowercase-only local part, single dot separator, fixed domain.
# Examples that pass: alen.jones@university.com, john.smith@university.com
# Examples that fail: alen@university.com, alen.jones@university (no .com)
_EMAIL_PATTERN = re.compile(r"^[a-z]+\.[a-z]+@university\.com$")

# Password: ^[A-Z][A-Za-z]{5,}\d{3,}$
#   ^[A-Z]            uppercase first character
#   [A-Za-z]{5,}      at least five more letters (so 6+ letters total)
#   \d{3,}$           three or more digits at the very end
#
# We arrived at the {5,} count empirically from the sample I/O – the
# document shows "Hello123" being rejected but "Helloworld123" being
# accepted, so "contains at least five (5) letters" really means
# "five letters AFTER the leading capital".
_PASSWORD_PATTERN = re.compile(r"^[A-Z][A-Za-z]{5,}\d{3,}$")


def is_valid_email(email: str) -> bool:
    """Return True if *email* matches the firstname.lastname@university.com format."""
    if email is None:
        return False
    return _EMAIL_PATTERN.match(email) is not None


def is_valid_password(password: str) -> bool:
    """Return True if *password* satisfies the project's three rules."""
    if password is None:
        return False
    return _PASSWORD_PATTERN.match(password) is not None


def credentials_acceptable(email: str, password: str) -> bool:
    """Convenience wrapper used by both the CLI and GUI flows."""
    return is_valid_email(email) and is_valid_password(password)
