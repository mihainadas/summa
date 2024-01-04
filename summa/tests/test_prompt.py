import unittest
from summa.llms import Prompt, PromptTemplate


class TestPrompt(unittest.TestCase):
    def setUp(self):
        # Create an instance of the Prompt class with the specified arguments
        self.prompt_template = PromptTemplate(
            template_filename="test_prompt.md", prompts_dir="tests/prompts"
        )

    def test_render_no_kwargs(self):
        # Check if the string representation of the prompt is correct
        self.assertEqual(self.prompt_template.render("Test"), "Hello, Test!")


if __name__ == "__main__":
    # Run the unit tests
    unittest.main()
