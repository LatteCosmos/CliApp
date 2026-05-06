"""
GUI entry point for GUIUniApp.

Run from the project root with::

    python gui_main.py

The Login window opens as the application's main window.  Successful
login pushes the student into the Enrolment window.  Closing the
Enrolment window brings the Login window back so a different student
can sign in without restarting the program.
"""

from app.gui_uni_app import GUIUniApp


def main() -> None:
    app = GUIUniApp()
    app.run()


if __name__ == "__main__":
    main()
