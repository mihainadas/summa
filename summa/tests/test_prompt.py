import unittest
from summa import prompt


class TestPrompt(unittest.TestCase):
    def setUp(self):
        # Create an instance of the Prompt class with the specified arguments
        self.prompt = prompt.Prompt(
            "test_prompt.md", prompts_dir="tests/prompts", name="Test"
        )

    def test_init(self):
        # Check if the prompt_template_kwargs attribute is set correctly
        self.assertEqual(self.prompt.prompt_template_kwargs, {"name": "Test"})
        # Check if the prompt contains the expected string
        self.assertIn("Hello, Test", self.prompt.prompt)

    def test_str(self):
        # Check if the string representation of the prompt is correct
        self.assertEqual(str(self.prompt), "Hello, Test!")


if __name__ == "__main__":
    # Run the unit tests
    unittest.main()
