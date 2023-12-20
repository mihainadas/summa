import hashlib


def short_text(text):
    """
    Truncates the given text to a maximum of 10 words and adds ellipsis if necessary.

    Args:
        text (str): The input text to be truncated.

    Returns:
        str: The truncated text.

    """
    words = text.split()[:10]
    truncated_text = " ".join(words)
    if len(words) < len(text.split()):
        truncated_text += "..."
    return truncated_text


def md5(text):
    """
    Calculate the MD5 hash of a given text.

    Args:
        text (str): The text to calculate the MD5 hash for.

    Returns:
        str: The MD5 hash of the input text.
    """
    return hashlib.md5(text.strip().encode("utf-8")).hexdigest()
