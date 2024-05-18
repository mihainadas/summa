from enum import Enum
from typing import Any
from .llms import TextGenerationLLM, TextGenerationOutput, Prompt
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_random_exponential, RetryCallState
import logging

logger = logging.getLogger(__name__)


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
    def process(self, model: TextGenerationLLM, prompt: Prompt) -> TextGenerationOutput:
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


class ExponentialBackoffTextProcessor(TextProcessor):
    """
    A processor class for text generation using exponential backoff.
    """

    def __init__(self):
        super().__init__(
            "Exponential Backoff Text Processor",
            "A processor class for text generation using exponential backoff.",
        )

    def log_retry(retry_state: RetryCallState):
        if retry_state.next_action is not None:
            sleep_time = retry_state.next_action.sleep
        else:
            sleep_time = "N/A"
        logger.info(
            f"Retrying {retry_state.fn.__name__} in {sleep_time:.2f} seconds... "
            f"(attempt {retry_state.attempt_number} of {retry_state.retry_object.stop.max_attempt_number})"
        )

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(25),
        before_sleep=log_retry,
    )
    def process(self, model, prompt):
        return model.generate(prompt)


class TextProcessors(Enum):
    """
    An enum for the available text processors.
    """

    BASIC = BasicTextProcessor()
    EXPONENTIAL_BACKOFF = ExponentialBackoffTextProcessor()
