"""
tests/test_validator.py
========================
util/validator.py 的单元测试。

【对应 SLO 5】"Apply appropriate testing techniques to ensure the quality
of the software system"

每条规则都至少有一个"通过"和一个"拒绝"用例，覆盖：
- 邮箱格式：合法、缺点、缺 .com、首字母大写
- 密码：太短、缺数字、首字母小写、结尾有字母
- 联合校验：组合不通过的情形
"""

import unittest

from util import validator


class EmailValidationTests(unittest.TestCase):
    """测试 is_valid_email。"""

    def test_accepts_firstname_lastname_format(self):
        # Sample I/O 中的两个真实例子
        self.assertTrue(validator.is_valid_email("john.smith@university.com"))
        self.assertTrue(validator.is_valid_email("alen.jones@university.com"))

    def test_rejects_missing_dot(self):
        # 缺中间的点 -> 不符合 firstname.lastname 模式
        self.assertFalse(validator.is_valid_email("johnsmith@university.com"))

    def test_rejects_missing_domain_suffix(self):
        # Brief 第 1 节明确说："firstname.lastname@university 是不合法的"
        self.assertFalse(validator.is_valid_email("john.smith@university"))

    def test_rejects_uppercase_local_part(self):
        # Sample 中所有邮箱都是小写，所以严格匹配小写
        self.assertFalse(validator.is_valid_email("John.Smith@university.com"))

    def test_rejects_none_or_empty(self):
        # 防御式：None 和空串都应拒绝，不能崩溃
        self.assertFalse(validator.is_valid_email(None))
        self.assertFalse(validator.is_valid_email(""))


class PasswordValidationTests(unittest.TestCase):
    """测试 is_valid_password。"""

    def test_accepts_helloworld123(self):
        # Sample I/O 中接受的密码
        self.assertTrue(validator.is_valid_password("Helloworld123"))

    def test_accepts_newworld123(self):
        # Sample 修改密码场景中用的
        self.assertTrue(validator.is_valid_password("Newworld123"))

    def test_rejects_short_password_from_sample(self):
        # Sample I/O 明确拒绝 "Hello123" —— 字母不够 5 个
        self.assertFalse(validator.is_valid_password("Hello123"))

    def test_rejects_lowercase_first(self):
        # 首字母必须大写
        self.assertFalse(validator.is_valid_password("helloworld123"))

    def test_rejects_too_few_digits(self):
        # 数字至少 3 个
        self.assertFalse(validator.is_valid_password("Helloworld12"))

    def test_rejects_letters_after_digits(self):
        # 数字必须在末尾，后面不能再有字母
        self.assertFalse(validator.is_valid_password("Helloworld123abc"))


class CombinedHelperTests(unittest.TestCase):
    """测试 credentials_acceptable 同时校验邮箱和密码。"""

    def test_both_good(self):
        self.assertTrue(
            validator.credentials_acceptable("john.smith@university.com", "Helloworld123")
        )

    def test_email_bad(self):
        self.assertFalse(validator.credentials_acceptable("bad", "Helloworld123"))

    def test_password_bad(self):
        self.assertFalse(
            validator.credentials_acceptable("john.smith@university.com", "bad")
        )


if __name__ == "__main__":
    unittest.main()
