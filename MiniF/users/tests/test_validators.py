import unittest
from django.core.exceptions import ValidationError
from users.validators import UppercaseValidator


class UppercaseValidatorSimpleTests(unittest.TestCase):
    """tests for UppercaseValidator."""

    def setUp(self):
        """Create a fresh validator instance for each test."""
        self.validator = UppercaseValidator()

    def test_valid_password_passes(self):
        """Password with at least one ASCII uppercase letter should pass."""
        try:
            self.validator.validate("abcD123")
        except ValidationError as exc:  
            self.fail(f"ValidationError was not expected: {exc}")

    def test_help_text_is_non_empty_string(self):
        """get_help_text should return a non-empty string."""
        text = self.validator.get_help_text()
        self.assertIsInstance(text, str)
        self.assertTrue(text.strip())
