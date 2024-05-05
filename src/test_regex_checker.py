import unittest
from regex_checker import check_content_and_extract


class RegexCheckerTests(unittest.TestCase):
    def test_pattern_found(self):
        result = check_content_and_extract("Hello, world!", r"Hello")
        self.assertEqual(result, (True, "Hello"))

    def test_pattern_not_found(self):
        result = check_content_and_extract("Hello, world!", r"Goodbye")
        self.assertEqual(result, (False, None))

    def test_pattern_is_none(self):
        result = check_content_and_extract("Hello, world!", None)
        self.assertEqual(result, (True, None))

    def test_content_is_empty(self):
        result = check_content_and_extract("", r"Hello")
        self.assertEqual(result, (False, None))

    def test_both_content_and_pattern_are_empty(self):
        result = check_content_and_extract("", "")
        self.assertEqual(result, (True, ""))


if __name__ == '__main__':
    unittest.main()
