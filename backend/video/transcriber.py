import json
import os
import subprocess
from pathlib import Path

from video.analyzer import ANALYSIS
from video.renderer import find_video_file, require_ffmpeg


def require_whisper_cpp() -> tuple[str, str]:
    executable = os.getenv("WHISPER_CPP_PATH")
    model = os.getenv("WHISPER_MODEL_PATH")

    if not executable:
        raise RuntimeError("WHISPER_CPP_PATH is not set. Point it to whisper-cli.exe or main.exe from whisper.cpp.")
    if not model:
        raise RuntimeError("WHISPER_MODEL_PATH is not set. Point it to a whisper.cpp ggml model .bin file.")

    executable_path = Path(executable)
    model_path = Path(model)
    if not executable_path.exists():
        raise RuntimeError(f"WHISPER_CPP_PATH does not exist: {executable}")
    if not model_path.exists():
        raise RuntimeError(f"WHISPER_MODEL_PATH does not exist: {model}")

    return str(executable_path), str(model_path)


def extract_audio_for_transcription(video_id: str) -> Path:
    ffmpeg = require_ffmpeg()
    source_video = find_video_file(video_id)
    output_dir = ANALYSIS / video_id / "transcript"
    output_dir.mkdir(parents=True, exist_ok=True)
    wav_path = output_dir / "audio_16k.wav"

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(source_video),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(wav_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"FFmpeg failed while extracting audio: {completed.stderr[-500:]}")
    return wav_path


def normalize_segment(segment: dict) -> dict:
    start = segment.get("t0", segment.get("start", 0))
    end = segment.get("t1", segment.get("end", 0))

    # whisper.cpp JSON uses centiseconds for t0/t1. Other wrappers may emit seconds.
    if isinstance(start, int) and start > 100:
        start = start / 100
    if isinstance(end, int) and end > 100:
        end = end / 100

    return {
        "start": round(float(start), 2),
        "end": round(float(end), 2),
        "text": str(segment.get("text", "")).strip(),
    }


def parse_whisper_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_segments = data.get("transcription") or data.get("segments") or []
    return [normalize_segment(segment) for segment in raw_segments if str(segment.get("text", "")).strip()]


def transcribe_video_with_whisper_cpp(video_id: str) -> dict:
    whisper, model = require_whisper_cpp()
    wav_path = extract_audio_for_transcription(video_id)
    output_dir = ANALYSIS / video_id / "transcript"
    output_base = output_dir / "whisper"
    json_path = output_base.with_suffix(".json")

    command = [
        whisper,
        "-m",
        model,
        "-f",
        str(wav_path),
        "-oj",
        "-of",
        str(output_base),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"whisper.cpp failed: {completed.stderr[-800:] or completed.stdout[-800:]}")
    if not json_path.exists():
        raise RuntimeError("whisper.cpp finished but did not produce a JSON transcript.")

    segments = parse_whisper_json(json_path)
    result = {
        "video_id": video_id,
        "engine": "whisper.cpp",
        "audio_file": str(wav_path),
        "segments": segments,
    }
    (output_dir / "transcript.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
