# CLIUniApp – University Self-Enrolment System

A self-enrolment system for a local university, built for **32555 Fundamentals
of Software Development, Assessment 1 – Part 2**. Provides a CLI subsystem
for students and admins, plus a Tkinter-based GUI subsystem for registered
students.

---

## Marking-criteria coverage map

| Rubric item | Where it lives in the code |
|-------------|---------------------------|
| **a. The University System (4)** – student/admin/browse/IO | `app/cli_uni_app.py` `run()` |
| **b. The Student System (9)** – register/login/regex/error/IO | `cli/student_system.py`, `service/student_service.py`, `util/validator.py` |
| **c. The Subject Enrolment System (15)** – enrol/track/remove/show/change-pwd/file/error/IO | `cli/subject_enrolment_system.py`, `service/student_service.py`, `data/database.py` |
| **d. The Admin System (15)** – list/group/partition/remove/clear/file/error/IO | `cli/admin_system.py`, `data/database.py` |
| **e. GUIUniApp (7)** – login/enrolment/subject/exception window | `gui/login_window.py`, `gui/enrolment_window.py`, `gui/subject_window.py`, `gui/exception_window.py` |

---

## Project Structure

```
CLIUniApp/
├── README.md                           Project overview and run instructions
├── main.py                             CLI entry point
├── gui_main.py                         GUI entry point
├── students.data                       Persistent student store (auto-created)
│
├── app/                                Top-level application classes
│   ├── uni_app.py                      Abstract UniApp superclass
│   ├── cli_uni_app.py                  CLIUniApp implementation
│   └── gui_uni_app.py                  GUIUniApp implementation
│
├── cli/                                Console subsystems
│   ├── student_system.py               Student login / register menu
│   ├── subject_enrolment_system.py     Course menu (c/e/r/s/x)
│   └── admin_system.py                 Admin menu (c/g/p/r/s/x)
│
├── data/                               Persistence layer
│   ├── i_database.py                   IDatabase interface (DIP)
│   └── database.py                     File-backed implementation
│
├── gui/                                Tkinter windows
│   ├── login_window.py                 Main window – login form
│   ├── enrolment_window.py             Post-login enrolment view
│   ├── subject_window.py               Read-only subject listing
│   └── exception_window.py             Error pop-ups
│
├── model/                              Domain objects
│   ├── user.py                         Abstract User superclass
│   ├── student.py                      Student (extends User)
│   ├── admin.py                        Admin (extends User)
│   └── subject.py                      Subject value object
│
├── service/                            Business logic
│   └── student_service.py              Validation, ID generation, registration
│
├── util/                               Cross-cutting helpers
│   ├── color.py                        ANSI colour codes for the CLI
│   └── validator.py                    Email and password regex helpers
│
└── tests/                              unittest test suite (51 tests)
    ├── test_validator.py
    ├── test_database.py
    ├── test_student_service.py
    ├── test_student_model.py
    └── test_admin_system.py            ← Sample-I/O matching tests
```

---

## Requirements

* Python 3.10 or newer.
* `tkinter` is required for the GUI. Ships with Python on Windows / macOS.
  On Ubuntu/Debian Linux:

    ```bash
    sudo apt-get install python3-tk
    ```

No third-party libraries are required.

---

## Running the Programs

```bash
# Command-line application
python main.py

# Graphical application
python gui_main.py
```

Both `main.py` and `gui_main.py` read from and write to the same
`students.data` file in the project root, so a student registered through
the CLI can sign in to the GUI.

---

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

Expected: **51 tests, all OK** (43 original + 8 admin/group/partition I/O matching tests).

---

## Sample I/O Compliance

Every wording, indentation, and colour matches the assignment brief sample:

* Sub-menu prompts use **8-space** indentation; nested `< Nothing to Display >`
  uses **16 spaces**.
* Menu prompts are **cyan**; status messages **yellow**; errors and danger
  prompts **red**.
* `Subject` lines render as `[ Subject::097 -- mark = 85 -- grade =  HD ]`
  with the grade right-aligned in a **3-character field** (3 spaces before P,
  2 before HD).
* Grade groups (admin `g`) are emitted in **Z → P → C → D → HD** order, not
  insertion order.
* PASS/FAIL partition always prints both `FAIL --> [...]` then `PASS --> [...]`,
  even when one or both lists are empty.
* The drop-subject message intentionally preserves the brief's typo
  `"Droping Subject-X"`.

---

## Design Highlights (talking points for showcase)

* **Single Responsibility** – `Student` only stores data; validation, ID
  generation, and registration logic all live in `StudentService`.
* **Open/Closed** – `UniApp` is an abstract superclass shared by `CLIUniApp`
  and `GUIUniApp`. Adding a new front end means subclassing, not editing.
* **Dependency Inversion** – the application depends on `IDatabase` (an
  abstract base class), not on the concrete file-backed `Database`. Tests
  substitute an in-memory fake without changing any production code.
* **Composition over inheritance** – a `Student` *contains* up to four
  `Subject` objects. Removing a `Student` removes the subjects with it.
* **DRY** – `Student.overall_grade` calls `Subject._calculate_grade` so the
  grade thresholds live in exactly one place.

