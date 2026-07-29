import json
import shutil
import subprocess
from pathlib import Path

from video.analyzer import ANALYSIS, UPLOADS


def find_video_file(video_id: str) -> Path:
    upload_dir = UPLOADS / video_id
    for suffix in (".mp4", ".mov", ".avi", ".mkv"):
        path = upload_dir / f"gameplay{suffix}"
        if path.exists():
            return path
    raise ValueError("Uploaded video file not found")


def load_commentary(video_id: str) -> dict:
    path = ANALYSIS / video_id / "commentary.json"
    if not path.exists():
        raise ValueError("Generate commentary cues before exporting proof clips")
    return json.loads(path.read_text(encoding="utf-8"))


def require_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to export proof clips. Install FFmpeg and make sure ffmpeg.exe is on PATH.")
    return ffmpeg


def export_proof_clips(video_id: str, padding_seconds: float = 2.0, max_clips: int = 6) -> dict:
    ffmpeg = require_ffmpeg()
    source_video = find_video_file(video_id)
    commentary = load_commentary(video_id)
    output_dir = ANALYSIS / video_id / "proof_clips"
    output_dir.mkdir(parents=True, exist_ok=True)

    clips = []
    for cue in commentary["cues"][:max_clips]:
        start = max(float(cue["start"]) - padding_seconds, 0)
        duration = max(float(cue["end"]) - float(cue["start"]) + padding_seconds * 2, 4)
        audio_path = ANALYSIS / video_id / "commentary" / Path(cue["audio_url"]).name
        if not audio_path.exists():
            continue

        out_name = f"{cue['cue_id']}_{cue['activity']['type']}.mp4"
        out_path = output_dir / out_name

        command = [
            ffmpeg,
            "-y",
            "-ss",
            f"{start:.2f}",
            "-t",
            f"{duration:.2f}",
            "-i",
            str(source_video),
            "-i",
            str(audio_path),
            "-filter_complex",
            "[0:a]volume=0.35[game];[1:a]volume=1.25[comm];[game][comm]amix=inputs=2:duration=longest:dropout_transition=0[aout]",
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-shortest",
            str(out_path),
        ]

        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(f"FFmpeg failed while exporting {cue['cue_id']}: {completed.stderr[-500:]}")

        clips.append({
            "cue_id": cue["cue_id"],
            "activity": cue["activity"],
            "start": cue["start"],
            "end": cue["end"],
            "text": cue["text"],
            "file": out_name,
            "video_url": f"/video/proof/{video_id}/{out_name}",
        })

    result = {
        "video_id": video_id,
        "clips_exported": len(clips),
        "clips": clips,
    }
    (output_dir / "proof_clips.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
