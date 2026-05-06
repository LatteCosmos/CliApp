"""
util/color.py
==============
ANSI 终端颜色码工具。

【为什么需要颜色？】
Sample I/O 中不同消息用不同颜色（青色菜单提示、绿色子菜单标题、黄色状态、红色错误）。
"Matching I/O" 这一项要求 wording 和 indentation 都对得上，颜色虽然不强制，
但加上颜色能让 Showcase 看起来更专业，也方便老师肉眼区分各种消息。

【ANSI 转义码工作原理】
\\033 是 ESC 字符（八进制 33 = 十进制 27）。
\\033[36m 是"切换到青色"，\\033[0m 是"恢复默认"。
终端看到这些字符不会显示出来，而是改变后面文字的颜色。

【为什么不直接 print 颜色？】
封装成函数后，调用方写 color.cyan("hello")，比每次都写
print("\\033[36m" + "hello" + "\\033[0m") 简洁得多。
"""

# 复位序列：所有颜色函数末尾都用它"关掉"颜色，避免后续输出被染色
RESET = "\033[0m"

# 前景色（4 个 ANSI 标准色）
CYAN = "\033[36m"      # 菜单提示
GREEN = "\033[32m"     # 子菜单标题（"Student Sign In" 等）
YELLOW = "\033[33m"    # 状态/动作消息（"Updating Password" 等）
RED = "\033[31m"       # 错误信息


def cyan(text: str) -> str:
    """把 text 包成青色，用于交互式菜单提示。"""
    return f"{CYAN}{text}{RESET}"


def green(text: str) -> str:
    """绿色，用于 'Student Sign In' / 'Student Sign Up' 这类标题。"""
    return f"{GREEN}{text}{RESET}"


def yellow(text: str) -> str:
    """黄色，用于状态消息和接受提示。"""
    return f"{YELLOW}{text}{RESET}"


def red(text: str) -> str:
    """红色，用于错误和危险操作的二次确认提示。"""
    return f"{RED}{text}{RESET}"
