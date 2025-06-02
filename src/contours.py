import cv2


def largest_contour(binary_image: cv2.typing.MatLike):
    """Returns the relative area of the largest contour of the image"""
    contours = cv2.findContours(
        binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )[0]
    largest = cv2.contourArea(max(contours, key=cv2.contourArea))

    width, height = binary_image.shape
    total_area = width * height
    relative_area = largest / total_area

    return relative_area


def contour_filter(image: cv2.typing.MatLike, threshold=0.9) -> bool:
    """Check if image has one large contour

    If the largest contour is smaller than the complement to the threshold,
    it also calculates the largest contour of the inverted image. This is a
    way to check for images with dark backgrounds and white text.

    Parameters
        image: cv2 image to check
        threshold: threshold to check contour area against, default is 90%

    Returns
        True if image has one contour larger than given threshold
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    binary = cv2.threshold(
        gray, 100, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV
    )[1]

    relative_area = largest_contour(binary)

    if (1 - relative_area) > threshold:
        inverted = cv2.bitwise_not(binary)

        inverteds_largest_area = largest_contour(inverted)

        relative_area = max(relative_area, inverteds_largest_area)

    return relative_area > threshold
