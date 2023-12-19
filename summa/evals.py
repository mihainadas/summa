def f1_score(precision, recall):
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


def f1_score_chars(original_text, restored_text):
    """
    Calculate the F1 score for character-level evaluation of restored text.

    Args:
        original_text (str): The original text.
        restored_text (str): The restored text.

    Returns:
        float: The F1 score.
    """
    # Initialize counts for true positives, false positives, and false negatives
    TP, FP, FN = 0, 0, 0

    # Iterate through the characters of the original and restored text
    for orig_char, rest_char in zip(original_text, restored_text):
        if orig_char == rest_char:
            TP += 1  # Correctly restored diacritic
        else:
            if orig_char.lower() == rest_char.lower():
                FN += 1  # Missed diacritic
            else:
                FP += 1  # Incorrectly added or misplaced diacritic

    # Adjust for lengths
    FP += abs(len(restored_text) - len(original_text))

    # Calculate Precision and Recall
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    # Calculate F1 Score
    return f1_score(precision, recall)


def f1_score_words(original_text, restored_text):
    """
    Calculate the F1 score for word-level evaluation of text restoration.

    Args:
        original_text (str): The original text.
        restored_text (str): The restored text.

    Returns:
        float: The F1 score.
    """
    # Splitting the texts into words
    original_words = original_text.split()
    restored_words = restored_text.split()

    # Initialize counts
    TP = 0
    FP = 0
    FN = 0

    # Iterate through the words
    for orig_word, rest_word in zip(original_words, restored_words):
        if orig_word == rest_word:
            TP += 1  # Correctly restored word
        else:
            FP += 1  # Word does not match
            FN += 1  # Missed correct word

    # Adjust for length differences
    len_diff = abs(len(original_words) - len(restored_words))
    FP += len_diff
    FN += len_diff

    # Calculating Precision and Recall
    precision = TP / (TP + FP) if TP + FP > 0 else 0
    recall = TP / (TP + FN) if TP + FN > 0 else 0

    return f1_score(precision, recall)


def ca_score_chars(original_text, restored_text):
    """
    Calculates the character accuracy score between the original text and the restored text.

    Args:
        original_text (str): The original text.
        restored_text (str): The restored text.

    Returns:
        float: The character accuracy score, ranging from 0 to 1.
               A score of 1 indicates a perfect match, while a score of 0 indicates no match.
    """
    # Check if the number of characters match, otherwise return 0
    if len(original_text) != len(restored_text):
        return 0

    # Initialize counts
    total_diacritics = 0
    correct_restorations = 0

    # Iterate through the characters of both texts
    for orig_char, rest_char in zip(original_text, restored_text):
        if orig_char.lower() in [
            "ă",
            "â",
            "î",
            "ș",
            "ț",
        ]:  # Check if character is a diacritic
            total_diacritics += 1
            if orig_char == rest_char:
                correct_restorations += 1

    # Calculate accuracy
    if total_diacritics == 0:
        return 1.0  # Avoid division by zero; if no diacritics, accuracy is perfect
    score = correct_restorations / total_diacritics
    return score


def ca_score_words(original_text, restored_text):
    """
    Calculates the Corrected Accuracy (CA) score for word-level evaluation.

    The CA score is calculated by comparing the original text with the restored text
    and counting the number of correctly restored words. The CA score is the ratio
    of correctly restored words to the total number of words in the original text.

    Args:
        original_text (str): The original text.
        restored_text (str): The restored text.

    Returns:
        float: The Corrected Accuracy (CA) score.

    Raises:
        None
    """
    # Splitting the texts into words
    original_words = original_text.split()
    restored_words = restored_text.split()

    # Check if the number of words match, otherwise return 0
    if len(original_words) != len(restored_words):
        return 0

    # Initialize counts
    total_words = len(original_words)
    correct_restorations = 0

    # Iterate through the words
    for orig_word, rest_word in zip(original_words, restored_words):
        if orig_word == rest_word:
            correct_restorations += 1  # Correctly restored word

    # Calculate accuracy
    if total_words == 0:
        return 1.0  # Avoid division by zero; if no words, accuracy is perfect
    score = correct_restorations / total_words
    return score
