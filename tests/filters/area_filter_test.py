from stum.contours import contour_filter


def test_contour_sign_finder(white_intertitles):
    for image in white_intertitles:
        assert contour_filter(image)


def test_contour_notsign_finder(not_intertitles):
    c = 0
    filtered = 0
    for image in not_intertitles:
        c += 1
        if not contour_filter(image):
            filtered += 1
    assert filtered == c - 8


def test_contour_inverse_finder(black_intertitles):
    for image in black_intertitles:
        assert contour_filter(image)


def test_contour_on_black(black_frames):
    for black_frame in black_frames:
        assert contour_filter(black_frame)
