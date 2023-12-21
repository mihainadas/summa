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

    def __init__(self, model: TextGenerationModel):
        self.model = model

    @abstractmethod
    def process(self, prompt: Prompt) -> ModelOutput:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class BasicTextProcessor(TextProcessor):
    """
    A processor class for basic text generation using a specified model.
    """

    def process(self, prompt):
        return self.model.generate(prompt)


class RestoreDiacritics(BasicTextProcessor):
    """
    A processor class for restoring diacritics in text using a specified model.
    """

    pass


class TextProcessors(Enum):
    """
    An enum for the available text processors.
    """

    BASIC = BasicTextProcessor
    RESTORE_DIACRITICS = RestoreDiacritics
