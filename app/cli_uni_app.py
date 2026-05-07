"""
app/cli_uni_app.py
====================
命令行版本的应用入口（CLIUniApp）。

【对应 Marking Criteria】
- "University System" (4 marks): Student/Admin 子菜单跳转、可来回切换、Thank You 退出
- "Matching I/O" (1 mark of 4): wording 和 indent 必须和 sample 一致

【Sample I/O 样例】
    University System: (A)dmin, (S)tudent, or X : A
            Admin System (c/g/p/r/s/x): x
    University System: (A)dmin, (S)tudent, or X : S
            Student System (l/r/x): x
    University System: (A)dmin, (S)tudent, or X : X
    Thank You
"""

from __future__ import annotations
from typing import Optional

from app.uni_app import UniApp
from cli.admin_system import AdminSystem
from cli.student_system import StudentSystem
from data.database import Database
from util import color


class CLIUniApp(UniApp):
    """命令行版本的 UniApp。"""

    def __init__(self, database: Optional[Database] = None):
        # database 参数允许测试时塞别的实现进来；正常使用时不传，自动用 Database()
        super().__init__(database or Database())

    def show_main_menu(self) -> None:
        """
        在 CLI 里"显示主菜单"等同于打印一次提示文字。
        实际的循环在 run() 里——每次循环都会重新打印这个提示。
        """
        # 这个抽象方法实现成 pass（什么都不做）只是为了满足 UniApp 的契约——
        # 实际的菜单显示融在了 run() 的 input() 提示里。
        pass

    def run(self) -> None:
        """
        主循环：反复显示 University System 菜单，根据用户输入分支到子系统或退出。
        """
        while True:
            # 提示符的内容、颜色、末尾 ": " 都和 sample I/O 一字不差
            choice = input(
                color.cyan("University System: (A)dmin, (S)tudent, or X : ")
            ).strip().upper()

            if choice == "A":
                # 用 AdminSystem 处理后续；返回时回到这个循环（即"可在菜单间切换"）
                AdminSystem(self.database).run()
            elif choice == "S":
                # StudentSystem 需要 service（注册/登录都要调 service）
                StudentSystem(self.service).run()
            elif choice == "X":
                # Thank You 用黄色——和 sample I/O 一致
                print(color.yellow("Thank You"))
                return
            # 其它输入：sample 没有显示错误提示，所以我们也静默忽略，
            # 直接让循环再来一次
