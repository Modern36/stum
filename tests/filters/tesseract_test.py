import re

import pytest
from jiwer import cer

from stum.tesseract import extract_text
from tests.utils import (
    get_text_badsintertitles_pairs,
    get_text_intertitle_pairs,
)

ids, pairs = zip(*get_text_intertitle_pairs())

ids2, pairs2 = zip(*get_text_badsintertitles_pairs())

alpha_num_pattern = re.compile(r"[^a-zA-Z0-9]")


def two_decimal_cer(text_1, text2):
    error = cer(text_1, text2)
    clean_text = alpha_num_pattern.sub("", text_1).strip().lower()
    clean_result = alpha_num_pattern.sub("", text2).strip().lower()
    clean_error = cer(clean_text, clean_result)

    return round(min(error, clean_error), 2)


def test_tesseract_intertitle_finder(white_intertitles):
    for image in white_intertitles:
        result = extract_text(image)
        assert type(result) is str
        assert result != ""


def test_tesseract_blackintertitle_finder(black_intertitles):
    for image in black_intertitles:
        result = extract_text(image)
        assert type(result) is str
        assert result != ""


def test_tesseract_notintertitle_finder(contour_false_positive):
    counter = 0
    success = 0
    for image in contour_false_positive:
        counter += 1

        extracted_text = extract_text(image)
        if "" == extracted_text:
            success += 1
    assert (success / counter) == 1.0


@pytest.mark.parametrize(
    "text, image",
    pairs,
    ids=ids,
)
def test_tesseract_accuracy(text, image, target_cer):
    result = extract_text(image)
    error = two_decimal_cer(text, result)
    assert error <= target_cer, (text, result, error)


@pytest.mark.parametrize(
    "text, image",
    pairs2,
    ids=ids2,
)
def test_tesseract_known_high_error_rates(text, image, target_cer):
    result = extract_text(image)
    error = two_decimal_cer(text, result)
    assert 0.09 <= error, (text, result, error)
