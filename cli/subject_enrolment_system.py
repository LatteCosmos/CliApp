"""
The Subject Enrolment System ("Course Menu") that a student sees once
they log in.  It exposes the c/e/r/s/x options described in the brief:

    (c) change password
    (e) enrol in a subject
    (r) remove a subject by id
    (s) show all enrolled subjects
    (x) exit back to the student menu
"""

from __future__ import annotations

from getpass import getpass

from model.student import Student
from service.student_service import StudentService
from util import color
from util import validator


# All Course Menu output is indented eight spaces (one tab worth) to
# match the sample I/O.
INDENT = "        "


class SubjectEnrolmentSystem:
    """Drives the student's post-login interaction loop."""

    def __init__(self, service: StudentService, student: Student):
        self._service = service
        self._student = student

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
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
                # Persist any final state and return to the caller.
                self._service.persist(self._student)
                return
            # Anything else is silently ignored – matches the sample I/O.

    # ------------------------------------------------------------------
    # Individual menu actions
    # ------------------------------------------------------------------
    def _change_password(self) -> None:
        print(INDENT + color.yellow("Updating Password"))
        new_password = input(INDENT + "New Password: ")
        # The sample shows a re-prompt loop until the two values match.
        while True:
            confirm = input(INDENT + "Confirm Password: ")
            if confirm == new_password:
                break
            print(INDENT + color.red("Password does not match - try again"))

        # The brief does not require validating the new password against
        # the regex, but doing so is a small bit of polish for HD.  We
        # only persist the change when it passes, so the student is
        # never left with an unusable password.
        if validator.is_valid_password(new_password):
            self._student.change_password(new_password)
            self._service.persist(self._student)

    def _enrol_subject(self) -> None:
        if self._student.is_enrolment_full():
            print(INDENT + color.red("Students are allowed to enrol in 4 subjects only"))
            return

        subject = self._service.create_subject_for(self._student)
        self._student.enrol(subject)
        self._service.persist(self._student)

        # The sample uses the raw integer here (e.g. "Subject-97"),
        # not the zero-padded form.
        print(INDENT + color.yellow(f"Enrolling in Subject-{subject.id}"))
        count = len(self._student.subjects)
        print(
            INDENT
            + f"You are now enrolled in {count} out of {Student.MAX_SUBJECTS} subjects"
        )

    def _remove_subject(self) -> None:
        raw = input(INDENT + "Remove Subject by ID: ").strip()
        try:
            subject_id = int(raw)
        except ValueError:
            # Silently ignore – the brief doesn't show this case.
            return

        if self._student.find_subject(subject_id) is None:
            # Not in the sample but useful as defensive output.
            return

        self._student.remove_subject(subject_id)
        self._service.persist(self._student)
        print(INDENT + color.yellow(f"Droping Subject-{subject_id}"))
        count = len(self._student.subjects)
        print(
            INDENT
            + f"You are now enrolled in {count} out of {Student.MAX_SUBJECTS} subjects"
        )

    def _show_subjects(self) -> None:
        count = len(self._student.subjects)
        print(INDENT + f"Showing {count} subjects")
        for subject in self._student.subjects:
            print(INDENT + repr(subject))
