"""
app/uni_app.py
================
UniApp 抽象基类。

【对应 Part 1 类图】
类图里画了 UniApp 是抽象类，CLIUniApp 和 GUIUniApp 都继承它。
这里就是把那张图变成代码。共享的部分（数据库引用、StudentService 实例）
放在父类里，子类只关心自己怎么"启动"。

【为什么要抽象？】
1. 强制 CLI 和 GUI 用同一个 IDatabase 和同一个 StudentService 的接口形态，
   两者注册的学生彼此看得见（CLI 注册的，GUI 也能登录）；
2. 任何写 UniApp(...) 直接实例化的代码会立刻报错——必须用具体子类。
"""

from abc import ABC, abstractmethod

from data.i_database import IDatabase
from service.student_service import StudentService


class UniApp(ABC):
    """CLI 和 GUI 共同的父类。"""

    def __init__(self, database: IDatabase):
        # 数据库和服务都"挂"在父类上，两个子类自动共享
        self._database = database
        self._service = StudentService(database)

    # ---------------------------------------------------------------
    # 子类必须提供自己的"启动"方法 —— 这就是模板方法模式
    # ---------------------------------------------------------------
    @abstractmethod
    def run(self) -> None:
        """启动应用。CLIUniApp 进入命令行循环，GUIUniApp 进入 mainloop。"""

    @abstractmethod
    def show_main_menu(self) -> None:
        """显示主菜单。CLI 是文字提示，GUI 是登录窗口。"""

    # ---------------------------------------------------------------
    # 公共属性——给子类访问 _database / _service 的简洁通道
    # ---------------------------------------------------------------
    @property
    def database(self) -> IDatabase:
        return self._database

    @property
    def service(self) -> StudentService:
        return self._service
