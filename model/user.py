"""
Abstract user superclass.

Both Student and Admin extend User and inherit password handling.
We model User with Python's ``abc`` module so the inheritance is
visible in the diagram and so accidental instantiation raises early.
"""

from abc import ABC


class User(ABC):
    """Common base type for any account-holder in the system."""

    def __init__(self, password: str):
        # The single underscore signals "treat as protected".  The brief's
        # class diagram says password is private so we expose it through
        # methods only.
        self._password = password

    # Plain accessor – the diagram lists ``getPassword``.
    def get_password(self) -> str:
        return self._password

    def change_password(self, new_password: str) -> None:
        """Update the stored password.  Validation is the caller's job."""
        self._password = new_password
