import os


class Prompt:
    def __init__(
        self, prompt_template, prompts_dir="prompts", **prompt_template_kwargs
    ):
        # Store the prompt template name
        self.prompt_template = prompt_template

        # Get the directory of the current file
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the prompt template file
        self.prompt_template_path = os.path.join(
            module_dir, prompts_dir, prompt_template
        )

        # Read the contents of the prompt template file
        with open(self.prompt_template_path, "r") as file:
            self.prompt_template_text = file.read()

        self.prompt_template_kwargs = prompt_template_kwargs

        # Format the prompt template with the provided keyword arguments
        self.prompt = self.prompt_template_text.format(**self.prompt_template_kwargs)

    def __str__(self):
        return self.prompt
