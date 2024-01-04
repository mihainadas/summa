import unittest
from summa.evals import Evaluators

"""
Restoration Accuracy: Evaluator for calculating the accuracy of a restoration.
"""

RAW_TEXT_WORD = "Transfăgărășan"
RAW_TEXT_WORD_LEN = len(RAW_TEXT_WORD)  # 14

RAW_TEXT_WORDS = "Transfăgărășanul s-a închis pentru iarnă"
RAW_TEXT_WORDS_COUNT = len(RAW_TEXT_WORDS.split())  # 5


class TestRestorationAccuracyEvaluator_CS_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CS_CL.value
        return super().setUp()

    def test_echo(self):
        processed_text = RAW_TEXT_WORD
        expected_result = 1.0
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths(self):
        processed_text = "Transfăgărășanul"  # len = 16
        expected_result = 0.0
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORD.upper()
        processed_text = RAW_TEXT_WORD.lower()
        expected_result = 0.0
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)

    def test_missed_restoration(self):
        processed_text = "Transfagărășan"  # 1 char error (missed restoration)
        expected_result = (RAW_TEXT_WORD_LEN - 1) / RAW_TEXT_WORD_LEN
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_over_restoration(self):
        processed_text = "Trănsfăgărășan"  # 1 char error (over restoration)
        expected_result = (RAW_TEXT_WORD_LEN - 1) / RAW_TEXT_WORD_LEN
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationAccuracyEvaluator_CI_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CI_CL.value
        return super().setUp()

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORD.upper()
        processed_text = RAW_TEXT_WORD.lower()
        expected_result = 1.0
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationAccuracyEvaluator_CS_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CS_WL.value
        return super().setUp()

    def test_echo(self):
        processed_text = RAW_TEXT_WORDS
        expected_result = 1.0
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_added_character(self):
        processed_text = (
            RAW_TEXT_WORDS + "!"
        )  # added '!' at the end to make the last word longer which should not result in a 0.0 score as it does in RA_CS_CL
        expected_result = 0.8  # this should be 0.8 because the last word is 1 char longer than the original, so 1/5 = 0.2, 1 - 0.2 = 0.8
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORDS.upper()
        processed_text = RAW_TEXT_WORDS.lower()
        expected_result = 0.0
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_added_word(self):
        processed_text = (
            RAW_TEXT_WORDS + " " + "EXTRA_WORD"
        )  # added 'EXTRA_WORD' at the end to make the last word longer which should result in a 0.0 since the word lengths are now different
        expected_result = (
            0.0  # this should be 0.0 because the two texts have different word lengths
        )
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_missed_restoration(self):
        processed_text = "Transfăgărășanul s-a închis pentru iarna"  # 1 word error (missed restoration)
        expected_result = (RAW_TEXT_WORDS_COUNT - 1) / RAW_TEXT_WORDS_COUNT
        result = self.eval.evaluate(
            RAW_TEXT_WORDS, processed_text
        )  # this should be 0.8 because the last word has a missed restoration, so 1/5 = 0.2, 1 - 0.2 = 0.8
        self.assertEqual(result, expected_result)

    def test_over_restoration(self):
        processed_text = "Transfăgărășanul s-a închis pentru iărnă"  # 1 word error (over restoration)
        expected_result = (RAW_TEXT_WORDS_COUNT - 1) / RAW_TEXT_WORDS_COUNT
        result = self.eval.evaluate(
            RAW_TEXT_WORDS, processed_text
        )  # this should be 0.8 because the last word has an over restoration, so 1/5 = 0.2, 1 - 0.2 = 0.8
        self.assertEqual(result, expected_result)


class TestRestorationAccuracyEvaluator_CI_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CI_WL.value
        return super().setUp()

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORDS.upper()
        processed_text = RAW_TEXT_WORDS.lower()
        expected_result = 1.0
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)


"""
Restoration Error Rate: Evaluator for calculating the error rate of a restoration.
"""


