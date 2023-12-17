from .prompt import Prompt
from .llms import OpenAI


def restore_diacritics(text, model=OpenAI()):
    prompt = Prompt("restore_diacritics.md", text=text)
    return model.generate(prompt)
