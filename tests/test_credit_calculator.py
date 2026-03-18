from app.services.credit_calculator import (
    calculate_credits,
    count_third_position_vowels,
    extract_words,
    is_palindrome,
)


class TestExtractWords:
    def test_simple_sentence(self):
        assert extract_words("Hello world") == ["Hello", "world"]

    def test_with_apostrophe(self):
        assert extract_words("don't stop") == ["don't", "stop"]

    def test_with_hyphen(self):
        assert extract_words("well-known fact") == ["well-known", "fact"]

    def test_with_punctuation(self):
        assert extract_words("Hello, world!") == ["Hello", "world"]

    def test_digits_excluded(self):
        assert extract_words("test 123 abc") == ["test", "abc"]

    def test_empty_string(self):
        assert extract_words("") == []

    def test_only_punctuation(self):
        assert extract_words("!@#$%") == []


class TestCountThirdPositionVowels:
    def test_vowel_at_position_three(self):
        # 1-indexed position 3 -> index 2
        assert count_third_position_vowels("xxa") == 1

    def test_no_vowels_at_third_positions(self):
        assert count_third_position_vowels("abcdef") == 0  # pos 3='c', pos 6='f'

    def test_multiple_third_position_vowels(self):
        # "orbital latibro": pos 6='a', pos 12='i', pos 15='o'
        assert count_third_position_vowels("orbital latibro") == 3

    def test_empty_string(self):
        assert count_third_position_vowels("") == 0

    def test_short_string(self):
        assert count_third_position_vowels("ab") == 0


class TestIsPalindrome:
    def test_simple_palindrome(self):
        assert is_palindrome("racecar") is True

    def test_palindrome_with_spaces(self):
        assert is_palindrome("A man a plan a canal Panama") is True

    def test_not_palindrome(self):
        assert is_palindrome("hello") is False

    def test_empty_string(self):
        assert is_palindrome("") is False

    def test_single_character(self):
        assert is_palindrome("a") is True

    def test_palindrome_with_punctuation(self):
        assert is_palindrome("Was it a car or a cat I saw?") is True

    def test_mixed_case_palindrome(self):
        assert is_palindrome("Aba") is True

    def test_data_palindrome(self):
        assert is_palindrome("orbital latibro") is True


class TestBaseCostAndCharacters:
    def test_digits_only(self):
        """No words, just base cost + character cost."""
        # base(1) + chars(3*0.05=0.15) = 1.15
        assert calculate_credits("123") == 1.15

    def test_empty_string(self):
        """Empty message: base cost only."""
        assert calculate_credits("") == 1.0

    def test_character_count_scales(self):
        """Ten digit characters: base + 10*0.05 = 1.5."""
        assert calculate_credits("1234567890") == 1.5


class TestWordLengthMultipliers:
    def test_short_words_no_unique_bonus(self):
        """Repeated short words avoid the unique-word bonus."""
        # "go go": 5 chars, words ["go","go"] each 2 chars
        # base(1) + chars(0.25) + words(2*0.1) = 1.45
        # third vowels: pos 3=' ', pos ... -> none
        # not unique -> no bonus; not palindrome
        # But wait: "go go" -> "gogo" reversed = "ogog" -> not palindrome
        result = calculate_credits("go go")
        # pos 3 (idx 2): ' ' -> no vowel
        assert result == 1.45

    def test_medium_words_repeated(self):
        """Repeated medium words (4-7 chars)."""
        # "test test": 9 chars, words ["test","test"] each 4 chars
        # base(1) + chars(0.45) + words(2*0.2=0.4) = 1.85
        # no third vowels, not unique, not palindrome
        assert calculate_credits("test test") == 1.85

    def test_long_word_repeated(self):
        """Repeated 8+ char words."""
        # "thinking thinking": 17 chars, words ["thinking","thinking"] each 8 chars
        # base(1) + chars(0.85) + words(2*0.3=0.6) = 2.45
        # third vowels: positions 3,6,9,12,15
        #   t-h-i-n-k-i-n-g- -t-h-i-n-k-i-n-g
        #   idx2='i'(vowel+0.3), idx5='i'(vowel+0.3), idx8=' '(no),
        #   idx11='i'(vowel+0.3), idx14='i'(vowel+0.3)
        # = 4 * 0.3 = 1.2
        # subtotal: 2.45 + 1.2 = 3.65
        # not unique -> no bonus
        # palindrome? "thinkingthinking" reversed="gniknihTgniknihT" -> no
        assert calculate_credits("thinking thinking") == 3.65


class TestThirdVowels:
    def test_vowels_at_every_third_position(self):
        """Repeated non-unique words with known vowel positions."""
        # "aaa bbb ccc aaa": 15 chars
        # words: ["aaa","bbb","ccc","aaa"] -> 4 short words (0.1 each = 0.4)
        # base(1) + chars(0.75) + words(0.4)
        # third vowels at idx 2,5,8,11,14:
        #   a,a,a,' ',b,b,b,' ',c,c,c,' ',a,a,a
        #   idx2='a'(+0.3), idx5='b'(no), idx8='c'(no), idx11=' '(no), idx14='a'(+0.3)
        # = 0.6
        # subtotal: 1+0.75+0.4+0.6 = 2.75
        # not unique ("aaa" repeated) -> no bonus
        # palindrome? "aaabbbcccaaa" rev="aaacccbbbaaa" -> no
        assert calculate_credits("aaa bbb ccc aaa") == 2.75

    def test_uppercase_vowels_counted(self):
        """Uppercase vowels at third positions also count."""
        # "xxE": 3 chars, word ["xxE"] (3 chars -> 0.1)
        # base(1) + chars(0.15) + words(0.1) + vowel_at_3(0.3) = 1.55
        # unique -> max(1.55-2, 1) = 1
        assert calculate_credits("xxE") == 1.0


