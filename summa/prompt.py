import os


class Prompt:
    def __init__(self, prompt_template, prompts_dir="prompts", **kwargs):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(module_dir, prompts_dir, prompt_template)

        with open(prompt_path, "r") as file:
            prompt_template = file.read()

        self.prompt = prompt_template.format(**kwargs)

    def __str__(self):
        return self.prompt
