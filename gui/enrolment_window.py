"""
EnrolmentWindow – the post-login view in GUIUniApp.

The brief requires it to:
    * let a logged-in student enrol in up to four (4) subjects
    * show each newly enrolled subject in their list
    * raise an exception when the student tries to add a fifth

We bundle the enrolment list, an "Enrol" button and a "Show subjects"
button on the same frame, then delegate the per-subject list to
SubjectWindow when requested.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui.exception_window import ExceptionWindow
from gui.subject_window import SubjectWindow
from model.student import Student
from service.student_service import StudentService


class EnrolmentWindow(tk.Toplevel):
    """Window the student lands on after a successful login."""

    def __init__(self, parent: tk.Misc, service: StudentService, student: Student):
        super().__init__(parent)
        self._service = service
        self._student = student

        self.title(f"Enrolment – {student.name}")
        self.resizable(False, False)
        self.configure(padx=22, pady=22)

        # Closing this window from the system controls should also
        # bring the login window back so the student can sign out.
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._parent = parent

        # ---- Header ----------------------------------------------------
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(
            header,
            text=f"Welcome, {student.name}",
            font=("TkDefaultFont", 13, "bold"),
        ).pack(anchor="w")
        ttk.Label(header, text=f"Student ID: {student.display_id()}",
                  foreground="#555").pack(anchor="w")

        # ---- Enrolment list -------------------------------------------
        list_frame = ttk.LabelFrame(self, text="Your Subjects", padding=10)
        list_frame.pack(fill="both", expand=True)

        columns = ("subject", "mark", "grade")
        self._tree = ttk.Treeview(list_frame, columns=columns,
                                  show="headings", height=4)
        self._tree.heading("subject", text="Subject")
        self._tree.heading("mark", text="Mark")
        self._tree.heading("grade", text="Grade")
        self._tree.column("subject", width=130, anchor="center")
        self._tree.column("mark", width=80, anchor="center")
        self._tree.column("grade", width=80, anchor="center")
        self._tree.pack(fill="both", expand=True)
        self._refresh_tree()

        # ---- Action bar -----------------------------------------------
        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(12, 0))

        self._counter = ttk.Label(
            actions,
            text=self._counter_text(),
        )
        self._counter.pack(side="left")

        ttk.Button(actions, text="Show Subjects",
                   command=self._open_subject_window).pack(side="right", padx=(6, 0))
        self._enrol_btn = ttk.Button(actions, text="Enrol", command=self._enrol)
        self._enrol_btn.pack(side="right")

        self._update_button_state()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _enrol(self) -> None:
        if self._student.is_enrolment_full():
            ExceptionWindow(
                self,
                "Students are allowed to enrol in 4 subjects only.",
                title="Enrolment limit reached",
            )
            return

        subject = self._service.create_subject_for(self._student)
        self._student.enrol(subject)
        self._service.persist(self._student)
        self._refresh_tree()
        self._counter.config(text=self._counter_text())
        self._update_button_state()

    def _open_subject_window(self) -> None:
        SubjectWindow(self, self._student)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _refresh_tree(self) -> None:
        # Wipe and re-fill so we never get out of sync.
        for child in self._tree.get_children():
            self._tree.delete(child)
        for s in self._student.subjects:
            self._tree.insert(
                "", "end",
                values=(f"Subject::{s.display_id()}", s.mark, s.grade),
            )

    def _counter_text(self) -> str:
        return (
            f"Enrolled in {len(self._student.subjects)} "
            f"out of {Student.MAX_SUBJECTS} subjects"
        )

    def _update_button_state(self) -> None:
        if self._student.is_enrolment_full():
            self._enrol_btn.state(["disabled"])
        else:
            self._enrol_btn.state(["!disabled"])

    def _on_close(self) -> None:
        # Bring the login window back when the enrolment view is closed.
        self.destroy()
        try:
            self._parent.deiconify()
        except tk.TclError:
            # Parent already gone (e.g. app shutting down) – ignore.
            pass
