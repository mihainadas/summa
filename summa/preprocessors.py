import unicodedata
from abc import ABC, abstractmethod


class Preprocessor(ABC):
    """
    Abstract base class for all preprocessors.
    """

    @abstractmethod
    def preprocess(self, input: str) -> str:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class StripDiacritics(Preprocessor):
    """
    Strips Romanian diacritics from the input text.
    """

    def preprocess(self, input):
        normalized_text = unicodedata.normalize("NFKD", input)
        stripped_text = "".join(
            c for c in normalized_text if not unicodedata.combining(c)
        )
        return stripped_text
