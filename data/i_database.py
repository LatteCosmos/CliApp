"""
Database interface.

Python doesn't have a dedicated ``interface`` keyword, so we use
``abc.ABC`` to mark this as a contract that concrete classes must
fulfill.  Keeping this separate from the implementation gives us the
DIP (Dependency Inversion Principle) we documented in the design:
high-level modules depend on this abstraction, not on the concrete
file-based class.
"""

from abc import ABC, abstractmethod
from typing import List

from model.student import Student


class IDatabase(ABC):
    """Contract for any object that can persist Student records."""

    @abstractmethod
    def load(self) -> List[Student]:
        """Return all stored students.  An empty list when nothing exists yet."""

    @abstractmethod
    def save_students(self, student_list: List[Student]) -> None:
        """Replace the stored data with *student_list*."""

    @abstractmethod
    def delete_student(self, student_id: int) -> bool:
        """Remove the student with *student_id*.  Returns True on success."""

    @abstractmethod
    def clear(self) -> None:
        """Wipe all stored data."""
