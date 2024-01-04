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


class TestRestorationErrorRateEvaluator_CS_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CS_CL.value
        self.raw_text = "S-au împlinit de curând, pe 2 iunie, 201 ani de la nașterea lui C.A. Rosetti. Un bicentenar și-un an."
        return super().setUp()

    def test_base_case(self):
        processed_text = self.raw_text
        expected_result = 1.0
        result = self.eval.evaluate(self.raw_text, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationErrorRateEvaluator_CI_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CI_CL.value
        self.raw_text = "S-au împlinit de curând, pe 2 iunie, 201 ani de la nașterea lui C.A. Rosetti. Un bicentenar și-un an."
        return super().setUp()

    def test_base_case(self):
        processed_text = self.raw_text
        expected_result = 1.0
        result = self.eval.evaluate(self.raw_text, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationErrorRateEvaluator_CS_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CS_WL.value
        self.raw_text = "S-au împlinit de curând, pe 2 iunie, 201 ani de la nașterea lui C.A. Rosetti. Un bicentenar și-un an."
        return super().setUp()

    def test_base_case(self):
        processed_text = self.raw_text
        expected_result = 1.0
        result = self.eval.evaluate(self.raw_text, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationErrorRateEvaluator_CI_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RER_CI_WL.value
        self.raw_text = "S-au împlinit de curând, pe 2 iunie, 201 ani de la nașterea lui C.A. Rosetti. Un bicentenar și-un an."
        return super().setUp()

    def test_base_case(self):
        processed_text = self.raw_text
        expected_result = 1.0
        result = self.eval.evaluate(self.raw_text, processed_text)
        self.assertEqual(result, expected_result)
