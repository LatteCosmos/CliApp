"""
CLI entry point for CLIUniApp.

Run from the project root with::

    python main.py

The students.data file will be created next to this script the first
time the program writes to it.
"""

from app.cli_uni_app import CLIUniApp


def main() -> None:
    app = CLIUniApp()
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        # Graceful exit when the user hits Ctrl+C or the input stream
        # ends mid-prompt.  Avoids the ugly stack trace.
        print()


if __name__ == "__main__":
    main()
