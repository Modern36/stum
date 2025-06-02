from stum.tesseract import clean_text, count_special_chars


class TestCountSpecialChars:
    def test_count_empty(self):
        assert count_special_chars("") == 0

    def test_count_known_1(self):
        for special_char in "()[]{}-+=/><,|'\"!@#$%^&*_«—”\\":
            assert count_special_chars(special_char) == 1

    def test_in_text(self):
        assert count_special_chars("This is a text with no s.chars") == 0

    def test_in_text1(self):
        assert count_special_chars("This is a text w/ one s.chars") == 1


class TestStringCleaner:
    def test_cleaning(self):
        clean = "This is clean"
        assert clean == clean_text(clean)

    def test_the_L(self):
        assert "" == clean_text("^L")

    def test_empty(self):
        assert "" == clean_text("         \t\n\t\n\n\n\t\t")
