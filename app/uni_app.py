"""
Abstract UniApp superclass.

UniApp captures what CLIUniApp and GUIUniApp have in common: a shared
StudentService and IDatabase, plus an entry point method ``run`` that
each subclass implements differently.

Modelling this with ``abc`` keeps the design diagram honest – we
literally cannot instantiate UniApp directly, only one of the two
subclasses.
"""

from abc import ABC, abstractmethod

from data.i_database import IDatabase
from service.student_service import StudentService


class UniApp(ABC):
    """Common base class for the CLI and GUI flavours of the application."""

    def __init__(self, database: IDatabase):
        # Both subclasses share the same database/service pair so they
        # see each other's writes.
        self._database = database
        self._service = StudentService(database)

    # Subclasses provide their own entry point.
    @abstractmethod
    def run(self) -> None:
        ...

    # Provided so the diagram's ``showMainMenu`` operation is still a
    # template method on the superclass.  Subclasses override.
    @abstractmethod
    def show_main_menu(self) -> None:
        ...

    # Convenience accessors so the subclasses don't need to reach into
    # private attributes.
    @property
    def database(self) -> IDatabase:
        return self._database

    @property
    def service(self) -> StudentService:
        return self._service
