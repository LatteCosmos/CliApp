"""
File-backed Database implementation.

We use Python's built-in ``pickle`` module to serialise the list of
Student objects to ``students.data``.  Pickle plays the same role as
Java's Serializable for the assignment: it lets us round-trip whole
object graphs (Student + nested Subject lists) without inventing a
custom on-disk format.

The brief requires that:
  * the file is created if it does not exist
  * read and write operations both go through this class
  * clearing the file removes all records

We satisfy all three by always reading and writing the entire student
list in one shot.  The file lives at the project root so it is easy to
inspect during marking.
"""

from __future__ import annotations

import os
import pickle
from typing import List

from data.i_database import IDatabase
from model.student import Student


class Database(IDatabase):
    """Concrete IDatabase backed by a pickle file."""

    def __init__(self, file_path: str = "students.data"):
        self._file_path = file_path
        # Make sure the file exists before anyone tries to read from it.
        self._ensure_file_exists()

    # ------------------------------------------------------------------
    # Public API – matches the IDatabase contract
    # ------------------------------------------------------------------
    def load(self) -> List[Student]:
        """Read the stored student list from disk."""
        self._ensure_file_exists()
        # An empty file (size 0) means we never wrote anything yet.
        if os.path.getsize(self._file_path) == 0:
            return []
        try:
            with open(self._file_path, "rb") as f:
                data = pickle.load(f)
                # Defensive: only return the data if it really is a list.
                if isinstance(data, list):
                    return data
                return []
        except (EOFError, pickle.UnpicklingError):
            # Corrupt or truncated file – treat as empty rather than crashing.
            return []

    def save_students(self, student_list: List[Student]) -> None:
        """Overwrite the file with the supplied list."""
        with open(self._file_path, "wb") as f:
            pickle.dump(student_list, f)

    def delete_student(self, student_id: int) -> bool:
        """Find and drop a student by id; return True if found."""
        students = self.load()
        for s in students:
            if s.id == student_id:
                students.remove(s)
                self.save_students(students)
                return True
        return False

    def clear(self) -> None:
        """Remove every record by writing an empty list back to disk."""
        self.save_students([])

    # ------------------------------------------------------------------
    # Convenience helpers used by services and the GUI
    # ------------------------------------------------------------------
    def find_by_email(self, email: str) -> Student | None:
        """Lookup helper for login – returns None if no match."""
        for s in self.load():
            if s.email == email:
                return s
        return None

    def find_by_id(self, student_id: int) -> Student | None:
        for s in self.load():
            if s.id == student_id:
                return s
        return None

    def update_student(self, student: Student) -> None:
        """Replace any stored copy of *student* (matched by id) with the new one."""
        students = self.load()
        for i, s in enumerate(students):
            if s.id == student.id:
                students[i] = student
                self.save_students(students)
                return
        # If we get here the student was not in the file yet – append.
        students.append(student)
        self.save_students(students)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_file_exists(self) -> None:
        if not os.path.exists(self._file_path):
            # Touch the file so subsequent reads/writes always succeed.
            open(self._file_path, "wb").close()
