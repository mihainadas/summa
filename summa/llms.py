import openai
from abc import ABC, abstractmethod
from decouple import config


class TextGeneration(ABC):
    @abstractmethod
    def generate(self, text):
        pass


class OpenAI(TextGeneration):
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))
        self.model = model

    def generate(self, prompt):
        return (
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": str(prompt)}],
                model=self.model,
            )
            .choices[0]
            .message.content
        )
