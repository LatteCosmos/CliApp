"""
tests/test_student_model.py
==============================
Student 和 Subject 的显示格式测试。

显示格式直接关系到 "Matching I/O" 这个marking criteria，
所以专门写一组测试来锁住格式：subject id 必须是 3 位补 0、
student id 必须是 6 位补 0、grade_line() 输出必须和 sample 一致。
"""

import unittest

from model.student import Student
from model.subject import Subject


class SubjectDisplayTests(unittest.TestCase):
    def test_subject_id_padded_to_three_digits(self):
        # Sample I/O 中 "Subject::097" 就是用这种格式
        self.assertEqual("097", Subject(97, 50).display_id())
        self.assertEqual("541", Subject(541, 50).display_id())
        self.assertEqual("001", Subject(1, 50).display_id())

    def test_subject_repr_matches_sample(self):
        # Sample: [ Subject::541 -- mark = 55 -- grade =  P ]
        s = Subject(541, 55)
        self.assertEqual("[ Subject::541 -- mark = 55 -- grade =  P ]", repr(s))

        # HD 占 2 字符宽，前面没空格
        s2 = Subject(97, 85)
        self.assertEqual("[ Subject::097 -- mark = 85 -- grade = HD ]", repr(s2))


class StudentDisplayTests(unittest.TestCase):

    def _make_student(self):
        # John Smith :: id 673358, 选了 4 门凑出平均 68.25 分（来自 Sample I/O）
        s = Student(673358, "John Smith", "john.smith@university.com", "Helloworld123")
        # 凑出 68.25 平均分：68 + 68 + 68 + 69 = 273 / 4 = 68.25
        s.enrol(Subject(1, 68))
        s.enrol(Subject(2, 68))
        s.enrol(Subject(3, 68))
        s.enrol(Subject(4, 69))
        return s

    def test_student_id_padded_to_six_digits(self):
        # Brief 第 1 节："002340 是合法的，2345 不是"
        self.assertEqual("002340", Student(2340, "X Y", "x.y@university.com", "Aaaaaa111").display_id())
        self.assertEqual("999999", Student(999999, "X Y", "x.y@university.com", "Aaaaaa111").display_id())

    def test_list_line_format(self):
        # Sample: John Smith :: 673358 --> Email: john.smith@university.com
        s = self._make_student()
        self.assertEqual(
            "John Smith :: 673358 --> Email: john.smith@university.com",
            s.list_line(),
        )

    def test_grade_line_format(self):
        # Sample: John Smith :: 673358 --> GRADE:  C - MARK: 68.25
        # 注意 GRADE 后面有 2 个空格（一个来自 ":"+space, 一个来自 grade 右对齐补的）
        s = self._make_student()
        self.assertEqual(
            "John Smith :: 673358 --> GRADE:  C - MARK: 68.25",
            s.grade_line(),
        )

    def test_grade_line_format_hd_no_extra_space(self):
        # 当 grade 是 HD（已经 2 字符）时不再补空格
        s = Student(1, "Top Star", "top.star@university.com", "Helloworld123")
        s.enrol(Subject(1, 90))
        s.enrol(Subject(2, 90))
        s.enrol(Subject(3, 90))
        s.enrol(Subject(4, 90))
        self.assertEqual(
            "Top Star :: 000001 --> GRADE: HD - MARK: 90.00",
            s.grade_line(),
        )


if __name__ == "__main__":
    unittest.main()
