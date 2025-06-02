from pathlib import Path

import cv2

model_loc = (
    Path(__file__).parents[2] / "models" / "frozen_east_text_detection.pb"
)

east_net = cv2.dnn.readNet(model_loc)

layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]


def east_filter(image: cv2.typing.MatLike) -> bool:
    """
    This function filters an image using the EAST text detection model.

    Parameters:
    - image (cv2.typing	MatLike): The input image to be filtered.

    Returns:
    - A boolean indicating whether the image contains any detected text or not.
    """

    image_height, image_width = image.shape[:2]

    blob = cv2.dnn.blobFromImage(
        image,
        1.0,
        (image_width, image_height),
        (123.68, 116.78, 103.94),
        swapRB=True,
        crop=False,
    )

    east_net.setInput(blob)
    scores, _ = east_net.forward(layerNames)

    num_scores = scores.shape[2]

    score_data = [scores[0, 0, i] for i in range(num_scores)]

    max_score = max([max(row) for row in score_data])
    return max_score > 0.5
