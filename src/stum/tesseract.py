"""
The purpose of this file is twofold:
1. Filter out some of the false-positives that slipped through the
contour filter.

2. Extract the text from the images, mirrored or not.

    For now I think it might be enough to pass both versions of the image
    through tesseract and keep the one that has the fewest special characters.
"""

import re

import cv2
import pytesseract

from stum.east import east_filter

specials = re.compile(r"[^a-zA-Z0-9 \nÅåÄäÖö\.áé,”]")
onlyvowels = re.compile(r"[aouåeiyäöAOUÅEIYÄÖ]{2;}")
words_with_numbers = re.compile(r"([a-zA-ZÅåÄäÖö][0-9]|[a-zA-ZÅåÄäÖö][0-9])+")


def count_special_chars(text: str):
    return len(specials.findall(text) + words_with_numbers.findall(text))


def clean_text(text: str) -> str:
    result = onlyvowels.sub("", text)
    result = result.replace("^L", "").strip()
    return result if len(result) > 1 else ""


def extract_text(image: cv2.typing.MatLike, contour_threshold=0.9) -> str:
    """Extract texts, or lack thereof from an image

    Uses `ocr_mirror_ocr` to OCR original and mirrored version of the image.

    If no text is found, it first checks for contours in the image -- and
    if the largest contour is > `contour_threshold` (default 90%) the
    binary inverse of the image will be used instead. If this also has a
    single contour that is > `contour_threshold` an empty string is returned.

    Otherwise, the image is cropped to the contour and then passed thorugh
    `ocr_mirror_ocr` to get the text (or lack thereof.)

    Arguments:
        image {cv2.typing.MatLike} -- The image to extract texts from
    output:
        {str} -- The extracted text, is empty if no text is found
    """

    if not east_filter(image):
        return ""

    result = ocr_mirror_ocr(image)

    if result != "":

        return result

    _, thresh1 = cv2.threshold(
        cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        ),
        100,
        255,
        cv2.THRESH_BINARY_INV,
    )

    im2 = image.copy()
    width, height, _ = image.shape
    total_area = width * height
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    x, y, w, h = largest_contour_box(thresh1, rect_kernel)

    if contour_area(x, y, w, h) / total_area > contour_threshold:
        thresh1 = cv2.bitwise_not(thresh1)

        x, y, w, h = largest_contour_box(thresh1, rect_kernel)

        if contour_area(x, y, w, h) / total_area > contour_threshold:

            return ""

    # Cropping the text block for giving input to OCR
    cropped = im2[y : y + h, x : x + w]

    return ocr_mirror_ocr(cropped)


def ocr_mirror_ocr(image):
    """Extract texts, or lack thereof from an image

    Passes the original and a mirrored version of the image through OCR
    and returns the 'best' text of the two.
    'best' being the text with the fewest special characters.

    Arguments:
        image {cv2.typing.MatLike} -- The image to extract texts from
    output:
        {str} -- The extracted text, is empty if no text is found
    """

    original_text = pytesseract.image_to_string(image, lang="swe")
    mirrored_text = pytesseract.image_to_string(cv2.flip(image, 1), lang="swe")

    # Use the text with the fewest special characters.
    if count_special_chars(mirrored_text) < count_special_chars(original_text):
        text = mirrored_text
    else:
        text = original_text

    result = clean_text(text)
    return result


def contour_area(x, y, w, h):
    return (x + w) * (y + h)


def largest_contour_box(thresh1, rect_kernel):
    """Finds the largest contour in an image

    Arguments:
        thresh1 {cv2.typing.MatLike} -- The threshold image to find contours from
        rect_kernel {cv2.typing.KernelLike} -- A kernel used for dilation, must be square
    output:
        The box-coorinates of the largest contour found in the image
        x - horizontal coordinate
        w - width of the contour box
        y - vertical coordinate
        h - height of the contour box
    """

    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
    contours, _ = cv2.findContours(
        dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    if len(contours) == 0:
        w, h = thresh1.shape[:2]
        return 0, 0, w, h

    # Find the largest contour in the image and extract the box-coordinates from

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    return x, y, w, h
