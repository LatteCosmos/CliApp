"""
cli/subject_enrolment_system.py
=================================
Subject Enrolment System：学生登录后的"课程菜单"，对应 c/e/r/s/x。

【对应 Marking Criteria — The Subject Enrolment System (15 marks)】
- Enroll (2): 最多选 4 门                            -> _enrol_subject()
- Tracking (2): 选课进度跟踪（"X out of 4 subjects"）  -> _enrol_subject() 和 _remove_subject()
- Remove a subject (2): 按 id 删除                    -> _remove_subject()
- Show subjects (1): 列出所有已选课                   -> _show_subjects()
- Change password (2): 修改登录密码                   -> _change_password()
- Read/Write to file (3): 任何修改都写回 students.data -> 每个动作都调 service.persist()
- Error Handling (2): 边界情况和异常都处理            -> 满 4 门、密码不匹配、id 非数字 等
- Matching I/O (1): wording 和 indent 一致            -> "Droping" 拼写故意保留以匹配 sample
"""

from __future__ import annotations

from model.student import Student
from service.student_service import StudentService
from util import color
from util import validator

# 8 空格缩进，和 Student System 保持一致
INDENT = "        "


class SubjectEnrolmentSystem:
    """学生登录后的课程菜单循环。"""

    def __init__(self, service: StudentService, student: Student):
        self._service = service
        self._student = student

    # =====================================================================
    #  主循环
    # =====================================================================
    def run(self) -> None:
        while True:
            choice = input(
                INDENT + color.cyan("Student Course Menu (c/e/r/s/x): ")
            ).strip().lower()

            if choice == "c":
                self._change_password()
            elif choice == "e":
                self._enrol_subject()
            elif choice == "r":
                self._remove_subject()
            elif choice == "s":
                self._show_subjects()
            elif choice == "x":
                # 退出前最后保存一次，确保所有内存修改都落到了文件
                self._service.persist(self._student)
                return
            # 其它输入：sample 中没有错误提示，静默忽略

    # =====================================================================
    #  (c) 修改密码
    # =====================================================================
    def _change_password(self) -> None:
        """
        Sample I/O：
            Student Course Menu (c/e/r/s/x): c
            Updating Password
            New Password: Helloworld123
            Confirm Password: Helloworld123

        如果两次输入不一致，只重新提示 Confirm Password（不重新提示 New Password）。
        """
        print(INDENT + color.yellow("Updating Password"))
        new_password = input(INDENT + "New Password: ")

        # 死循环让用户重输 Confirm 直到匹配——对应 Error Handling
        while True:
            confirm = input(INDENT + "Confirm Password: ")
            if confirm == new_password:
                break
            print(INDENT + color.red("Password does not match - try again"))

        # 改进点：新密码也要符合规则，否则给出明确提示而不是静默成功
        # （之前版本悄悄不更新会让用户以为成功了，扣 Error Handling 分）
        if not validator.is_valid_password(new_password):
            print(INDENT + color.red("Incorrect password format - password not updated"))
            return

        # 通过校验，更新模型 + 写文件
        self._student.change_password(new_password)
        self._service.persist(self._student)

    # =====================================================================
    #  (e) 选课
    # =====================================================================
    def _enrol_subject(self) -> None:
        """
        Sample I/O：
            Student Course Menu (c/e/r/s/x): e
            Enrolling in Subject-541
            You are now enrolled in 1 out of 4 subjects

        超过 4 门时显示红色错误：
            Students are allowed to enrol in 4 subjects only
        """
        # 先检查是否已满 4 门——对应 "Error Handling" 和 "Enroll max 4"
        if self._student.is_enrolment_full():
            print(INDENT + color.red("Students are allowed to enrol in 4 subjects only"))
            return

        # 让 service 造一门带 id 和分数的课，再挂到学生身上
        subject = self._service.create_subject_for(self._student)
        self._student.enrol(subject)
        # 立刻持久化——对应 Read/Write to file (3 marks)
        self._service.persist(self._student)

        # Sample 用 subject.id 的整数（不补零）显示："Subject-541"、"Subject-97"
        print(INDENT + color.yellow(f"Enrolling in Subject-{subject.id}"))

        # 显示进度——对应 "Tracking" (2 marks)
        count = len(self._student.subjects)
        print(
            INDENT
            + f"You are now enrolled in {count} out of {Student.MAX_SUBJECTS} subjects"
        )

    # =====================================================================
    #  (r) 退课
    # =====================================================================
    def _remove_subject(self) -> None:
        """
        Sample I/O：
            Student Course Menu (c/e/r/s/x): r
            Remove Subject by ID: 541
            Droping Subject-541
            You are now enrolled in 3 out of 4 subjects

        注意 sample 故意拼错了 "Droping"（应该是 Dropping），但为了
        "Matching I/O" 这一项，我们也用同样的拼写。
        """
        raw = input(INDENT + "Remove Subject by ID: ").strip()

        # 把字符串转成整数。失败说明用户输了非数字——对应 Error Handling
        try:
            subject_id = int(raw)
        except ValueError:
            print(INDENT + color.red("Subject ID must be a number"))
            return

        # 检查这门课确实存在
        if self._student.find_subject(subject_id) is None:
            print(INDENT + color.red(f"Subject-{subject_id} not found in enrolment"))
            return

        # 真正删除并立即持久化
        self._student.remove_subject(subject_id)
        self._service.persist(self._student)

        # 注意 sample 用 "Droping"（少一个 p）—— 故意保留以匹配 I/O
        print(INDENT + color.yellow(f"Droping Subject-{subject_id}"))
        count = len(self._student.subjects)
        print(
            INDENT
            + f"You are now enrolled in {count} out of {Student.MAX_SUBJECTS} subjects"
        )

    # =====================================================================
    #  (s) 显示已选科目
    # =====================================================================
    def _show_subjects(self) -> None:
        """
        Sample I/O：
            Student Course Menu (c/e/r/s/x): s
            Showing 0 subjects

        或者：
            Student Course Menu (c/e/r/s/x): s
            Showing 2 subjects
            [ Subject::541 -- mark = 55 -- grade =  P ]
            [ Subject::455 -- mark = 57 -- grade =  P ]
        """
        count = len(self._student.subjects)
        print(INDENT + f"Showing {count} subjects")
        # repr(subject) 调用的是 Subject.__repr__()，已经把格式化做好了
        for subject in self._student.subjects:
            print(INDENT + repr(subject))