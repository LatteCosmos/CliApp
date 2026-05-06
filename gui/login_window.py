"""
LoginWindow – the main window of GUIUniApp.

The brief makes the login window the entry point and only allows
already-registered students to proceed.  Empty fields, malformed
credentials and unknown students all surface through ExceptionWindow.

On success we hide the login window, push the student into
EnrolmentWindow, and re-show the login window when they close it –
that way one process can be used by several students one after
another.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui.enrolment_window import EnrolmentWindow
from gui.exception_window import ExceptionWindow
from service.student_service import StudentService


class LoginWindow(tk.Tk):
    """Root window of the GUI application."""

    def __init__(self, service: StudentService):
        super().__init__()
        self._service = service

        self.title("GUIUniApp – Login")
        self.geometry("360x240")
        self.resizable(False, False)
        # The tk frame uses a slightly larger padding to feel less
        # cramped than a stock dialog.
        self.configure(padx=28, pady=24)

        # ---- Title ----------------------------------------------------
        ttk.Label(
            self,
            text="University Login",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(pady=(0, 4))
        ttk.Label(
            self,
            text="Use your registered email and password.",
            foreground="#555",
        ).pack(pady=(0, 18))

        # ---- Form -----------------------------------------------------
        form = ttk.Frame(self)
        form.pack(fill="x")

        ttk.Label(form, text="Email").grid(row=0, column=0, sticky="w", pady=4)
        self._email_entry = ttk.Entry(form, width=28)
        self._email_entry.grid(row=0, column=1, padx=(10, 0))

        ttk.Label(form, text="Password").grid(row=1, column=0, sticky="w", pady=4)
        self._password_entry = ttk.Entry(form, width=28, show="*")
        self._password_entry.grid(row=1, column=1, padx=(10, 0))

        # ---- Action button -------------------------------------------
        ttk.Button(self, text="Login", command=self._handle_login).pack(pady=(20, 0))

        # Pressing Enter on either field also submits.
        self.bind("<Return>", lambda _e: self._handle_login())

        # Focus the email box for convenience.
        self._email_entry.focus_set()

    # ------------------------------------------------------------------
    # Login workflow
    # ------------------------------------------------------------------
    def _handle_login(self) -> None:
        email = self._email_entry.get().strip()
        password = self._password_entry.get()

        # 1) Empty-field check – the brief calls this out explicitly.
        if not email or not password:
            ExceptionWindow(self, "Email and password cannot be empty.",
                            title="Missing fields")
            return

        # 2) Format validation against the same regex used by the CLI.
        if not self._service.credentials_acceptable(email, password):
            ExceptionWindow(self, "Incorrect email or password format.",
                            title="Invalid format")
            return

        # 3) Authenticate against students.data.
        student = self._service.authenticate(email, password)
        if student is None:
            ExceptionWindow(self, "Student does not exist or credentials don't match.",
                            title="Login failed")
            return

        # On success, hide ourselves, clear the fields, and open the
        # enrolment window.  When the student closes that window the
        # login window comes back via the on_close callback.
        self._password_entry.delete(0, tk.END)
        self.withdraw()
        EnrolmentWindow(self, self._service, student)
