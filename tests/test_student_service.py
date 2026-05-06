"""
Unit tests for service.student_service.

Where the database tests verify persistence, these tests focus on the
business rules: id generation, subject enrolment limits, grade
calculation, etc.

We use a small in-memory IDatabase fake instead of the real one so the
tests stay independent of disk state and run quickly.
"""

import unittest
from typing import List

from data.i_database import IDatabase
from model.student import Student
from model.subject import Subject
from service.student_service import StudentService


class _FakeDatabase(IDatabase):
    """Tiny in-memory IDatabase double for service-layer tests."""

    def __init__(self):
        self._students: List[Student] = []

    def load(self):
        return list(self._students)

    def save_students(self, student_list):
        self._students = list(student_list)

    def delete_student(self, student_id):
        for s in self._students:
            if s.id == student_id:
                self._students.remove(s)
                return True
        return False

    def clear(self):
        self._students.clear()

    # The Database concrete class also exposes these helpers; the service
    # uses ``find_by_email`` and ``update_student`` so we match the
    # surface area here.
    def find_by_email(self, email):
        for s in self._students:
            if s.email == email:
                return s
        return None

    def find_by_id(self, student_id):
        for s in self._students:
            if s.id == student_id:
                return s
        return None

    def update_student(self, student):
        for i, s in enumerate(self._students):
            if s.id == student.id:
                self._students[i] = student
                return
        self._students.append(student)


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.db = _FakeDatabase()
        self.service = StudentService(self.db)

    def test_generated_student_id_is_in_range(self):
        for _ in range(20):
            sid = self.service.generate_student_id()
            self.assertTrue(StudentService.STUDENT_ID_MIN <= sid <= StudentService.STUDENT_ID_MAX)

    def test_generated_subject_id_is_three_digit(self):
        student = Student(1, "Test Holder", "test.holder@university.com", "Helloworld123")
        for _ in range(10):
            sid = self.service.generate_subject_id(student)
            self.assertTrue(1 <= sid <= 999)

    def test_auto_assigned_mark_is_in_range(self):
        for _ in range(20):
            mark = self.service.auto_assign_mark()
            self.assertTrue(25 <= mark <= 100)


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.db = _FakeDatabase()
        self.service = StudentService(self.db)

    def test_register_persists_student(self):
        student = self.service.register("John Smith", "john.smith@university.com", "Helloworld123")
        self.assertEqual(1, len(self.db.load()))
        self.assertEqual("john.smith@university.com", student.email)

    def test_email_exists_after_registration(self):
        self.assertFalse(self.service.email_exists("john.smith@university.com"))
        self.service.register("John Smith", "john.smith@university.com", "Helloworld123")
        self.assertTrue(self.service.email_exists("john.smith@university.com"))

    def test_authenticate_with_correct_credentials(self):
        self.service.register("John Smith", "john.smith@university.com", "Helloworld123")
        student = self.service.authenticate("john.smith@university.com", "Helloworld123")
        self.assertIsNotNone(student)

    def test_authenticate_rejects_wrong_password(self):
        self.service.register("John Smith", "john.smith@university.com", "Helloworld123")
        self.assertIsNone(self.service.authenticate("john.smith@university.com", "Helloworld999"))

    def test_authenticate_rejects_unknown_email(self):
        self.assertIsNone(self.service.authenticate("ghost@university.com", "Helloworld123"))


class GradeAndEnrolmentTests(unittest.TestCase):
    """Verify the rules expressed in the brief and the design diagram."""

    def test_grade_boundaries(self):
        self.assertEqual("Z", Subject(1, 49).grade)
        self.assertEqual("P", Subject(1, 50).grade)
        self.assertEqual("P", Subject(1, 64).grade)
        self.assertEqual("C", Subject(1, 65).grade)
        self.assertEqual("C", Subject(1, 74).grade)
        self.assertEqual("D", Subject(1, 75).grade)
        self.assertEqual("D", Subject(1, 84).grade)
        self.assertEqual("HD", Subject(1, 85).grade)
        self.assertEqual("HD", Subject(1, 100).grade)

    def test_max_four_subjects(self):
        student = Student(1, "Limit Tester", "limit.tester@university.com", "Helloworld123")
        for i in range(4):
            self.assertTrue(student.enrol(Subject(i + 1, 60)))
        # The fifth attempt has to fail.
        self.assertFalse(student.enrol(Subject(5, 60)))
        self.assertEqual(4, len(student.subjects))

    def test_average_mark_and_pass(self):
        student = Student(1, "Pass Tester", "pass.tester@university.com", "Helloworld123")
        student.enrol(Subject(1, 60))
        student.enrol(Subject(2, 70))
        student.enrol(Subject(3, 50))
        student.enrol(Subject(4, 80))
        # mean = 65 -> grade C, passing.
        self.assertAlmostEqual(65.0, student.average_mark())
        self.assertTrue(student.is_passing())
        self.assertEqual("C", student.overall_grade())

    def test_remove_subject(self):
        student = Student(1, "Remove Tester", "remove.tester@university.com", "Helloworld123")
        student.enrol(Subject(101, 60))
        student.enrol(Subject(102, 70))
        self.assertTrue(student.remove_subject(101))
        self.assertEqual(1, len(student.subjects))
        self.assertFalse(student.remove_subject(999))


if __name__ == "__main__":
    unittest.main()
