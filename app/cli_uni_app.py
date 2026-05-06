"""
CLIUniApp – the command-line entry point.

Shows the University System menu and routes the user into either the
admin or student subsystem.  Exiting the top menu prints the
"Thank You" closing message and returns control to the caller.
"""

from __future__ import annotations

from app.uni_app import UniApp
from cli.admin_system import AdminSystem
from cli.student_system import StudentSystem
from data.database import Database
from util import color


class CLIUniApp(UniApp):
    """Concrete CLI flavour of the application."""

    def __init__(self, database: Database | None = None):
        # Default to the file-based database but allow injection so the
        # tests can swap in a fake.
        super().__init__(database or Database())

    # ------------------------------------------------------------------
    # UniApp contract
    # ------------------------------------------------------------------
    def show_main_menu(self) -> None:
        # The main prompt has no leading indentation – only the
        # sub-systems do.  This is what produces the visual hierarchy
        # in the sample I/O.
        pass  # The main menu is rendered inside ``run``.

    def run(self) -> None:
        while True:
            choice = input(
                color.cyan("University System: (A)dmin, (S)tudent, or X : ")
            ).strip().upper()

            if choice == "A":
                AdminSystem(self.database).run()
            elif choice == "S":
                StudentSystem(self.service).run()
            elif choice == "X":
                print(color.yellow("Thank You"))
                return
            # Any other input loops back to the prompt – the brief does
            # not specify a "try again" message.
