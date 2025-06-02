from contours import contour_filter
from east import east_filter


def test_contour_white_finder(white_intertitles):
    for image in white_intertitles:
        contour = contour_filter(image)
        east = east_filter(image)
        assert contour and east


def test_contour_black_finder(black_intertitles):
    for image in black_intertitles:
        contour = contour_filter(image)
        east = east_filter(image)
        assert contour and east


def test_contour_notsign_finder(not_intertitles):
    c = 0
    filtered = 0
    for image in not_intertitles:
        c += 1
        contour = contour_filter(image)
        east = east_filter(image)
        if not (contour and east):
            filtered += 1
    assert filtered == c - 5


def test_contour_falsepositive_finder(contour_false_positive):
    for image in contour_false_positive:
        contour = contour_filter(image)
        east = east_filter(image)
        assert not (contour and east)


def test_contour_inverse_finder(black_intertitles):
    for image in black_intertitles:
        contour = contour_filter(image)
        east = east_filter(image)
        assert contour and east
