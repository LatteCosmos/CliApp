"""
ExceptionWindow – a small modal dialog used by the GUI to surface
errors back to the student.

The brief calls for an exception window for three cases:
    * empty login fields
    * invalid email/password format
    * an attempt to enrol in more than four subjects

We model that with a single reusable Toplevel-based dialog so the
GUIUniApp side can stay short and declarative.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ExceptionWindow(tk.Toplevel):
    """Modal pop-up that displays a single error string."""

    def __init__(self, parent: tk.Misc, message: str, title: str = "Error"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(padx=20, pady=20)

        # Make the window modal – the user has to dismiss it before
        # they can keep clicking around the underlying frame.
        self.transient(parent)
        self.grab_set()

        # Layout: an icon-style red prefix, the message, then OK.
        ttk.Label(self, text="\u26a0  " + message,
                  foreground="#b00020", wraplength=320,
                  font=("TkDefaultFont", 11)).pack(pady=(0, 12))
        ttk.Button(self, text="OK", command=self.destroy).pack()

        # Centre the dialog over its parent for a polished look.
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - self.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{px}+{py}")