class TestLengthPenalty:
    def test_exactly_100_chars_no_penalty(self):
        """100 chars should NOT trigger penalty (only >100)."""
        msg = "x" * 100
        # base(1) + chars(5.0) + word(0.3 for 100-char word)
        # third vowels: none ('x' is never a vowel)
        # subtotal: 6.3, unique: max(6.3-2,1)=4.3, not palindrome (all x's IS palindrome!)
        # palindrome -> 4.3 * 2 = 8.6
        result = calculate_credits(msg)
        assert result == 8.6

    def test_101_chars_triggers_penalty(self):
        """101 chars triggers the +5 penalty."""
        msg = "x" * 101
        # base(1) + chars(5.05) + word(0.3) + penalty(5) = 11.35
        # unique: max(11.35-2,1)=9.35, palindrome -> 9.35*2 = 18.7
        result = calculate_credits(msg)
        assert result == 18.7


class TestUniqueWordBonus:
    def test_all_unique_words(self):
        """Unique words get a -2 bonus."""
        # "test this thing now please stop" (31 chars, 6 unique words)
        # base(1) + chars(31*0.05=1.55) + words: test(4->0.2)+this(4->0.2)+thing(5->0.2)
        #   +now(3->0.1)+please(6->0.2)+stop(4->0.2) = 1.1
        # third vowels at idx 2,5,8,11,14,17,20,23,26,29:
        #   idx17='o'(+0.3), idx23='a'(+0.3), idx29='o'(+0.3) = 0.9
        # subtotal: 1+1.55+1.1+0.9 = 4.55
        # unique bonus: max(4.55-2, 1) = 2.55
        # not palindrome
        assert calculate_credits("test this thing now please stop") == 2.55

    def test_repeated_words_no_bonus(self):
        # "test test" already tested -> 1.85 (no bonus applied)
        assert calculate_credits("test test") == 1.85

    def test_case_sensitive_uniqueness(self):
        """'Test' and 'test' are different words (case-sensitive), so all unique."""
        # "Test test" : 9 chars, words ["Test","test"] (4 chars each)
        # base(1) + chars(0.45) + words(0.4)
        # third vowels: idx2='s', idx5='t', idx8='t' -> none
        # subtotal: 1.85
        # unique (case-sensitive: "Test" != "test") -> max(1.85-2, 1) = 1
        # not palindrome
        assert calculate_credits("Test test") == 1.0

    def test_minimum_cost_floor(self):
        """Cost after unique bonus cannot go below 1."""
        # "Hi": 2 chars, word ["Hi"] (2 chars -> 0.1)
        # base(1) + chars(0.1) + words(0.1) = 1.2
        # unique -> max(1.2-2, 1) = 1.0
        assert calculate_credits("Hi") == 1.0


class TestPalindrome:
    def test_single_word_palindrome(self):
        """'racecar' is a palindrome."""
        # base(1) + chars(7*0.05=0.35) + word(7->0.2)
        # third vowels: idx2='c'(no), idx5='a'(+0.3) -> 0.3
        # subtotal: 1.85, unique: max(1.85-2,1)=1.0
        # palindrome -> 2.0
        assert calculate_credits("racecar") == 2.0

    def test_sentence_palindrome(self):
        """'A man a plan a canal Panama' is a classic palindrome."""
        # 27 chars, words: A(1),man(3),a(1),plan(4),a(1),canal(5),Panama(6)
        # base(1) + chars(1.35) + words(0.1+0.1+0.1+0.2+0.1+0.2+0.2=1.0)
        # third vowels: only idx26='a'(+0.3) -> 0.3
        # subtotal: 3.65, not unique("a" repeats) -> no bonus
        # palindrome -> 3.65*2 = 7.3
        assert calculate_credits("A man a plan a canal Panama") == 7.3

    def test_data_palindrome_orbital_latibro(self):
        """'orbital latibro' from the actual dataset is a palindrome."""
        # 15 chars, words: orbital(7->0.2), latibro(7->0.2) = 0.4
        # base(1) + chars(0.75) + words(0.4)
        # third vowels: idx5='a'(+0.3), idx11='i'(+0.3), idx14='o'(+0.3) -> 0.9
        # subtotal: 3.05, unique -> max(3.05-2,1) = 1.05
        # palindrome -> 1.05*2 = 2.1
        assert calculate_credits("orbital latibro") == 2.1

    def test_not_palindrome(self):
        """Non-palindrome message is not doubled."""
        assert calculate_credits("test test") == 1.85


class TestCombinedRules:
    def test_real_data_message_no_report(self):
        """Verify calculation for a message from the actual dataset."""
        text = "Are there any restrictions on alterations or improvements?"
        # 58 chars, 8 words all unique
        # base(1) + chars(2.9)
        # words: Are(3->0.1) there(5->0.2) any(3->0.1) restrictions(12->0.3)
        #        on(2->0.1) alterations(11->0.3) or(2->0.1) improvements(12->0.3) = 1.5
        # third vowels (idx 2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50,53,56):
        #   idx2='e', idx8='e', idx23='o', idx35='a', idx38='o', idx53='e' -> 6 * 0.3 = 1.8
        # subtotal: 1+2.9+1.5+1.8 = 7.2
        # unique: max(7.2-2,1) = 5.2
        # not palindrome
        assert calculate_credits(text) == 5.2

    def test_all_rules_combined(self):
        """A contrived message exercising most rules simultaneously."""

        text = "racecar"
        result = calculate_credits(text)
        assert result == 2.0
