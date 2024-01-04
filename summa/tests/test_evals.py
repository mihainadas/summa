import unittest
from summa.evals import Evaluators

"""
Restoration Accuracy: Evaluator for calculating the accuracy of a restoration.
"""

RAW_TEXT_WORD = "Transfăgărășan"
RAW_TEXT_WORD_LEN = len(RAW_TEXT_WORD)  # 14

RAW_TEXT_WORDS = "Transfăgărășanul s-a închis pentru iarnă"
RAW_TEXT_WORDS_LEN = len(RAW_TEXT_WORDS)  # 40


class TestRestorationAccuracyEvaluator_CS_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CS_CL.value
        return super().setUp()

    def test_echo(self):
        processed_text = RAW_TEXT_WORD
        expected_result = 1.0
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)

    def test_case_sensitive(self):
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

    def test_unequal_lengths(self):
        processed_text = "Transfăgărășanul"  # len = 16
        expected_result = 0.0
        result = self.eval.evaluate(RAW_TEXT_WORD, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationAccuracyEvaluator_CI_CL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CI_CL.value
        self.raw_text = "S-au împlinit de curând, pe 2 iunie, 201 ani de la nașterea lui C.A. Rosetti. Un bicentenar și-un an."
        return super().setUp()

    def test_base_case(self):
        processed_text = self.raw_text
        expected_result = 1.0
        result = self.eval.evaluate(self.raw_text, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationAccuracyEvaluator_CS_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CS_WL.value
        self.raw_text = "S-au împlinit de curând, pe 2 iunie, 201 ani de la nașterea lui C.A. Rosetti. Un bicentenar și-un an."
        return super().setUp()

    def test_base_case(self):
        processed_text = self.raw_text
        expected_result = 1.0
        result = self.eval.evaluate(self.raw_text, processed_text)
        self.assertEqual(result, expected_result)


class TestRestorationAccuracyEvaluator_CI_WL(unittest.TestCase):
    def setUp(self) -> None:
        self.eval = Evaluators.RA_CI_WL.value
        self.raw_text = "S-au împlinit de curând, pe 2 iunie, 201 ani de la nașterea lui C.A. Rosetti. Un bicentenar și-un an."
        return super().setUp()

    def test_base_case(self):
        processed_text = self.raw_text
        expected_result = 1.0
        result = self.eval.evaluate(self.raw_text, processed_text)
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
