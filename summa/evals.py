import logging
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class EvaluatorOutput:
    """
    Represents the output of an evaluator.
    """

    def __init__(self, evaluator: "Evaluator", score: float):
        """
        Initializes the evaluator output.

        Args:
            evaluator (Evaluator): The evaluator.
            score (float): The score of the evaluator.
        """
        self.evaluator = evaluator
        self.score = score

    def __str__(self) -> str:
        return f"{self.evaluator.name}: {self.score}"


class Evaluator(ABC):
    """
    Abstract base class for all evaluators.
    """

    def __init__(self, name: str, description: str):
        """
        Initializes the evaluator.

        Args:
            name (str): The name of the evaluator.
            description (str): The description of the evaluator.
        """
        self.name = name
        self.description = description

    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def evaluate(self, raw_text: str, processed_text: str) -> EvaluatorOutput:
        """
        Evaluates the restored text against the original text.

        Args:
            raw_text (str): The original text.
            processed_text (str): The processed text.
        """
        pass


class RestorationEvaluator(Evaluator, ABC):
    """
    Specialized evaluator for restoration evaluators. Provides methods for adjusting inputs for case sensitivity and padding and for evaluating at character and word levels.
    """

    def __init__(
        self,
        name: str,
        description: str,
        case_sensitive=True,
        strip_padding=True,
        word_level=False,
    ):
        self.case_sensitive = case_sensitive
        self.strip_padding = strip_padding
        self.word_level = word_level

        name = f'{name} ({"Case Sensitive" if case_sensitive else "Case Insensitive"}, {"Word" if word_level else "Character"} Level, {"Padding Stripped" if strip_padding else "Padding Preserved"})'

        super().__init__(name, description)

    def adjust_inputs(self, raw_text: str, processed_text: str) -> tuple[str, str]:
        """
        Adjusts the inputs for the evaluator based on the evaluator's settings.

        Args:
            raw_text (str): The original text.
            processed_text (str): The processed text.

        Returns:
            tuple[str, str]: The adjusted inputs.
        """
        if not self.case_sensitive:
            raw_text = raw_text.lower()
            processed_text = processed_text.lower()

        if self.strip_padding:
            raw_text = raw_text.strip()
            processed_text = processed_text.strip()

        return raw_text, processed_text


class RestorationAccuracyEvaluator(RestorationEvaluator):
    def __init__(
        self,
        case_sensitive=True,
        strip_padding=True,
        word_level=False,
    ):
        super().__init__(
            "RA",
            "Restoration Accuracy: Evaluator for calculating the accuracy of a restoration.",
            case_sensitive,
            strip_padding,
            word_level,
        )

    def _evaluate_word_level(self, raw_text: str, processed_text: str) -> float:
        # Splitting the texts into words
        raw_words = raw_text.split()
        processed_words = processed_text.split()

        # Check if the number of words match, otherwise return 0
        if len(raw_words) != len(processed_words):
            logger.warning(
                "The lengths of original and restored texts must be the same for accuracy calculation."
            )
            return 0

        # Initialize counts
        total_words = len(raw_words)
        correct_restorations = 0

        # Iterate through the words
        for raw_word, proc_word in zip(raw_words, processed_words):
            if raw_word == proc_word:
                correct_restorations += 1

        return correct_restorations / total_words

    def _evaluate_char_level(self, raw_text: str, processed_text: str) -> float:
        # Check if the number of characters match, otherwise return 0
        if len(raw_text) != len(processed_text):
            logger.warning(
                "The lengths of original and restored texts must be the same for accuracy calculation."
            )
            return 0

        # Initialize counts
        total_chars = len(raw_text)
        correct_restorations = 0

        # Iterate through the characters
        for raw_char, proc_char in zip(raw_text, processed_text):
            if raw_char == proc_char:
                correct_restorations += 1

        return correct_restorations / total_chars

    def evaluate(self, raw_text: str, processed_text: str) -> float:
        """
        Evaluates the restored text against the original text.

        Args:
            raw_text (str): The original text.
            processed_text (str): The processed text.

        Returns:
            float: The score of the evaluator.
        """

        (raw_text, processed_text) = self.adjust_inputs(raw_text, processed_text)

        if self.word_level:
            return self._evaluate_word_level(raw_text, processed_text)
        else:
            return self._evaluate_char_level(raw_text, processed_text)


class RestorationErrorRateEvaluator(RestorationEvaluator):
    def __init__(
        self,
        case_sensitive=True,
        strip_padding=True,
        word_level=False,
    ):
        super().__init__(
            "RER",
            "Restoration Error Rate: Evaluator for calculating the error rate of a restoration.",
            case_sensitive,
            strip_padding,
            word_level,
        )

    @staticmethod
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return RestorationErrorRateEvaluator.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def calculate_cer(original_text, restored_text):
        distance = RestorationErrorRateEvaluator.levenshtein_distance(
            original_text, restored_text
        )
        return distance / len(original_text)

    @staticmethod
    def calculate_wer(original_text, restored_text):
        original_words = original_text.split()
        restored_words = restored_text.split()
        distance = RestorationErrorRateEvaluator.levenshtein_distance(
            original_words, restored_words
        )
        return distance / len(original_words)

    def evaluate(self, raw_text: str, processed_text: str) -> EvaluatorOutput:
        (raw_text, processed_text) = self.adjust_inputs(raw_text, processed_text)

        # calculations are inverted (1 - error rate) because we want to be consistent with the other evaluators
        if self.word_level:
            return 1 - self.calculate_wer(raw_text, processed_text)
        else:
            return 1 - self.calculate_cer(raw_text, processed_text)


class Evaluators(Enum):
    RA_CS_CL = RestorationAccuracyEvaluator(
        case_sensitive=True, strip_padding=True, word_level=False
    )
    RA_CI_CL = RestorationAccuracyEvaluator(
        case_sensitive=False, strip_padding=True, word_level=False
    )
    RA_CS_WL = RestorationAccuracyEvaluator(
        case_sensitive=True, strip_padding=True, word_level=True
    )
    RA_CI_WL = RestorationAccuracyEvaluator(
        case_sensitive=False, strip_padding=True, word_level=True
    )
    RER_CS_CL = RestorationErrorRateEvaluator(
        case_sensitive=True, strip_padding=True, word_level=False
    )
    RER_CI_CL = RestorationErrorRateEvaluator(
        case_sensitive=False, strip_padding=True, word_level=True
    )
    RER_CS_WL = RestorationErrorRateEvaluator(
        case_sensitive=True, strip_padding=True, word_level=False
    )
    RER_CI_WL = RestorationErrorRateEvaluator(
        case_sensitive=False, strip_padding=True, word_level=True
    )
