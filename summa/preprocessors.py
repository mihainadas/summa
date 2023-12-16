import unicodedata


def strip_diacritics(text):
    """
    Strips Romanian diacritics from the input text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with Romanian diacritics removed.
    """
    normalized_text = unicodedata.normalize("NFKD", text)
    stripped_text = "".join(c for c in normalized_text if not unicodedata.combining(c))
    return stripped_text
