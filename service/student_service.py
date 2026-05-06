"""
StudentService – business logic layer.

The class diagram from Part 1 keeps the Student model focused on data
and pulls all the rule-based logic out into this service.  Both
CLIUniApp and GUIUniApp will use the same StudentService instance, so
behaviour stays consistent across the two interfaces.

Responsibilities:
    * validate emails and passwords
    * generate unique 6-digit student ids
    * generate unique 3-digit subject ids and random marks
    * coordinate the registration workflow
    * authenticate a student during login
"""

from __future__ import annotations

import random
from typing import Optional

from data.i_database import IDatabase
from model.student import Student
from model.subject import Subject
from util import validator


class StudentService:
    """Stateless helper around an IDatabase – no fields except the db."""

    # Brief: student id is 1..999_999, subject id is 1..999.
    STUDENT_ID_MIN = 1
    STUDENT_ID_MAX = 999_999
    SUBJECT_ID_MIN = 1
    SUBJECT_ID_MAX = 999
    SUBJECT_MARK_MIN = 25
    SUBJECT_MARK_MAX = 100

    def __init__(self, database: IDatabase):
        self._db = database

    # ------------------------------------------------------------------
    # Validation – thin wrappers around the regex helpers so callers can
    # depend on the service rather than the util module directly.
    # ------------------------------------------------------------------
    @staticmethod
    def validate_email(email: str) -> bool:
        return validator.is_valid_email(email)

    @staticmethod
    def validate_password(password: str) -> bool:
        return validator.is_valid_password(password)

    @staticmethod
    def credentials_acceptable(email: str, password: str) -> bool:
        return validator.credentials_acceptable(email, password)

    # ------------------------------------------------------------------
    # ID and mark generation
    # ------------------------------------------------------------------
    def generate_student_id(self) -> int:
        """Pick an unused 6-digit student id."""
        existing_ids = {s.id for s in self._db.load()}
        # In practice the keyspace is 1M wide so a collision is unlikely,
        # but we still loop just in case.
        while True:
            candidate = random.randint(self.STUDENT_ID_MIN, self.STUDENT_ID_MAX)
            if candidate not in existing_ids:
                return candidate

    def generate_subject_id(self, student: Student) -> int:
        """Pick a 3-digit id that the *student* doesn't already have."""
        existing_ids = {s.id for s in student.subjects}
        while True:
            candidate = random.randint(self.SUBJECT_ID_MIN, self.SUBJECT_ID_MAX)
            if candidate not in existing_ids:
                return candidate

    def auto_assign_mark(self) -> int:
        return random.randint(self.SUBJECT_MARK_MIN, self.SUBJECT_MARK_MAX)

    # ------------------------------------------------------------------
    # Registration / authentication
    # ------------------------------------------------------------------
    def email_exists(self, email: str) -> bool:
        return self._db.find_by_email(email) is not None

    def register(self, name: str, email: str, password: str) -> Student:
        """Create a Student, persist it and return the new object.

        Callers are expected to have already verified the credentials are
        acceptable and that the email is unique.  We do not duplicate
        those checks here so the calling layer can show its own
        formatted error messages.
        """
        student_id = self.generate_student_id()
        student = Student(student_id, name, email, password)
        # Append rather than overwrite – there may be other students.
        students = self._db.load()
        students.append(student)
        self._db.save_students(students)
        return student

    def authenticate(self, email: str, password: str) -> Optional[Student]:
        """Return the matching Student or ``None`` if credentials don't match."""
        student = self._db.find_by_email(email)
        if student is None:
            return None
        if student.get_password() != password:
            return None
        return student

    # ------------------------------------------------------------------
    # Subject helpers used by the enrolment system
    # ------------------------------------------------------------------
    def create_subject_for(self, student: Student) -> Subject:
        """Build a fully-populated Subject and attach it to *student*."""
        subject_id = self.generate_subject_id(student)
        mark = self.auto_assign_mark()
        return Subject(subject_id, mark)

    def persist(self, student: Student) -> None:
        """Save the latest state of *student* back to the database."""
        self._db.update_student(student)
