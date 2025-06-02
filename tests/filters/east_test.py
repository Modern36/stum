from east import east_filter


def test_east_sign_finder(white_intertitles):
    for image in white_intertitles:
        assert east_filter(image)


def test_east_inverse_finder(black_intertitles):
    for image in black_intertitles:
        assert east_filter(image)
