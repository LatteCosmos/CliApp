"""
cli/admin_system.py
=====================
Admin System：管理员子系统的 c/g/p/r/s/x 菜单。

【对应 Marking Criteria — The Admin System (15 marks)】
- Show students (1):                       _show_students()
- Group students (2):                      _group_by_grade()
- Partition students (2):                  _partition_pass_fail()
- Remove a student (2):                    _remove_student()
- Clear file (2):                          _clear_database()
- Read/Write to file (3): 全部走 IDatabase
- Error Handling (2): 空 db、id 非数字、二次确认拒绝 全有处理
- Matching I/O (1): wording 和 indent 一致

【Sample I/O 关键格式】
- 菜单项缩进 8 个空格
- "< Nothing to Display >" 缩进是 16 个空格（嵌套缩进）
- 按 grade 分组：每行 "P  --> [Alen Jones :: 762740 --> GRADE:  P - MARK: 63.50]"
  注意 grade 是左对齐 2 字符宽（{:<2}），所以 P 后面有一个空格再加 " --> "
- 分组顺序：按 grade 等级从低到高排序（Z → P → C → D → HD），
  和 Brief 第 6 页 Sample I/O 一致（P 在 C 前面）
"""

from __future__ import annotations

from typing import Dict, List

from data.i_database import IDatabase
from model.student import Student
from model.subject import Subject
from util import color


INDENT = "        "          # 8 空格：菜单和大部分输出
NESTED_INDENT = INDENT * 2   # 16 空格：用于 "< Nothing to Display >"


