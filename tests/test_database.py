"""
tests/test_database.py
========================
data/database.py 的单元测试。

【关键设计】
每个测试都用 tempfile 创建独立的临时文件，setUp 创建、tearDown 清掉。
这样无论运行多少次测试，真正的 students.data 都不会被动到。

测试覆盖：
- 文件不存在时 load() 返回 []
- 写入 → 读取 的 round-trip 是否一致
- Subject 列表是否在 pickle 之后保持完整
- clear() 把文件清空
- delete_student() 找到/找不到的两种情形
- find_by_email() 命中/未命中
"""

import os
import tempfile
import unittest

from data.database import Database
from model.student import Student
from model.subject import Subject


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        # tempfile.mkstemp 给我们一个独一无二的文件路径
        # 我们立刻删掉文件本身（保留路径），让 Database 自己创建——
        # 这样能顺便测试"文件不存在时自动创建"的行为
        fd, self._path = tempfile.mkstemp(suffix=".data")
        os.close(fd)
        os.remove(self._path)
        self._db = Database(self._path)

    def tearDown(self):
        # 测试完清理临时文件
        if os.path.exists(self._path):
            os.remove(self._path)

    # =====================================================================
    #  基本读写
    # =====================================================================
    def test_load_returns_empty_list_when_file_is_fresh(self):
        """新文件应该被当作"没数据"，返回空列表而不是报错。"""
        self.assertEqual([], self._db.load())

    def test_save_then_load_roundtrips_one_student(self):
        """写一个学生进去，再读出来，关键字段应该完全一致。"""
        student = Student(123, "Test User", "test.user@university.com", "Helloworld123")
        self._db.save_students([student])

        loaded = self._db.load()
        self.assertEqual(1, len(loaded))
        self.assertEqual("test.user@university.com", loaded[0].email)
        self.assertEqual("Test User", loaded[0].name)

    def test_save_preserves_subject_list(self):
        """学生的 subjects 列表也得能完整地 round-trip。"""
        student = Student(7, "Sub Owner", "sub.owner@university.com", "Helloworld123")
        student.enrol(Subject(101, 90))
        student.enrol(Subject(202, 40))
        self._db.save_students([student])

        loaded = self._db.load()[0]
        self.assertEqual(2, len(loaded.subjects))
        self.assertEqual({101, 202}, {s.id for s in loaded.subjects})

    # =====================================================================
    #  删除 / 清空
    # =====================================================================
    def test_clear_empties_the_file(self):
        s = Student(1, "Doomed Student", "doomed.student@university.com", "Helloworld123")
        self._db.save_students([s])
        self._db.clear()
        self.assertEqual([], self._db.load())

    def test_delete_student_removes_only_match(self):
        """删除应该只影响 id 匹配的那一条，其他保留不变。"""
        a = Student(1, "Alice User", "alice.user@university.com", "Helloworld123")
        b = Student(2, "Bob Smith", "bob.smith@university.com", "Helloworld123")
        self._db.save_students([a, b])

        self.assertTrue(self._db.delete_student(1))
        remaining = self._db.load()
        self.assertEqual([2], [s.id for s in remaining])

    def test_delete_student_returns_false_when_missing(self):
        """ID 不存在时返回 False，不抛异常。"""
        self.assertFalse(self._db.delete_student(999))

    # =====================================================================
    #  辅助查询
    # =====================================================================
    def test_find_by_email_returns_match(self):
        s = Student(5, "Found Me", "found.me@university.com", "Helloworld123")
        self._db.save_students([s])
        self.assertIsNotNone(self._db.find_by_email("found.me@university.com"))
        self.assertIsNone(self._db.find_by_email("nope@university.com"))

    def test_update_student_replaces_existing(self):
        """更新一个已存在的学生，应该替换而不是新增。"""
        s = Student(8, "Original", "original@university.com", "Helloworld123")
        self._db.save_students([s])

        # 改个名字再 update
        s_updated = Student(8, "Renamed", "original@university.com", "Helloworld123")
        self._db.update_student(s_updated)

        # 应该还是只有一条记录，但名字已经变了
        loaded = self._db.load()
        self.assertEqual(1, len(loaded))
        self.assertEqual("Renamed", loaded[0].name)

    def test_update_student_appends_when_not_found(self):
        """要更新的学生不在文件里时，应该当作"新增"。"""
        s = Student(9, "New", "new.guy@university.com", "Helloworld123")
        self._db.update_student(s)
        loaded = self._db.load()
        self.assertEqual(1, len(loaded))


if __name__ == "__main__":
    unittest.main()