# Case Sensitive, Character Level
class TestRestorationErrorRateEvaluator_CS_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CS_CL.value
        return super().setUp()

    def test_echo(self):
        processed_text = RAW_TEXT_WORD
        expected_result = 1.0  # this should be 1.0 because the two texts are identical
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_d1(self):
        processed_text = "ransfăgărășan"
        expected_result = (
            1 - 1 / RAW_TEXT_WORD_LEN
        )  # the levenstein distance is 1, so 1/14 = 0.07, and reversed is 1 - 0.07 = 0.93
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_d2(self):
        processed_text = "Transfăgărășanul"
        expected_result = (
            1 - 2 / RAW_TEXT_WORD_LEN
        )  # the levenshtein distance is 2, so 2/14 = 0.14, and reversed is 1 - 0.14 = 0.86
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_equal_lengths_d1(self):
        processed_text = "Transfagărășan"
        expected_result = (
            1 - 1 / RAW_TEXT_WORD_LEN
        )  # the levenshtein distance is 2, so 2/14 = 0.14, and reversed is 1 - 0.14 = 0.86
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_equal_lengths_d2(self):
        processed_text = "Transfagarășan"
        expected_result = (
            1 - 2 / RAW_TEXT_WORD_LEN
        )  # the levenshtein distance is 2, so 2/14 = 0.14, and reversed is 1 - 0.14 = 0.86
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_dhigh(self):
        processed_text = RAW_TEXT_WORD * 100
        expected_result = 0.0  # this should be 0.0 because the two texts have significantly different lengths
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORD.upper()
        processed_text = RAW_TEXT_WORD.lower()
        expected_result = (
            0.0  # this should be 0.0 because the case sensitivity is enabled
        )
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)


# Case Insensitive, Character Level
class TestRestorationErrorRateEvaluator_CI_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CI_CL.value
        return super().setUp()

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORD.upper()
        processed_text = RAW_TEXT_WORD.lower()
        expected_result = (
            1.0  # this should be 1.0 because the case sensitivity is ignored
        )
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)


# Case Sensitive, Word Level
class TestRestorationErrorRateEvaluator_CS_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CS_WL.value
        return super().setUp()

    def test_echo(self):
        processed_text = RAW_TEXT_WORDS
        expected_result = 1.0  # this should be 1.0 because the two texts are identical
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_d1(self):
        processed_text = "Transfăgărășanul s-a închis pentru această iarnă"
        expected_result = (
            1 - 1 / RAW_TEXT_WORDS_COUNT
        )  # the levenstein distance is 1 (one word needs to be deleted)
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_d2(self):
        processed_text = "Transfăgărășanul s-a închis pentru această iarnă grea"
        expected_result = (
            1 - 2 / RAW_TEXT_WORDS_COUNT
        )  # the levenstein distance is 2 (two words need to be deleted)
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_unequal_lengths_dhigh(self):
        processed_text = RAW_TEXT_WORDS * 100
        expected_result = (
            0.0  # this should be 0.0 because the two texts have different word lengths
        )
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)

    def test_equal_lengths_d1(self):
        processed_text = "Transfagărășanul s-a închis pentru iarnă"  # missed one diacratic in the first word
        expected_result = (
            1 - 1 / RAW_TEXT_WORDS_COUNT
        )  # the levenstein distance is 1 (one word needs to be deleted)
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_equal_lengths_d2(self):
        processed_text = "Transfagărășanul s-a inchis pentru iarnă"  # missed one diacratic in the first word, and one in the third word
        expected_result = (
            1 - 2 / RAW_TEXT_WORDS_COUNT
        )  # the levenstein distance is 1 (one word needs to be deleted)
        result = self.eval.evaluate(RAW_TEXT_WORDS, processed_text)
        self.assertEqual(result, expected_result)

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORD.upper()
        processed_text = RAW_TEXT_WORD.lower()
        expected_result = (
            0.0  # this should be 0.0 because the case sensitivity is enabled
        )
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationErrorRateEvaluator_CI_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CI_WL.value
        return super().setUp()

    def test_case_sensitivity(self):
        raw_text_upper = RAW_TEXT_WORD.upper()
        processed_text = RAW_TEXT_WORD.lower()
        expected_result = (
            1.0  # this should be 0.0 because the case sensitivity is enabled
        )
        result = self.eval.evaluate(raw_text_upper, processed_text)
        self.assertEqual(result, expected_result)
