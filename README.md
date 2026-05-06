# CLIUniApp – University Self-Enrolment System

A self-enrolment system for a local university, providing two
interactive subsystems (one for students, one for admins) plus a
Tk-based GUI version for registered students.

---

## Project Structure

```
CLIUniApp/
├── README.md                      Project overview and run instructions
├── main.py                        CLI entry point
├── gui_main.py                    GUI entry point
├── students.data                  Persistent student store (auto-created)
│
├── app/                           Top-level application classes
│   ├── uni_app.py                 Abstract UniApp superclass
│   ├── cli_uni_app.py             CLIUniApp implementation
│   └── gui_uni_app.py             GUIUniApp implementation
│
├── cli/                           Console subsystems
│   ├── student_system.py          Student login / register menu
│   ├── subject_enrolment_system.py Course menu (c/e/r/s/x)
│   └── admin_system.py            Admin menu (c/g/p/r/s/x)
│
├── data/                          Persistence layer
│   ├── i_database.py              IDatabase interface (DIP)
│   └── database.py                File-backed implementation
│
├── gui/                           Tkinter windows
│   ├── login_window.py            Main window – login form
│   ├── enrolment_window.py        Post-login enrolment view
│   ├── subject_window.py          Read-only subject listing
│   └── exception_window.py        Error pop-ups
│
├── model/                         Domain objects
│   ├── user.py                    Abstract User superclass
│   ├── student.py                 Student (extends User)
│   ├── admin.py                   Admin (extends User)
│   └── subject.py                 Subject value object
│
├── service/                       Business logic
│   └── student_service.py         Validation, ID generation, registration
│
├── util/                          Cross-cutting helpers
│   ├── color.py                   ANSI colour codes for the CLI
│   └── validator.py               Email and password regex helpers
│
└── tests/                         unittest test suite
    ├── test_validator.py
    ├── test_database.py
    └── test_student_service.py
```

---

## Requirements

* Python 3.10 or newer.
* The `tkinter` module is required for the GUI. It ships with Python on
  Windows and macOS. On Ubuntu/Debian Linux, install it with:

    ```bash
    sudo apt-get install python3-tk
    ```

No third-party libraries are required.

---

## Running the Programs

From the project root:

```bash
# Command-line application
python main.py

# Graphical application
python gui_main.py
```

The first time either program writes student data, it creates a file
called `students.data` in the project root. Both `main.py` and
`gui_main.py` read from and write to the same file, so a student
registered through the CLI can sign in to the GUI.

---

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

The suite covers the validator, the file-backed database (using
temporary files so the real `students.data` is never touched) and the
service layer.

---

## Design Highlights

* **Single Responsibility** – the `Student` model only stores data;
  validation, ID generation, and registration logic all live in
  `StudentService`.
* **Open/Closed** – `UniApp` is an abstract superclass shared by
  `CLIUniApp` and `GUIUniApp`. Adding a new front end means adding a
  new subclass, not editing the existing ones.
* **Dependency Inversion** – the application depends on `IDatabase`
  (an abstract base class), not on the concrete file-backed
  `Database`. Tests can substitute an in-memory fake without changing
  any production code.
* **Composition over inheritance** – a `Student` *contains* up to
  four `Subject` objects. Removing a `Student` removes the subjects
  with it.

---

## Sample I/O Compliance

All wording, indentation, and colours used by the CLI match the
sample I/O in the assessment brief:

* Sub-menu prompts use eight spaces of indentation.
* Menu prompts are cyan; status messages are yellow; errors are red.
* Subject lines render as `[ Subject::097 -- mark = 85 -- grade = HD ]`
  with the grade right-aligned in a two-character field.
* Admin grade and pass/fail outputs use Python-style list literals as
  shown in the sample.
