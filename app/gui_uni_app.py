"""
GUIUniApp – the Tk-based flavour of UniApp.

Concrete subclass that wires the LoginWindow to the shared
StudentService / Database pair from UniApp.  The brief specifies that
GUIUniApp uses students.data the same way CLIUniApp does, so pointing
both at the default Database() makes them interchangeable.
"""

from __future__ import annotations

from app.uni_app import UniApp
from data.database import Database
from gui.login_window import LoginWindow


class GUIUniApp(UniApp):
    """Concrete GUI flavour of the application."""

    def __init__(self, database: Database | None = None):
        super().__init__(database or Database())
        self._root: LoginWindow | None = None

    def show_main_menu(self) -> None:
        # In the GUI the "main menu" *is* the login window, so
        # constructing it is the show step.
        self._root = LoginWindow(self.service)

    def run(self) -> None:
        if self._root is None:
            self.show_main_menu()
        # mypy/runtime safety: at this point _root is definitely set.
        assert self._root is not None
        self._root.mainloop()
