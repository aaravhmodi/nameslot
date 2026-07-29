from pathlib import Path

from video.frames import require_cv2


def detect_yellow_star(frame_path: Path) -> dict:
    cv = require_cv2()
    image = cv.imread(str(frame_path))
    if image is None:
        raise ValueError(f"Could not read frame: {frame_path}")

    height, width = image.shape[:2]
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # FIFA's player marker is usually saturated yellow/gold. The range is intentionally broad
    # because capture brightness, HDR, and compression shift the marker color.
    lower = (18, 90, 120)
    upper = (42, 255, 255)
    mask = cv.inRange(hsv, lower, upper)

    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    candidates = []

    for contour in contours:
        area = cv.contourArea(contour)
        if area < 12 or area > 1800:
            continue

        x, y, w, h = cv.boundingRect(contour)
        aspect = w / h if h else 0
        if aspect < 0.45 or aspect > 2.2:
            continue

        center_x = x + w / 2
        center_y = y + h / 2
        if center_y > height * 0.9:
            continue

        saturation_bonus = min(area / 220, 1.0)
        shape_bonus = 1.0 - min(abs(1.0 - aspect), 1.0)
        upper_pitch_bonus = 0.15 if center_y < height * 0.55 else 0
        confidence = min(0.99, 0.35 + saturation_bonus * 0.35 + shape_bonus * 0.2 + upper_pitch_bonus)

        candidates.append({
            "x": round(center_x),
            "y": round(center_y),
            "width": w,
            "height": h,
            "area": round(area, 2),
            "confidence": round(confidence, 2),
        })

    candidates.sort(key=lambda item: item["confidence"], reverse=True)
    best = candidates[0] if candidates else None
    player_anchor = None
    if best:
        player_anchor = {
            "x": best["x"],
            "y": min(height, best["y"] + max(best["height"] * 4, 48)),
        }

    return {
        "detected": best is not None,
        "star": best,
        "player_anchor": player_anchor,
        "candidates": candidates[:5],
    }
