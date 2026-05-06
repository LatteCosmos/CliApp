"""
Unit tests for data.database.

Each test runs against a temporary file that is created in setUp and
removed in tearDown so the suite never touches the real
students.data.
"""

import os
import tempfile
import unittest

from data.database import Database
from model.student import Student
from model.subject import Subject


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        # NamedTemporaryFile + delete=False gives us a guaranteed-unique
        # path that we control the lifecycle of.
        fd, self._path = tempfile.mkstemp(suffix=".data")
        os.close(fd)
        os.remove(self._path)
        self._db = Database(self._path)

    def tearDown(self):
        if os.path.exists(self._path):
            os.remove(self._path)

    # ------------------------------------------------------------------
    # Round-trip tests
    # ------------------------------------------------------------------
    def test_load_returns_empty_list_when_file_is_fresh(self):
        self.assertEqual([], self._db.load())

    def test_save_then_load_roundtrips_one_student(self):
        student = Student(123, "Test User", "test.user@university.com",
                          "Helloworld123")
        self._db.save_students([student])

        loaded = self._db.load()
        self.assertEqual(1, len(loaded))
        self.assertEqual("test.user@university.com", loaded[0].email)
        self.assertEqual("Test User", loaded[0].name)

    def test_save_preserves_subject_list(self):
        student = Student(7, "Sub Owner", "sub.owner@university.com",
                          "Helloworld123")
        student.enrol(Subject(101, 90))
        student.enrol(Subject(202, 40))
        self._db.save_students([student])

        loaded = self._db.load()[0]
        self.assertEqual(2, len(loaded.subjects))
        self.assertEqual({101, 202}, {s.id for s in loaded.subjects})

    def test_clear_empties_the_file(self):
        s = Student(1, "Doomed Student", "doomed.student@university.com",
                    "Helloworld123")
        self._db.save_students([s])
        self._db.clear()
        self.assertEqual([], self._db.load())

    def test_delete_student_removes_only_match(self):
        a = Student(1, "Alice User", "alice.user@university.com", "Helloworld123")
        b = Student(2, "Bob Smith", "bob.smith@university.com", "Helloworld123")
        self._db.save_students([a, b])

        self.assertTrue(self._db.delete_student(1))
        remaining = self._db.load()
        self.assertEqual([2], [s.id for s in remaining])

    def test_delete_student_returns_false_when_missing(self):
        self.assertFalse(self._db.delete_student(999))

    def test_find_by_email_returns_match(self):
        s = Student(5, "Found Me", "found.me@university.com", "Helloworld123")
        self._db.save_students([s])
        self.assertIsNotNone(self._db.find_by_email("found.me@university.com"))
        self.assertIsNone(self._db.find_by_email("nope@university.com"))


if __name__ == "__main__":
    unittest.main()
