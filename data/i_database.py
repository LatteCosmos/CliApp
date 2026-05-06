"""
data/i_database.py
====================
数据库接口（Interface）。

【为什么要有"接口"这一层？】
老师对 Part 1 的反馈："data handling and system logic are not clearly abstracted"。
这一层就是直接回应这条意见。

Python 没有 Java 那样的 interface 关键字，但用 abc.ABC + @abstractmethod 一样能实现
"只定义合同、不写实现"的抽象接口。

【DIP（依赖倒置原则）】
高层模块（StudentService、AdminSystem）只依赖 IDatabase 这个抽象，
不直接依赖具体的 Database 类。这样：
  1. 测试时可以塞一个内存版的 FakeDatabase（见 tests/test_student_service.py），
     测试根本不会碰真实的 students.data 文件，又快又干净；
  2. 以后想换成 SQLite、JSON、远程 API 都不用改业务代码，只换实现。
"""

from abc import ABC, abstractmethod
from typing import List

from model.student import Student


class IDatabase(ABC):
    """任何能保存/读取学生数据的"东西"都必须实现这些方法。"""

    @abstractmethod
    def load(self) -> List[Student]:
        """读出所有已保存的学生。文件不存在或为空时返回空列表 []。"""

    @abstractmethod
    def save_students(self, student_list: List[Student]) -> None:
        """用 student_list 整体覆盖存储里的内容。"""

    @abstractmethod
    def delete_student(self, student_id: int) -> bool:
        """按 id 删除一个学生。返回 True 表示找到并删除了，False 表示没这人。"""

    @abstractmethod
    def clear(self) -> None:
        """清空全部数据。"""

    # 注意：下面这两个不带 @abstractmethod，所以它们是【可选的】辅助方法。
    # 子类可以重写，但不重写也不会报错（默认会抛 NotImplementedError，由子类处理）。

    def find_by_email(self, email: str) -> Student:
        """按邮箱找学生，找不到返回 None。"""
        raise NotImplementedError

    def find_by_id(self, student_id: int) -> Student:
        """按 id 找学生，找不到返回 None。"""
        raise NotImplementedError

    def update_student(self, student: Student) -> None:
        """更新（或追加）一个学生。"""
        raise NotImplementedError
