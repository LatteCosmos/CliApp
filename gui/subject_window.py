"""
SubjectWindow – read-only listing of the student's currently enrolled
subjects, including marks and grades.

Implemented as a Toplevel dialog so it can pop up alongside the
enrolment window when the user clicks a "Show subjects" button.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from model.student import Student


class SubjectWindow(tk.Toplevel):
    """Modal listing of every subject the student has enrolled in."""

    def __init__(self, parent: tk.Misc, student: Student):
        super().__init__(parent)
        self.title("Enrolled Subjects")
        self.resizable(False, False)
        self.configure(padx=18, pady=18)
        self.transient(parent)
        self.grab_set()

        # Header summarising how many subjects are listed.
        count = len(student.subjects)
        ttk.Label(
            self,
            text=f"Showing {count} subjects",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        # Use a Treeview rather than a pile of labels so the columns
        # line up neatly even with HD/D/C/P/Z mixed in.
        columns = ("subject", "mark", "grade")
        tree = ttk.Treeview(self, columns=columns, show="headings", height=max(count, 1))
        tree.heading("subject", text="Subject")
        tree.heading("mark", text="Mark")
        tree.heading("grade", text="Grade")
        tree.column("subject", width=110, anchor="center")
        tree.column("mark", width=80, anchor="center")
        tree.column("grade", width=80, anchor="center")

        for s in student.subjects:
            tree.insert("", "end", values=(f"Subject::{s.display_id()}", s.mark, s.grade))

        if count == 0:
            tree.insert("", "end", values=("(no subjects yet)", "", ""))

        tree.pack(fill="both", expand=True)
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=(12, 0))
