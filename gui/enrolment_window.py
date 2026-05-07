"""
gui/enrolment_window.py
=========================
GUI 的"选课窗口"——4 个窗口之一。

【对应 Marking Criteria — Enrolment window (2 marks)】
"Enrolment window allows students to enrol in a maximum of four (4) subjects."

也涵盖：
- Exception window 的触发场景之一（点击 Enrol 时已经满 4 门）
- 调用 SubjectWindow（点击"Show Subjects"按钮）

【设计要点】
- 主窗口（LoginWindow）登录成功后弹出这个窗口
- 关闭这个窗口时把 LoginWindow 重新显示出来——这样可以"切换学生"而不用重启程序
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from gui.exception_window import ExceptionWindow
from gui.subject_window import SubjectWindow
from model.student import Student
from service.student_service import StudentService


class EnrolmentWindow(tk.Toplevel):
    """登录后的主操作窗口。"""

    def __init__(self, parent: tk.Misc, service: StudentService, student: Student):
        super().__init__(parent)
        self._service = service
        self._student = student
        self._parent = parent

        self.title(f"Enrolment – {student.name}")
        self.resizable(False, False)
        self.configure(padx=22, pady=22)

        # 用户点窗口右上角 X 关掉时也走我们自定义的回调（让 LoginWindow 显回来）
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ---------------------------------------------------------------
        # 顶部头部：欢迎语 + 学生 ID
        # ---------------------------------------------------------------
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(
            header,
            text=f"Welcome, {student.name}",
            font=("TkDefaultFont", 13, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            header,
            text=f"Student ID: {student.display_id()}",
            foreground="#555",
        ).pack(anchor="w")

        # ---------------------------------------------------------------
        # 中间：已选科目表格（直接嵌在窗口里，方便随时看）
        # ---------------------------------------------------------------
        list_frame = ttk.LabelFrame(self, text="Your Subjects", padding=10)
        list_frame.pack(fill="both", expand=True)

        columns = ("subject", "mark", "grade")
        self._tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=4
        )
        self._tree.heading("subject", text="Subject")
        self._tree.heading("mark", text="Mark")
        self._tree.heading("grade", text="Grade")
        self._tree.column("subject", width=130, anchor="center")
        self._tree.column("mark", width=80, anchor="center")
        self._tree.column("grade", width=80, anchor="center")
        self._tree.pack(fill="both", expand=True)
        self._refresh_tree()

        # ---------------------------------------------------------------
        # 底部：进度计数器 + 两个按钮
        # ---------------------------------------------------------------
        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(12, 0))

        self._counter = ttk.Label(actions, text=self._counter_text())
        self._counter.pack(side="left")

        ttk.Button(
            actions,
            text="Show Subjects",
            command=self._open_subject_window,
        ).pack(side="right", padx=(6, 0))

        self._enrol_btn = ttk.Button(actions, text="Enrol", command=self._enrol)
        self._enrol_btn.pack(side="right")

        # 已经满 4 门时按钮显示为灰色禁用——这是双保险，
        # 即使禁用没生效，_enrol() 里也会再检查一次并弹错误
        self._update_button_state()

    # =====================================================================
    #  动作
    # =====================================================================
    def _enrol(self) -> None:
        """点击 Enrol 按钮——选一门新课。"""
        # 防御式：再检查一次（即使按钮被禁用，键盘快捷键也可能触发）
        if self._student.is_enrolment_full():
            ExceptionWindow(
                self,
                "Students are allowed to enrol in 4 subjects only.",
                title="Enrolment limit reached",
            )
            return

        # 用 service 造一门新课，挂到学生上，写文件，刷 UI
        subject = self._service.create_subject_for(self._student)
        self._student.enrol(subject)
        self._service.persist(self._student)
        self._refresh_tree()
        self._counter.config(text=self._counter_text())
        self._update_button_state()

    def _open_subject_window(self) -> None:
        """打开只读的"已选科目"窗口。"""
        SubjectWindow(self, self._student)

    # =====================================================================
    #  辅助方法
    # =====================================================================
    def _refresh_tree(self) -> None:
        """清空表格再重新填——保证不会出现"幽灵旧数据"。"""
        for child in self._tree.get_children():
            self._tree.delete(child)
        for s in self._student.subjects:
            self._tree.insert(
                "",
                "end",
                values=(f"Subject::{s.display_id()}", s.mark, s.grade),
            )

    def _counter_text(self) -> str:
        """生成 "Enrolled in X out of 4 subjects" 这种文字。"""
        return (
            f"Enrolled in {len(self._student.subjects)} "
            f"out of {Student.MAX_SUBJECTS} subjects"
        )

    def _update_button_state(self) -> None:
        """已满 4 门时把 Enrol 按钮禁用。"""
        if self._student.is_enrolment_full():
            self._enrol_btn.state(["disabled"])
        else:
            self._enrol_btn.state(["!disabled"])

    def _on_close(self) -> None:
        """
        关闭这个窗口时执行的清理：销毁自己 + 让 LoginWindow 显回来。
        这样可以让一个 GUI 进程被多个学生轮流使用。
        """
        self.destroy()
        try:
            # 让父窗口（LoginWindow）从隐藏状态恢复
            self._parent.deiconify()
        except tk.TclError:
            # 父窗口已经被销毁（比如整个程序在退出）—— 安全地忽略
            pass
