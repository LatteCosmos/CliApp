"""
The Student System – the (l)ogin / (r)egister / (x)exit menu that
shows up when the user picks 'S' from the University System menu.

Successful login pushes the user into the SubjectEnrolmentSystem
("Course Menu").  Successful registration just prints the acknowledgement
messages and returns to the prompt.
"""

from __future__ import annotations

from cli.subject_enrolment_system import SubjectEnrolmentSystem
from service.student_service import StudentService
from util import color


INDENT = "        "


class StudentSystem:
    """Login / register loop, anchored on a shared StudentService."""

    def __init__(self, service: StudentService):
        self._service = service

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        while True:
            choice = input(INDENT + color.cyan("Student System (l/r/x): ")).strip().lower()
            if choice == "l":
                self._login()
            elif choice == "r":
                self._register()
            elif choice == "x":
                return

    # ------------------------------------------------------------------
    # Sign-in
    # ------------------------------------------------------------------
    def _login(self) -> None:
        print(INDENT + color.green("Student Sign In"))

        # Loop until both values match the regex.  The sample shows the
        # error message printed inline after a failed attempt and then
        # the prompts redisplayed.
        while True:
            email = input(INDENT + "Email: ")
            password = input(INDENT + "Password: ")
            if self._service.credentials_acceptable(email, password):
                print(INDENT + color.yellow("email and password formats acceptable"))
                break
            print(INDENT + color.red("Incorrect email or password format"))

        student = self._service.authenticate(email, password)
        if student is None:
            print(INDENT + color.yellow("Student does not exist"))
            return

        # Hand control over to the Course Menu.
        SubjectEnrolmentSystem(self._service, student).run()

    # ------------------------------------------------------------------
    # Sign-up
    # ------------------------------------------------------------------
    def _register(self) -> None:
        print(INDENT + color.green("Student Sign Up"))

        while True:
            email = input(INDENT + "Email: ")
            password = input(INDENT + "Password: ")
            if self._service.credentials_acceptable(email, password):
                print(INDENT + color.yellow("email and password formats acceptable"))
                break
            print(INDENT + color.red("Incorrect email or password format"))

        # Derive the display name from the email address so the message
        # matches the sample ("Student John Smith already exists" /
        # "Enrolling Student Alen Jones").  The local part is always
        # firstname.lastname after the regex check above.
        local_part = email.split("@", 1)[0]
        first, last = local_part.split(".", 1)
        name = f"{first.capitalize()} {last.capitalize()}"

        if self._service.email_exists(email):
            print(INDENT + color.yellow(f"Student {name} already exists"))
            return

        # Echoing the name back to the user before we register matches
        # the sample's "Name: Alen Jones / Enrolling Student Alen Jones"
        # sequence.
        print(INDENT + f"Name: {name}")
        print(INDENT + color.yellow(f"Enrolling Student {name}"))
        self._service.register(name, email, password)
