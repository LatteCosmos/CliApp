"""
tests/test_student_service.py
===============================
StudentService 的业务逻辑单元测试。

【关键设计：FakeDatabase】
我们没用真实的 Database 类，而是写了一个内存版的假数据库（FakeDatabase）。
原因：
1. 测试速度快——纯内存，没磁盘 IO
2. 测试干净——不会污染真正的 students.data
3. 演示 DIP（依赖倒置）—— StudentService 只认 IDatabase 接口，
   生产代码塞 Database()，测试代码塞 FakeDatabase()，service 完全感受不到

【测试覆盖】
- ID 生成在合法范围内（学生 1..999999、科目 1..999）
- 随机分数在 25..100 之间
- 注册流程能持久化
- 邮箱重复检测
- 登录认证：邮箱不存在、密码错、全对 三种路径
- 等级边界值（49->Z, 50->P, 64->P, 65->C, ...）
- 不能选第 5 门课
- 平均分和及格判断
- 退课
"""

import unittest
from typing import List

from data.i_database import IDatabase
from model.student import Student
from model.subject import Subject
from service.student_service import StudentService


class _FakeDatabase(IDatabase):
    """实现 IDatabase 合同的内存版假数据库——专给 service 测试用。"""

    def __init__(self):
        self._students: List[Student] = []

    def load(self):
        # 返回一份 list 拷贝——避免外部代码意外修改内部状态
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
    """测试 ID 和分数的随机生成。"""

    def setUp(self):
        self.db = _FakeDatabase()
        self.service = StudentService(self.db)

    def test_generated_student_id_is_in_range(self):
        # 跑 20 次，每次都应该落在 1..999999
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
    """测试注册和登录流程。"""

    def setUp(self):
        self.db = _FakeDatabase()
        self.service = StudentService(self.db)

    def test_register_persists_student(self):
        student = self.service.register(
            "John Smith", "john.smith@university.com", "Helloworld123"
        )
        # 注册后数据库里应该有 1 条
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
        self.assertIsNone(
            self.service.authenticate("john.smith@university.com", "Helloworld999")
        )

    def test_authenticate_rejects_unknown_email(self):
        self.assertIsNone(self.service.authenticate("ghost@university.com", "Helloworld123"))


class GradeAndEnrolmentTests(unittest.TestCase):
    """测试分数等级映射和选课限制。"""

    def test_grade_boundaries(self):
        """逐个边界值确认等级映射正确。"""
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
        """第 5 门必须选不上。"""
        student = Student(1, "Limit Tester", "limit.tester@university.com", "Helloworld123")
        for i in range(4):
            self.assertTrue(student.enrol(Subject(i + 1, 60)))
        # 第 5 次必须返回 False
        self.assertFalse(student.enrol(Subject(5, 60)))
        self.assertEqual(4, len(student.subjects))

    def test_average_mark_and_pass(self):
        """平均分计算 + 及格判断。"""
        student = Student(1, "Pass Tester", "pass.tester@university.com", "Helloworld123")
        student.enrol(Subject(1, 60))
        student.enrol(Subject(2, 70))
        student.enrol(Subject(3, 50))
        student.enrol(Subject(4, 80))
        # 平均 = (60+70+50+80)/4 = 65 -> grade C, 及格
        self.assertAlmostEqual(65.0, student.average_mark())
        self.assertTrue(student.is_passing())
        self.assertEqual("C", student.overall_grade())

    def test_student_with_no_subjects_is_failing(self):
        """没选课的学生平均 0 分 -> FAIL（不能算 PASS）。"""
        s = Student(1, "Empty", "empty.cup@university.com", "Helloworld123")
        self.assertFalse(s.is_passing())
        self.assertEqual(0.0, s.average_mark())

    def test_remove_subject(self):
        """退课要确实减少计数；删不存在的返回 False。"""
        student = Student(1, "Remove Tester", "remove.tester@university.com", "Helloworld123")
        student.enrol(Subject(101, 60))
        student.enrol(Subject(102, 70))
        self.assertTrue(student.remove_subject(101))
        self.assertEqual(1, len(student.subjects))
        # 退一门不存在的——应该返回 False，不能崩溃
        self.assertFalse(student.remove_subject(999))


class PasswordChangeTests(unittest.TestCase):
    """测试密码修改后能正确登录。"""

    def setUp(self):
        self.db = _FakeDatabase()
        self.service = StudentService(self.db)

    def test_change_password_then_login(self):
        student = self.service.register(
            "John Smith", "john.smith@university.com", "Helloworld123"
        )
        # 改密码
        student.change_password("Newworld456")
        self.service.persist(student)

        # 用旧密码不该登得进去
        self.assertIsNone(
            self.service.authenticate("john.smith@university.com", "Helloworld123")
        )
        # 用新密码可以
        self.assertIsNotNone(
            self.service.authenticate("john.smith@university.com", "Newworld456")
        )


if __name__ == "__main__":
    unittest.main()
