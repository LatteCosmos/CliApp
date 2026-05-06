"""
Subject domain object.

Each Subject has an auto-generated 3-digit id (1..999), a random mark
between 25 and 100, and a grade that is derived from the mark.

The Subject is intentionally a lightweight value-style object: ID
generation and mark generation belong to the StudentService class so
that the rule logic stays in one place (single responsibility).
"""

from __future__ import annotations


class Subject:
    """Represents one subject a student is enrolled in."""

    # Grade boundaries are class-level constants so they can be
    # referenced from tests or other modules without magic numbers.
    GRADE_HD = "HD"
    GRADE_D = "D"
    GRADE_C = "C"
    GRADE_P = "P"
    GRADE_Z = "Z"

    def __init__(self, subject_id: int, mark: int):
        # _id is a plain integer; we format it on display only.
        self._id = subject_id
        self._mark = mark
        self._grade = self._calculate_grade(mark)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    @property
    def id(self) -> int:
        return self._id

    @property
    def mark(self) -> int:
        return self._mark

    @property
    def grade(self) -> str:
        return self._grade

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _calculate_grade(mark: int) -> str:
        """Map a numeric mark onto the UTS grade scale used by the brief."""
        if mark >= 85:
            return Subject.GRADE_HD
        if mark >= 75:
            return Subject.GRADE_D
        if mark >= 65:
            return Subject.GRADE_C
        if mark >= 50:
            return Subject.GRADE_P
        return Subject.GRADE_Z

    # ------------------------------------------------------------------
    # Display helpers – keep formatting in one place to make sample I/O
    # matching easier later on.
    # ------------------------------------------------------------------
    def display_id(self) -> str:
        """Return the id zero-padded to three digits, as in '[ Subject::097 ... ]'."""
        return f"{self._id:03d}"

    def __repr__(self) -> str:
        # Matches the sample line "[ Subject::541 -- mark = 55 -- grade =  P ]"
        # Grade is right-aligned in a 2-character field so HD lines up with P/C/D/Z.
        return f"[ Subject::{self.display_id()} -- mark = {self._mark} -- grade = {self._grade:>2} ]"
