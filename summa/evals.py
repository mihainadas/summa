def f1_score(precision, recall):
    return (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )


# Calculates the F1 score of the restored text compared to the original text, at a character level.
def f1_score_chars(original_text, restored_text):
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


# Calculates the F1 score of the restored text compared to the original text, at a word level.
def f1_score_words(original_text, restored_text):
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
