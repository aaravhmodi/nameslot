from pathlib import Path

try:
    import cv2
except ImportError:  # pragma: no cover - handled at runtime
    cv2 = None


def require_cv2():
    if cv2 is None:
        raise RuntimeError("opencv-python is required for video analysis. Run pip install -r backend/requirements.txt")
    return cv2


def sample_video_frames(video_path: Path, output_dir: Path, every_seconds: float = 1.0, max_frames: int = 120) -> list[dict]:
    cv = require_cv2()
    output_dir.mkdir(parents=True, exist_ok=True)

    capture = cv.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError("Could not open uploaded video")

    fps = capture.get(cv.CAP_PROP_FPS) or 30
    frame_count = int(capture.get(cv.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if fps else 0
    frame_step = max(int(fps * every_seconds), 1)

    frames: list[dict] = []
    frame_index = 0
    saved = 0

    while saved < max_frames:
        ok, frame = capture.read()
        if not ok:
            break

        if frame_index % frame_step == 0:
            timestamp = frame_index / fps
            frame_name = f"frame_{saved:04d}.jpg"
            frame_path = output_dir / frame_name
            cv.imwrite(str(frame_path), frame)
            frames.append({
                "index": saved,
                "frame_number": frame_index,
                "timestamp": round(timestamp, 2),
                "path": frame_path,
                "width": int(capture.get(cv.CAP_PROP_FRAME_WIDTH) or frame.shape[1]),
                "height": int(capture.get(cv.CAP_PROP_FRAME_HEIGHT) or frame.shape[0]),
            })
            saved += 1

        frame_index += 1

    capture.release()
    return frames
