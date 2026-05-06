"""
Unit tests for util.validator.

Each rule from the brief gets at least one positive and one negative
case.  The "Hello123 should fail" case is included explicitly because
the sample I/O depends on the password length being interpreted as
"5 letters AFTER the leading capital".
"""

import unittest

from util import validator


class EmailValidationTests(unittest.TestCase):
    def test_accepts_firstname_lastname_format(self):
        self.assertTrue(validator.is_valid_email("john.smith@university.com"))
        self.assertTrue(validator.is_valid_email("alen.jones@university.com"))

    def test_rejects_missing_dot(self):
        self.assertFalse(validator.is_valid_email("johnsmith@university.com"))

    def test_rejects_missing_domain_suffix(self):
        self.assertFalse(validator.is_valid_email("john.smith@university"))

    def test_rejects_uppercase_local_part(self):
        # The brief shows only lowercase usage; matching that strictly
        # protects us from "John.Smith@university.com" sneaking through.
        self.assertFalse(validator.is_valid_email("John.Smith@university.com"))

    def test_rejects_none_or_empty(self):
        self.assertFalse(validator.is_valid_email(None))
        self.assertFalse(validator.is_valid_email(""))


class PasswordValidationTests(unittest.TestCase):
    def test_accepts_helloworld123(self):
        self.assertTrue(validator.is_valid_password("Helloworld123"))

    def test_accepts_newworld123(self):
        self.assertTrue(validator.is_valid_password("Newworld123"))

    def test_rejects_short_password_from_sample(self):
        # Sample I/O explicitly rejects "Hello123" – our regex must
        # refuse it too.
        self.assertFalse(validator.is_valid_password("Hello123"))

    def test_rejects_lowercase_first(self):
        self.assertFalse(validator.is_valid_password("helloworld123"))

    def test_rejects_too_few_digits(self):
        self.assertFalse(validator.is_valid_password("Helloworld12"))

    def test_rejects_letters_after_digits(self):
        self.assertFalse(validator.is_valid_password("Helloworld123abc"))


class CombinedHelperTests(unittest.TestCase):
    def test_credentials_acceptable_requires_both(self):
        good_email = "john.smith@university.com"
        good_password = "Helloworld123"
        self.assertTrue(validator.credentials_acceptable(good_email, good_password))
        self.assertFalse(validator.credentials_acceptable(good_email, "bad"))
        self.assertFalse(validator.credentials_acceptable("bad", good_password))


if __name__ == "__main__":
    unittest.main()
