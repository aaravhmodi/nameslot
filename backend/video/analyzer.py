import json
import shutil
import uuid
from pathlib import Path

from video.frames import sample_video_frames
from video.star_detector import detect_yellow_star

ROOT = Path(__file__).parent.parent.parent
STORAGE = ROOT / "storage"
UPLOADS = STORAGE / "uploads"
ANALYSIS = STORAGE / "analysis"


def save_upload(file, suffix: str) -> tuple[str, Path]:
    upload_id = f"video_{uuid.uuid4().hex[:10]}"
    upload_dir = UPLOADS / upload_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    video_path = upload_dir / f"gameplay{suffix or '.mp4'}"
    with video_path.open("wb") as output:
        shutil.copyfileobj(file, output)
    return upload_id, video_path


def analyze_star_timeline(video_path: Path, upload_id: str) -> dict:
    analysis_dir = ANALYSIS / upload_id
    frames_dir = analysis_dir / "frames"
    frames = sample_video_frames(video_path, frames_dir)

    timeline = []
    for frame in frames:
        detection = detect_yellow_star(frame["path"])
        relative_frame = frame["path"].relative_to(STORAGE).as_posix()
        timeline.append({
            "time": frame["timestamp"],
            "frame_url": f"/video/frame/{relative_frame}",
            "width": frame["width"],
            "height": frame["height"],
            **detection,
        })

    detected_count = sum(1 for item in timeline if item["detected"])
    result = {
        "video_id": upload_id,
        "frames_sampled": len(timeline),
        "detections": detected_count,
        "detection_rate": round(detected_count / len(timeline), 2) if timeline else 0,
        "timeline": timeline,
    }

    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "analysis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