class AdminSystem:
    """管理员子系统。"""

    def __init__(self, database: IDatabase):
        self._db = database

    # =====================================================================
    #  主循环
    # =====================================================================
    def run(self) -> None:
        while True:
            choice = input(
                INDENT + color.cyan("Admin System (c/g/p/r/s/x): ")
            ).strip().lower()

            if choice == "c":
                self._clear_database()
            elif choice == "g":
                self._group_by_grade()
            elif choice == "p":
                self._partition_pass_fail()
            elif choice == "r":
                self._remove_student()
            elif choice == "s":
                self._show_students()
            elif choice == "x":
                return

    # =====================================================================
    #  (s) 显示所有学生
    # =====================================================================
    def _show_students(self) -> None:
        """
        Sample I/O（有学生时）：
            Admin System (c/g/p/r/s/x): s
            Student List
            John Smith :: 673358 --> Email: john.smith@university.com

        Sample I/O（数据库被清空后）：
            Admin System (c/g/p/r/s/x): s
            Student List
                    < Nothing to Display >
        """
        print(INDENT + color.yellow("Student List"))
        students = self._db.load()
        if not students:
            # 注意是嵌套缩进（16 空格）—— 和 sample 一致
            print(NESTED_INDENT + "< Nothing to Display >")
            return
        for s in students:
            # list_line() 已经把格式封装好了
            print(INDENT + s.list_line())

    # =====================================================================
    #  (g) 按等级分组
    # =====================================================================
    def _group_by_grade(self) -> None:
        """
        Sample I/O（Brief 第 6 页）：
            Admin System (c/g/p/r/s/x): g
            Grade Grouping
            P  --> [Alen Jones :: 762740 --> GRADE:  P - MARK: 63.50]
            C  --> [John Smith :: 673358 --> GRADE:  C - MARK: 68.25]

        【输出顺序的关键】
        Sample 中 John 先注册（已存在）, Alen 后注册。但 group 输出
        是 P 先 C 后。这说明 grade group 的输出顺序是按【等级从低到高】
        而不是按数据库插入顺序。等级顺序：Z (<50) → P (50-64) → C (65-74)
        → D (75-84) → HD (≥85)。

        组内学生的顺序仍然按数据库插入顺序（先注册的先出现在组里）。

        没数据时显示 "< Nothing to Display >"（16 空格嵌套缩进）。
        """
        print(INDENT + color.yellow("Grade Grouping"))

        students = self._db.load()
        if not students:
            print(NESTED_INDENT + "< Nothing to Display >")
            return

        # 按 grade 分组——dict 保持插入顺序，组内自动按数据库顺序
        groups: Dict[str, List[Student]] = {}
        for s in students:
            grade = s.overall_grade()
            groups.setdefault(grade, []).append(s)

        # 按等级从低到高排序输出（Z → P → C → D → HD）。
        # 用 Subject 类常量字符串作为权威定义，未来改 grade 名称只改一处。
        GRADE_ORDER = [
            Subject.GRADE_Z,
            Subject.GRADE_P,
            Subject.GRADE_C,
            Subject.GRADE_D,
            Subject.GRADE_HD,
        ]
        for grade in GRADE_ORDER:
            if grade not in groups:
                continue   # 没人在这个等级 → 跳过这一行
            members = groups[grade]
            inner = ", ".join(m.grade_line() for m in members)
            # {grade:<2} 让 P 变成 "P "（占 2 字符），HD 本身就是 2 字符
            print(INDENT + f"{grade:<2} --> [{inner}]")

    # =====================================================================
    #  (p) 划分及格 / 不及格
    # =====================================================================
    def _partition_pass_fail(self) -> None:
        """
        Sample I/O：
            Admin System (c/g/p/r/s/x): p
            PASS/FAIL Partition
            FAIL --> []
            PASS --> [John Smith :: 673358 --> GRADE:  C - MARK: 68.25, Alen Jones :: 762740 --> GRADE:  P - MARK: 63.50]

        及格规则（Brief 第 3 节）：average mark >= 50 -> PASS，否则 FAIL。
        没有学生时仍然显示 FAIL --> [] 和 PASS --> [] 两行（这是 sample 的格式）。
        """
        print(INDENT + color.yellow("PASS/FAIL Partition"))
        students = self._db.load()

        # 用列表推导式把学生分到两个桶
        # 没选课的学生平均分是 0 -> 算 FAIL（这是合理的默认行为）
        passes = [s for s in students if s.is_passing()]
        fails = [s for s in students if not s.is_passing()]

        pass_inner = ", ".join(s.grade_line() for s in passes)
        fail_inner = ", ".join(s.grade_line() for s in fails)
        # Sample 格式：FAIL 在前，PASS 在后
        print(INDENT + f"FAIL --> [{fail_inner}]")
        print(INDENT + f"PASS --> [{pass_inner}]")

    # =====================================================================
    #  (r) 删除单个学生
    # =====================================================================
    def _remove_student(self) -> None:
        """
        Sample I/O：
            Admin System (c/g/p/r/s/x): r
            Remove by ID: 762740
            Removing Student 762740 Account

        如果 ID 不存在：
            Admin System (c/g/p/r/s/x): r
            Remove by ID: 777888
            Student 777888 does not exist
        """
        raw = input(INDENT + "Remove by ID: ").strip()

        # 异常处理：用户输入非数字时给一个友好的红字提示，不要让程序崩溃
        try:
            student_id = int(raw)
        except ValueError:
            print(INDENT + color.red("Student ID must be a number"))
            return

        if self._db.delete_student(student_id):
            print(INDENT + color.yellow(f"Removing Student {student_id} Account"))
        else:
            print(INDENT + color.red(f"Student {student_id} does not exist"))

    # =====================================================================
    #  (c) 清空数据库
    # =====================================================================
    def _clear_database(self) -> None:
        """
        Sample I/O：
            Admin System (c/g/p/r/s/x): c
            Clearing students database
            Are you sure you want to clear the database (Y)ES/(N)O: Y
            Students data cleared

        如果选 N：什么都不做，直接回菜单。
        """
        print(INDENT + color.yellow("Clearing students database"))
        confirm = input(
            INDENT
            + color.red("Are you sure you want to clear the database (Y)ES/(N)O: ")
        ).strip().upper()

        if confirm == "Y":
            self._db.clear()
            print(INDENT + color.yellow("Students data cleared"))
        # 选 N 或者别的：不做任何事，直接回菜单——这就是"二次确认"的安全网
