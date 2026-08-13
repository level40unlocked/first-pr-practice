import unittest

from greet import greet


class GreetTests(unittest.TestCase):
    def test_greet_returns_expected_message(self):
        self.assertEqual(greet("World"), "Hello, World!")

    def test_greet_raises_on_empty_name(self):
        with self.assertRaises(ValueError):
            greet("")


if __name__ == "__main__":
    unittest.main()
