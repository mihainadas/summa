from abc import ABC, abstractmethod
from enum import Enum


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

    @abstractmethod
    def evaluate(self, raw_text: str, processed_text: str) -> EvaluatorOutput:
        """
        Evaluates the restored text against the original text.

        Args:
            raw_text (str): The original text.
            processed_text (str): The processed text.
        """
        pass


def _f1_score(precision, recall):
    """
    Calculate the F1 score given the precision and recall.

    Args:
        precision (float): The precision value.
        recall (float): The recall value.

    Returns:
        float: The F1 score.
    """
    return (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )


class F1ScoreWordsEvaluator(Evaluator):
    """
    Evaluates the restored text against the original text using the F1 score for word-level evaluation.
    """

    def __init__(self):
        """
        Initializes the evaluator.
        """
        super().__init__("F1 Score (Words)", "A word-level F1 score evaluator.")

    def evaluate(self, raw_text: str, processed_text: str) -> float:
        """
        Evaluates the restored text against the original text using the F1 score for word-level evaluation.

        Args:
            raw_text (str): The original text.
            processed_text (str): The restored text.

        Returns:
            float: The F1 score.
        """
        raw_words = raw_text.split()
        processed_words = processed_text.split()

        # Initialize counts
        TP = 0
        FP = 0
        FN = 0

        # Iterate through the words
        for orig_word, rest_word in zip(raw_words, processed_words):
            if orig_word == rest_word:
                TP += 1  # Correctly restored word
            else:
                FP += 1  # Word does not match
                FN += 1  # Missed correct word

        # Adjust for length differences
        len_diff = abs(len(raw_words) - len(processed_words))
        FP += len_diff
        FN += len_diff

        # Calculating Precision and Recall
        precision = TP / (TP + FP) if TP + FP > 0 else 0
        recall = TP / (TP + FN) if TP + FN > 0 else 0

        return _f1_score(precision, recall)


class F1ScoreCharsEvaluator(Evaluator):
    """
    Evaluates the restored text against the original text using the F1 score for character-level evaluation.
    """

    def __init__(self):
        """
        Initializes the evaluator.
        """
        super().__init__("F1 Score (Chars)", "A character-level F1 score evaluator.")

    def evaluate(self, raw_text: str, processed_text: str) -> float:
        """
        Evaluates the restored text against the original text using the F1 score for character-level evaluation.

        Args:
            raw_text (str): The original text.
            processed_text (str): The restored text.

        Returns:
            float: The F1 score.
        """
        # Initialize counts for true positives, false positives, and false negatives
        TP, FP, FN = 0, 0, 0

        # Iterate through the characters of the original and restored text
        for raw_char, proc_char in zip(raw_text, processed_text):
            if raw_char == proc_char:
                TP += 1  # Correctly restored diacritic
            else:
                if raw_char.lower() == proc_char.lower():
                    FN += 1  # Missed diacritic
                else:
                    FP += 1  # Incorrectly added or misplaced diacritic

        # Adjust for lengths
        FP += abs(len(processed_text) - len(raw_text))

        # Calculate Precision and Recall
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0

        # Calculate F1 Score
        return _f1_score(precision, recall)


class CharacterAccuracyEvaluator(Evaluator):
    """
    Evaluates the restored text against the original text using the character accuracy score.
    """

    def __init__(self):
        """
        Initializes the evaluator.
        """
        super().__init__("Character Accuracy", "A character-level accuracy evaluator.")

    def evaluate(self, raw_text: str, processed_text: str) -> float:
        """
        Evaluates the restored text against the original text using the character accuracy score.

        Args:
            raw_text (str): The original text.
            processed_text (str): The restored text.

        Returns:
            float: The character accuracy score.
        """
        # Check if the number of characters match, otherwise return 0
        if len(raw_text) != len(processed_text):
            return 0

        # Initialize counts
        total_diacritics = 0
        correct_restorations = 0

        # Iterate through the characters of both texts
        for raw_char, proc_char in zip(raw_text, processed_text):
            if raw_char.lower() in [
                "ă",
                "â",
                "î",
                "ș",
                "ț",
            ]:  # Check if character is a diacritic
                total_diacritics += 1
                if raw_char == proc_char:
                    correct_restorations += 1

        # Calculate accuracy
        if total_diacritics == 0:
            return 1.0  # Avoid division by zero; if no diacritics, accuracy is perfect
        score = correct_restorations / total_diacritics
        return score


class WordAccuracyEvaluator(Evaluator):
    """
    Evaluates the restored text against the original text using the word accuracy score.
    """

    def __init__(self):
        """
        Initializes the evaluator.
        """
        super().__init__("Word Accuracy", "A word-level accuracy evaluator.")

    def evaluate(self, raw_text: str, processed_text: str) -> float:
        """
        Evaluates the restored text against the original text using the word accuracy score.

        Args:
            raw_text (str): The original text.
            processed_text (str): The restored text.

        Returns:
            float: The word accuracy score.
        """
        # Splitting the texts into words
        raw_words = raw_text.split()
        processed_words = processed_text.split()

        # Check if the number of words match, otherwise return 0
        if len(raw_words) != len(processed_words):
            return 0

        # Initialize counts
        total_words = len(raw_words)
        correct_restorations = 0

        # Iterate through the words
        for raw_word, proc_word in zip(raw_words, processed_words):
            if raw_word == proc_word:
                correct_restorations += 1  # Correctly restored word

        # Calculate accuracy
        if total_words == 0:
            return 1.0  # Avoid division by zero; if no words, accuracy is perfect
        score = correct_restorations / total_words
        return score


class Evaluators(Enum):
    F1_SCORE_WORDS = F1ScoreWordsEvaluator()
    F1_SCORE_CHARS = F1ScoreCharsEvaluator()
    CHARACTER_ACCURACY = CharacterAccuracyEvaluator()
    WORD_ACCURACY = WordAccuracyEvaluator()
