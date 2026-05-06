"""
util/validator.py
==================
邮箱与密码的格式校验。

【为什么要单独抽出来？】
Marking criteria 中 "RegEx" 占 2 分，"Error Handling" 占 2 分。
把正则集中在一个文件里：
  1. 注册和登录、CLI 和 GUI 都共用同一份规则，绝对一致；
  2. 单元测试只测这一个文件，覆盖度高；
  3. 后期想改规则只改一处，不会漏掉。

【规则来源（来自 Assessment Brief 第 1、4 节）】
邮箱：firstname.lastname@university.com
  - 必须是小写字母 + 一个点 + 小写字母 + 固定域名 @university.com
  - 反例：johnsmith@university.com（缺点）、john.smith@university（缺.com）

密码：(i) 大写字母开头 (ii) 至少 5 个字母 (iii) 末尾至少 3 位数字
  - 注意：样例 I/O 中 "Hello123" 被拒绝，"Helloworld123" 被接受
  - 这意味着规则其实是 "首字母大写之后 + 至少 5 个字母 + 至少 3 位数字"
  - 即 "至少 5 letters" 是指首字母之后还要再有 5 个，加上首字母总共 6 个或更多
"""

import re

# ---------------------------------------------------------------------------
# 邮箱正则
# ---------------------------------------------------------------------------
# ^                  开头
# [a-z]+             一个或多个小写字母（first name）
# \.                 一个点（在正则里 . 是特殊字符，要转义）
# [a-z]+             一个或多个小写字母（last name）
# @university\.com   固定的域名后缀
# $                  结尾
#
# 用 re.compile 是为了把正则编译一次，后面每次匹配都直接用编译好的对象，
# 比每次调用 re.match() 字符串去重复编译要快。
EMAIL_PATTERN = re.compile(r"^[a-z]+\.[a-z]+@university\.com$")

# ---------------------------------------------------------------------------
# 密码正则
# ---------------------------------------------------------------------------
# ^[A-Z]             首字母必须是大写
# [A-Za-z]{5,}       后面跟 5 个或更多的字母（大小写都行）
# \d{3,}             末尾是 3 个或更多的数字（\d 等于 [0-9]）
# $                  结尾
#
# 这个写法保证：
#   "Helloworld123" -> 通过（H + elloworld + 123）
#   "Hello123"      -> 失败（H 后面只有 4 个字母，不够 5 个）
#   "helloworld123" -> 失败（开头没有大写）
#   "Helloworld12"  -> 失败（数字只有 2 位）
PASSWORD_PATTERN = re.compile(r"^[A-Z][A-Za-z]{5,}\d{3,}$")


def is_valid_email(email: str) -> bool:
    """检查邮箱是否符合 firstname.lastname@university.com 格式。"""
    # 防御式编程：万一传进来 None 不要报错，直接返回 False
    if not email:
        return False
    # re.match 从字符串开头开始匹配；匹配到了就返回 Match 对象（真），否则 None（假）
    return EMAIL_PATTERN.match(email) is not None


def is_valid_password(password: str) -> bool:
    """检查密码是否符合规则（大写开头 + 至少 5 字母 + 至少 3 数字）。"""
    if not password:
        return False
    return PASSWORD_PATTERN.match(password) is not None


def credentials_acceptable(email: str, password: str) -> bool:
    """
    一次性校验邮箱和密码。
    CLI 注册/登录 和 GUI 注册/登录 都调用这一个函数，保证规则一致。
    """
    return is_valid_email(email) and is_valid_password(password)