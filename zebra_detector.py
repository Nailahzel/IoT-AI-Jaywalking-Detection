import cv2
import numpy as np

def detect_zebra(frame):
    """
    Zebra detector tuned for:
    - Cardboard prototype
    - Diagonal view
    - Indoor lighting
    """

    H, W = frame.shape[:2]

    # ------------------------------------------------
    # 1. Use only LOWER HALF of frame (realistic zebra position)
    # ------------------------------------------------
    roi_top = int(H * 0.4)
    roi = frame[roi_top:H, :]

    # ------------------------------------------------
    # 2. Grayscale + blur
    # ------------------------------------------------
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # ------------------------------------------------
    # 3. Fixed threshold (better for clean cardboard)
    # ------------------------------------------------
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    # ------------------------------------------------
    # 4. Morphological opening (separate stripes)
    # ------------------------------------------------
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # ------------------------------------------------
    # 5. Find contours
    # ------------------------------------------------
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    stripes = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Width relative to frame
        if w < 0.3 * W:
            continue

        # Height constraint
        if h < 15 or h > 0.3 * H:
            continue

        area = cv2.contourArea(cnt)
        if area < 500:
            continue

        stripes.append((x, y + roi_top, w, h))

    # ------------------------------------------------
    # 6. Zebra decision (2+ stripes)
    # ------------------------------------------------
    if len(stripes) >= 2:
        ys = [y for (_, y, _, _) in stripes]
        bottoms = [y + h for (_, y, _, h) in stripes]

        zebra_top = min(ys) - 10
        zebra_bottom = max(bottoms) + 10

        zebra_top = max(0, zebra_top)
        zebra_bottom = min(H, zebra_bottom)

        return True, stripes, zebra_top, zebra_bottom

    return False, [], None, None
