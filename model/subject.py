"""
model/subject.py
=================
科目（Subject）领域对象。

【职责（Single Responsibility）】
Subject 只负责存放一门课的数据：id、mark、grade。
它【不】生成 id，【不】生成随机分数，那些是 StudentService 的事。
分离职责让 Subject 可以被单独测试，也方便老师改卷时看出"模型只装数据"的设计。

【数据来源 / 规则（Brief 第 3 节）】
- id: 1..999 的随机 3 位数
- mark: 25..100 的随机整数
- grade: 由 mark 推算
    mark < 50  -> Z
    50..64     -> P
    65..74     -> C
    75..84     -> D
    >= 85      -> HD
"""

from __future__ import annotations  # 让类型注解里的 "Subject" 不需要先定义就能用


class Subject:
    """一门已选的科目。"""

    # -----------------------------------------------------------------------
    # 等级常量
    # -----------------------------------------------------------------------
    # 写成类常量而不是字符串字面量，可以：
    #   1. 单元测试里能 import 这些常量做断言；
    #   2. 任何拼写错误（例如打成 "HC"）会立刻在 import 时报错；
    #   3. IDE 能做自动补全。
    GRADE_HD = "HD"
    GRADE_D = "D"
    GRADE_C = "C"
    GRADE_P = "P"
    GRADE_Z = "Z"

    def __init__(self, subject_id: int, mark: int):
        # 单下划线前缀 _xxx 在 Python 中表示"protected"——告诉别人"请不要直接改这个"。
        # 类外仍然能访问，但配合下面的 @property 提供只读视图。
        self._id = subject_id
        self._mark = mark
        # 等级可以由 mark 直接推出来，所以构造时一次算好存起来即可
        self._grade = Subject._calculate_grade(mark)

    # -----------------------------------------------------------------------
    # @property 让 obj.id 看起来像属性，但其实背后是一个 getter 方法。
    # 这样既保护了 _id（外部不能 obj._id = 新值），又给出了简洁的访问语法。
    # -----------------------------------------------------------------------
    @property
    def id(self) -> int:
        return self._id

    @property
    def mark(self) -> int:
        return self._mark

    @property
    def grade(self) -> str:
        return self._grade

    # -----------------------------------------------------------------------
    # 私有辅助方法：根据分数算等级
    # -----------------------------------------------------------------------
    @staticmethod
    def _calculate_grade(mark: int) -> str:
        """
        按 UTS 评分制把分数映射到等级。
        @staticmethod 表示这个方法不依赖 self，从分数到等级是纯函数关系。
        """
        # 注意判断顺序：必须从高到低，因为命中第一个就 return
        if mark >= 85:
            return Subject.GRADE_HD
        if mark >= 75:
            return Subject.GRADE_D
        if mark >= 65:
            return Subject.GRADE_C
        if mark >= 50:
            return Subject.GRADE_P
        return Subject.GRADE_Z

    # -----------------------------------------------------------------------
    # 显示辅助
    # -----------------------------------------------------------------------
    def display_id(self) -> str:
        """
        把 id 格式化成 3 位数字（不足前面补 0）。
        例如 id=97 -> "097"，id=541 -> "541"。
        Sample I/O 中 "[ Subject::097 -- ... ]" 就是用这个格式。
        """
        # f-string 里 {x:03d} 表示"3 位的十进制整数，前面用 0 填充"
        return f"{self._id:03d}"

    def __repr__(self) -> str:
        """
        当 print(subject) 或 repr(subject) 时调用这个方法。

        【Sample I/O 实际格式（Brief 第 5 页）】
            [ Subject::541 -- mark = 55 -- grade =   P ]   ← `=` 与 P 之间 3 个空格
            [ Subject::097 -- mark = 85 -- grade =  HD ]   ← `=` 与 HD 之间 2 个空格

        【为什么是 {:>3} 不是 {:>2}】
        字面量 "= " 自带 1 个尾随空格。再用右对齐 3 字符宽:
            P  -> "  P"  (前面补 2 空格) → 拼出来 "=   P"  (3 空格)
            HD -> " HD"  (前面补 1 空格) → 拼出来 "=  HD"  (2 空格)
        这样 P/HD 在视觉上的 `]` 收尾右对齐到同一列，且匹配 Sample 字面输出。
        """
        return (
            f"[ Subject::{self.display_id()} "
            f"-- mark = {self._mark} "
            f"-- grade = {self._grade:>3} ]"
        )
