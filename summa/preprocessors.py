from enum import Enum
import unicodedata
from abc import ABC, abstractmethod


class TextPreprocessor(ABC):
    """
    Abstract base class for all preprocessors.
    """

    @abstractmethod
    def preprocess(self, input: str) -> str:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class BasicTextPreprocessor(TextPreprocessor):
    """
    A preprocessor class for basic text processing that takes the input text as is and strips it of leading and trailing whitespace.
    """

    def preprocess(self, input):
        return input.strip()


class StripDiacritics(TextPreprocessor):
    """
    Strips Romanian diacritics from the input text.
    """

    def preprocess(self, input):
        normalized_text = unicodedata.normalize("NFKD", input)
        stripped_text = "".join(
            c for c in normalized_text if not unicodedata.combining(c)
        )
        return stripped_text


class TextPreprocessors(Enum):
    """
    An enum for the available preprocessors.
    """

    BASIC = BasicTextPreprocessor
    STRIP_DIACRITICS = StripDiacritics
