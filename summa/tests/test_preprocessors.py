import unittest
from summa import preprocessors


class TestPreprocessors(unittest.TestCase):
    def test_strip_diacritics_romanian_diacritics(self):
        romanian_diacritics = "ăĂâÂîÎșȘțȚ"
        expected_text = "aAaAiIsStT"
        result = preprocessors.strip_diacritics(romanian_diacritics)
        self.assertEqual(result, expected_text)

    def test_strip_diacritics_romanian_punctuation_text(self):
        romanian_punctuation_text = "Aveți vreo întrebare?"
        expected_text = "Aveti vreo intrebare?"
        result = preprocessors.strip_diacritics(romanian_punctuation_text)
        self.assertEqual(result, expected_text)

    def test_strip_diacritics_empty_string(self):
        empty_string = ""
        expected_text = ""
        result = preprocessors.strip_diacritics(empty_string)
        self.assertEqual(result, expected_text)

    def test_strip_diacritics_no_diacritics(self):
        no_diacritics_text = "Hello, World!"
        expected_text = "Hello, World!"
        result = preprocessors.strip_diacritics(no_diacritics_text)
        self.assertEqual(result, expected_text)

    def test_strip_diacritics_mixed_case(self):
        mixed_case_text = "ĂvĂțĂrĂ vRȘ"
        expected_text = "AvAtArA vRS"
        result = preprocessors.strip_diacritics(mixed_case_text)
        self.assertEqual(result, expected_text)

    def test_strip_diacritics_spanish_diacritics(self):
        spanish_diacritics = "áéíóúüñ"
        expected_text = "aeiouun"
        result = preprocessors.strip_diacritics(spanish_diacritics)
        self.assertEqual(result, expected_text)

    def test_strip_diacritics_french_diacritics(self):
        french_diacritics = "àâçéèêëîïôûùüÿ"
        expected_text = "aaceeeeiiouuuy"
        result = preprocessors.strip_diacritics(french_diacritics)
        self.assertEqual(result, expected_text)

    def test_strip_diacritics_german_diacritics(self):
        german_diacritics = "äöüß"
        expected_text = "aouß"
        result = preprocessors.strip_diacritics(german_diacritics)
        self.assertEqual(result, expected_text)


if __name__ == "__main__":
    unittest.main()
