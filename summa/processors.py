from .prompt import Prompt


def restore_diacritics(input, model, prompt_template="restore_diacritics.md"):
    # Create a Prompt object with the specified text
    prompt = Prompt(prompt_template, input=input)

    # Generate the restored text using the specified model
    return model.generate(prompt)
