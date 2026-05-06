"""
Student domain object.

A Student inherits password handling from User and adds the data that
identifies them as a student: id, name, email and the list of enrolled
subjects.  The ``subjects`` field is a composition relationship – when
the Student object disappears, so do their subjects.
"""

from __future__ import annotations

from typing import List, Optional

from model.subject import Subject
from model.user import User


class Student(User):
    """A registered student in the university system."""

    # Hard cap on enrolment.  Kept on the class so other modules can
    # check the limit without hard-coding 4.
    MAX_SUBJECTS = 4

    def __init__(self, student_id: int, name: str, email: str, password: str):
        super().__init__(password)
        self._id = student_id
        self._name = name
        self._email = email
        self._subjects: List[Subject] = []

    # ------------------------------------------------------------------
    # Accessors – named to match the class diagram in the design doc
    # ------------------------------------------------------------------
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def subjects(self) -> List[Subject]:
        # Return the list directly – the SubjectEnrolmentSystem mutates
        # it, but only via the helper methods on this class.
        return self._subjects

    def display_id(self) -> str:
        """Return the id zero-padded to six digits ('002340', '673358', ...)."""
        return f"{self._id:06d}"

    # ------------------------------------------------------------------
    # Subject management
    # ------------------------------------------------------------------
    def is_enrolment_full(self) -> bool:
        return len(self._subjects) >= Student.MAX_SUBJECTS

    def enrol(self, subject: Subject) -> bool:
        """Attempt to add *subject*.  Returns True on success."""
        if self.is_enrolment_full():
            return False
        self._subjects.append(subject)
        return True

    def remove_subject(self, subject_id: int) -> bool:
        """Remove the subject with *subject_id*.  Returns True if a removal happened."""
        for s in self._subjects:
            if s.id == subject_id:
                self._subjects.remove(s)
                return True
        return False

    def find_subject(self, subject_id: int) -> Optional[Subject]:
        for s in self._subjects:
            if s.id == subject_id:
                return s
        return None

    # ------------------------------------------------------------------
    # Derived data – computed on demand so it is always in sync
    # ------------------------------------------------------------------
    def average_mark(self) -> float:
        """Mean of the marks across all enrolled subjects, or 0 when empty."""
        if not self._subjects:
            return 0.0
        total = sum(s.mark for s in self._subjects)
        return total / len(self._subjects)

    def overall_grade(self) -> str:
        """Apply the same grade boundaries used per-subject to the average mark."""
        avg = self.average_mark()
        if avg >= 85:
            return Subject.GRADE_HD
        if avg >= 75:
            return Subject.GRADE_D
        if avg >= 65:
            return Subject.GRADE_C
        if avg >= 50:
            return Subject.GRADE_P
        return Subject.GRADE_Z

    def is_passing(self) -> bool:
        """Pass = average mark >= 50, per the Part 2 brief."""
        return self.average_mark() >= 50

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------
    def list_line(self) -> str:
        """Format used by the admin 'Student List' view."""
        return f"{self._name} :: {self.display_id()} --> Email: {self._email}"

    def grade_line(self) -> str:
        """Format used by 'Group by grade' and 'PASS/FAIL Partition' output."""
        return (
            f"{self._name} :: {self.display_id()} --> "
            f"GRADE: {self.overall_grade():>2} - MARK: {self.average_mark():.2f}"
        )
