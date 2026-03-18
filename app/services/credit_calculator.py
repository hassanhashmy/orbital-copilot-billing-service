import re

VOWEL_CHARACTERS = set("aeiouAEIOU")
WORD_REGEX = re.compile(r"[a-zA-Z'\-]+")
NON_ALPHANUMERIC_REGEX = re.compile(r"[^a-zA-Z0-9]")


def extract_words(text: str) -> list[str]:
    """Extract valid words from text."""

    return WORD_REGEX.findall(text)


def count_third_position_vowels(text: str) -> int:
    """Count vowels at positions 3, 6, 9... (1-indexed)."""

    return sum(
        1 for i in range(2, len(text), 3)
        if text[i] in VOWEL_CHARACTERS
    )


def is_palindrome(text: str) -> bool:
    """Check if text is a palindrome ignoring non-alphanumeric characters."""

    cleaned = NON_ALPHANUMERIC_REGEX.sub("", text).lower()
    return bool(cleaned) and cleaned == cleaned[::-1]


def word_length_cost(word: str) -> float:
    """Return credit cost based on word length."""

    length = len(word)
    return 0.1 if length <= 3 else 0.2 if length <= 7 else 0.3


def calculate_credits(text: str) -> float:
    """
    Calculate the number of credits consumed by a message.

    Rules:
    1. Base cost of 1 credit
    2. +0.05 credits per character
    3. Word length multiplier
    4. +0.3 for each vowel at positions 3,6,9...
    5. +5 penalty if message > 100 characters
    6. -2 bonus if all words are unique (floor at 1)
    7. Double total if message is palindrome
    """

    words = extract_words(text)
    text_length = len(text)

    cost = 1.0
    cost += 0.05 * text_length
    cost += sum(word_length_cost(word) for word in words)
    cost += 0.3 * count_third_position_vowels(text)
    cost += 5.0 * (text_length > 100)
    if words and len(words) == len(set(words)):
        cost = max(cost - 2.0, 1.0)
    cost *= 2 if is_palindrome(text) else 1

    return round(cost, 2)
