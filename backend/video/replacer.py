import json
import subprocess
from pathlib import Path

from audio.tts import generate_commentary_clip
from video.analyzer import ANALYSIS
from video.renderer import find_video_file, require_ffmpeg


async def replace_commentary_phrase(
    video_id: str,
    player_id: str,
    start: float,
    end: float,
    replacement_text: str,
    padding_seconds: float = 2.0,
) -> dict:
    if end <= start:
        raise ValueError("Replacement end time must be after start time")
    if not replacement_text.strip():
        raise ValueError("Replacement text is required")

    ffmpeg = require_ffmpeg()
    source_video = find_video_file(video_id)
    output_dir = ANALYSIS / video_id / "replacements"
    output_dir.mkdir(parents=True, exist_ok=True)

    clip_start = max(start - padding_seconds, 0)
    local_start = start - clip_start
    local_end = end - clip_start
    clip_duration = max((end - start) + padding_seconds * 2, 4)
    cue_key = f"{video_id}_replace_{str(start).replace('.', '_')}_{str(end).replace('.', '_')}"

    voice_path = await generate_commentary_clip(
        player_id=player_id,
        template_id=cue_key,
        text=replacement_text.strip(),
        style="neutral",
        output_dir=output_dir,
    )

    out_name = f"replace_{str(start).replace('.', '_')}_{str(end).replace('.', '_')}.mp4"
    out_path = output_dir / out_name
    delay_ms = round(local_start * 1000)

    filter_complex = (
        f"[0:a]volume='if(between(t,{local_start:.2f},{local_end:.2f}),0.08,0.45)'[game];"
        f"[1:a]adelay={delay_ms}|{delay_ms},volume=1.25[voice];"
        "[game][voice]amix=inputs=2:duration=first:dropout_transition=0[aout]"
    )

    command = [
        ffmpeg,
        "-y",
        "-ss",
        f"{clip_start:.2f}",
        "-t",
        f"{clip_duration:.2f}",
        "-i",
        str(source_video),
        "-i",
        str(voice_path),
        "-filter_complex",
        filter_complex,
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
        raise RuntimeError(f"FFmpeg failed while replacing commentary phrase: {completed.stderr[-500:]}")

    result = {
        "video_id": video_id,
        "player_id": player_id,
        "start": start,
        "end": end,
        "replacement_text": replacement_text.strip(),
        "file": out_name,
        "video_url": f"/video/replacement/{video_id}/{out_name}",
        "audio_url": f"/video/replacement-audio/{video_id}/{voice_path.name}",
    }
    (output_dir / "last_replacement.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
