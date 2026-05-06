"""
The Admin System – (c)lear / (g)roup / (p)artition / (r)emove /
(s)how / e(x)it.

Admins are not authenticated; they pick this branch from the
University System menu and are taken straight here, as required by
the brief.

Output formatting for grade grouping and PASS/FAIL partitioning is
fiddly because the sample uses Python-style list literals
(``[John Smith :: 673358 --> ... , Alen Jones :: ...]``).  The
``Student.grade_line()`` helper produces one entry; we join with
``", "`` to assemble the inner part.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from data.i_database import IDatabase
from model.student import Student
from model.subject import Subject
from util import color


INDENT = "        "
NESTED_INDENT = INDENT + INDENT  # used for "< Nothing to Display >"

# Order in which the grades are listed when no real students fall into
# a category.  Not strictly required by the sample, but makes the
# output deterministic.
_GRADE_ORDER = [Subject.GRADE_HD, Subject.GRADE_D, Subject.GRADE_C, Subject.GRADE_P, Subject.GRADE_Z]


class AdminSystem:
    """Drives the admin command loop."""

    def __init__(self, database: IDatabase):
        self._db = database

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        while True:
            choice = input(INDENT + color.cyan("Admin System (c/g/p/r/s/x): ")).strip().lower()
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

    # ------------------------------------------------------------------
    # (s) Show all students
    # ------------------------------------------------------------------
    def _show_students(self) -> None:
        print(INDENT + color.yellow("Student List"))
        students = self._db.load()
        if not students:
            print(NESTED_INDENT + "< Nothing to Display >")
            return
        for s in students:
            print(INDENT + s.list_line())

    # ------------------------------------------------------------------
    # (g) Group students by grade
    # ------------------------------------------------------------------
    def _group_by_grade(self) -> None:
        print(INDENT + color.yellow("Grade Grouping"))
        students = [s for s in self._db.load() if s.subjects]
        if not students:
            print(NESTED_INDENT + "< Nothing to Display >")
            return

        groups: Dict[str, List[Student]] = defaultdict(list)
        for s in students:
            groups[s.overall_grade()].append(s)

        # Print one line per non-empty group, matching the sample
        # ordering by iterating from HD down to Z.
        for grade in _GRADE_ORDER:
            if grade not in groups:
                continue
            joined = ", ".join(s.grade_line() for s in groups[grade])
            print(INDENT + f"{grade:<2} --> [{joined}]")

    # ------------------------------------------------------------------
    # (p) Partition pass / fail
    # ------------------------------------------------------------------
    def _partition_pass_fail(self) -> None:
        print(INDENT + color.yellow("PASS/FAIL Partition"))
        students = self._db.load()

        # Students with no subjects don't really have a meaningful
        # average; the sample shows them excluded from both sides.
        eligible = [s for s in students if s.subjects]
        fails = [s for s in eligible if not s.is_passing()]
        passes = [s for s in eligible if s.is_passing()]

        fail_inner = ", ".join(s.grade_line() for s in fails)
        pass_inner = ", ".join(s.grade_line() for s in passes)
        print(INDENT + f"FAIL --> [{fail_inner}]")
        print(INDENT + f"PASS --> [{pass_inner}]")

    # ------------------------------------------------------------------
    # (r) Remove a single student
    # ------------------------------------------------------------------
    def _remove_student(self) -> None:
        raw = input(INDENT + "Remove by ID: ").strip()
        # Strip any leading zeros and validate it is numeric.
        try:
            student_id = int(raw)
        except ValueError:
            return

        if self._db.delete_student(student_id):
            print(INDENT + color.yellow(f"Removing Student {student_id} Account"))
        else:
            print(INDENT + color.red(f"Student {student_id} does not exist"))

    # ------------------------------------------------------------------
    # (c) Clear the database
    # ------------------------------------------------------------------
    def _clear_database(self) -> None:
        print(INDENT + color.yellow("Clearing students database"))
        confirm = input(
            INDENT + color.red("Are you sure you want to clear the database (Y)ES/(N)O: ")
        ).strip().upper()
        if confirm == "Y":
            self._db.clear()
            print(INDENT + color.yellow("Students data cleared"))
