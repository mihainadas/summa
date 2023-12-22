from enum import Enum
from typing import Any
from .llms import TextGenerationModel, ModelOutput, Prompt
from abc import ABC, abstractmethod


class TextProcessor(ABC):
    """
    Abstract base class for text processors.

    Args:
        model (TextGenerationModel): The text generation model used for text processing.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def process(self, model: TextGenerationModel, prompt: Prompt) -> ModelOutput:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class BasicTextProcessor(TextProcessor):
    """
    A processor class for basic text generation using a specified model.
    """

    def __init__(self):
        super().__init__(
            "Basic Text Processor",
            "A processor class for basic text generation using a specified model.",
        )

    def process(self, model, prompt):
        return model.generate(prompt)


class TextProcessors(Enum):
    """
    An enum for the available text processors.
    """

    BASIC = BasicTextProcessor()
