def test_count_white_intertitles(white_intertitles):
    assert len(list(white_intertitles)) == 15


def test_count_sign_pairs(texts_and_intertitle):
    assert len(list(texts_and_intertitle)) == 29


def test_count_black_intertitles(black_intertitles):
    assert len(list(black_intertitles)) == 14


def test_count_not_signs(not_intertitles):
    assert len(list(not_intertitles)) == 19


def test_count_false_positive(contour_false_positive):
    assert len(list(contour_false_positive)) == 18
