"""
tests/test_admin_system.py
============================
AdminSystem 的行为测试，特别针对 Sample I/O 中容易踩坑的细节：
  - Group by grade 必须按 Z → P → C → D → HD 排序输出
    （Brief 第 6 页：P 在 C 前面，即使数据库里 C 学生先注册）
  - PASS/FAIL Partition 在 db 为空时仍然显示 FAIL --> [] 和 PASS --> []
  - Student List / Grade Grouping 在 db 为空时显示 < Nothing to Display >

这些细节直接关系到 "Matching I/O" (1 mark) 的得失。

【实现细节】
我们用 io.StringIO 重定向 sys.stdout 来捕获实际输出，再做 assert。
用 _FakeDatabase 避开真实文件 I/O。
"""

import io
import sys
import unittest

from cli.admin_system import AdminSystem
from data.i_database import IDatabase
from model.student import Student
from model.subject import Subject


class _FakeDatabase(IDatabase):
    """In-memory IDatabase——和 service 测试里那个同思路。"""

    def __init__(self, students=None):
        self._students = list(students or [])

    def load(self):
        return list(self._students)

    def save_students(self, lst):
        self._students = list(lst)

    def delete_student(self, student_id: int) -> bool:
        for s in self._students:
            if s.id == student_id:
                self._students.remove(s)
                return True
        return False

    def clear(self) -> None:
        self._students = []

    def find_by_email(self, email):
        return next((s for s in self._students if s.email == email), None)

    def find_by_id(self, sid):
        return next((s for s in self._students if s.id == sid), None)

    def update_student(self, student) -> None:
        for i, s in enumerate(self._students):
            if s.id == student.id:
                self._students[i] = student
                return
        self._students.append(student)


def _strip_ansi(text: str) -> str:
    """删掉 ANSI 颜色码，方便比对纯文字。"""
    import re
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _make_john_first_alen_second():
    """模拟 Brief 第 6 页 Sample 的数据库状态：John 先注册（C 等级），Alen 后注册（P 等级）。"""
    john = Student(673358, "John Smith", "john.smith@university.com", "Helloworld123")
    # 4 门课，平均 68.25 → C
    john.enrol(Subject(1, 68))
    john.enrol(Subject(2, 68))
    john.enrol(Subject(3, 68))
    john.enrol(Subject(4, 69))
    alen = Student(762740, "Alen Jones", "alen.jones@university.com", "Helloworld123")
    # 4 门课，平均 63.50 → P
    alen.enrol(Subject(1, 63))
    alen.enrol(Subject(2, 64))
    alen.enrol(Subject(3, 63))
    alen.enrol(Subject(4, 64))
    return [john, alen]


class GroupByGradeOrderingTests(unittest.TestCase):
    """Brief 第 6 页关键 Sample：P 必须在 C 前输出，即使 C 学生先注册。"""

    def test_group_output_is_sorted_z_p_c_d_hd(self):
        db = _FakeDatabase(_make_john_first_alen_second())
        admin = AdminSystem(db)

        captured = io.StringIO()
        sys.stdout, real = captured, sys.stdout
        try:
            admin._group_by_grade()
        finally:
            sys.stdout = real

        text = _strip_ansi(captured.getvalue())
        # 关键断言：P 行必须在 C 行之前（按等级低→高排序）
        p_pos = text.find("P  --> [")
        c_pos = text.find("C  --> [")
        self.assertGreater(p_pos, 0, "P group should be present")
        self.assertGreater(c_pos, 0, "C group should be present")
        self.assertLess(p_pos, c_pos, "P group must appear before C group")

    def test_group_with_no_students_shows_nothing_to_display(self):
        db = _FakeDatabase([])
        admin = AdminSystem(db)

        captured = io.StringIO()
        sys.stdout, real = captured, sys.stdout
        try:
            admin._group_by_grade()
        finally:
            sys.stdout = real

        text = _strip_ansi(captured.getvalue())
        self.assertIn("< Nothing to Display >", text)


class PartitionTests(unittest.TestCase):
    """Brief 第 7 页：空 db 也要显示 FAIL --> [] / PASS --> []，不是 Nothing to Display。"""

    def test_partition_with_no_students_shows_two_empty_lists(self):
        db = _FakeDatabase([])
        admin = AdminSystem(db)

        captured = io.StringIO()
        sys.stdout, real = captured, sys.stdout
        try:
            admin._partition_pass_fail()
        finally:
            sys.stdout = real

        text = _strip_ansi(captured.getvalue())
        self.assertIn("FAIL --> []", text)
        self.assertIn("PASS --> []", text)
        # 不应该出现 Nothing to Display
        self.assertNotIn("< Nothing to Display >", text)

    def test_partition_fail_always_before_pass(self):
        db = _FakeDatabase(_make_john_first_alen_second())
        admin = AdminSystem(db)

        captured = io.StringIO()
        sys.stdout, real = captured, sys.stdout
        try:
            admin._partition_pass_fail()
        finally:
            sys.stdout = real

        text = _strip_ansi(captured.getvalue())
        fail_pos = text.find("FAIL --> [")
        pass_pos = text.find("PASS --> [")
        self.assertLess(fail_pos, pass_pos, "FAIL must be printed before PASS")


class ShowStudentsTests(unittest.TestCase):
    def test_empty_db_shows_nothing_to_display(self):
        db = _FakeDatabase([])
        admin = AdminSystem(db)

        captured = io.StringIO()
        sys.stdout, real = captured, sys.stdout
        try:
            admin._show_students()
        finally:
            sys.stdout = real

        text = _strip_ansi(captured.getvalue())
        self.assertIn("Student List", text)
        self.assertIn("< Nothing to Display >", text)

    def test_lists_students_in_db_order(self):
        db = _FakeDatabase(_make_john_first_alen_second())
        admin = AdminSystem(db)

        captured = io.StringIO()
        sys.stdout, real = captured, sys.stdout
        try:
            admin._show_students()
        finally:
            sys.stdout = real

        text = _strip_ansi(captured.getvalue())
        john_pos = text.find("John Smith")
        alen_pos = text.find("Alen Jones")
        self.assertLess(john_pos, alen_pos, "John (registered first) must appear first")


if __name__ == "__main__":
    unittest.main()
