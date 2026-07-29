import json
from pathlib import Path

from audio.cache import get_player
from audio.tts import generate_commentary_clip
from video.analyzer import ANALYSIS


def load_analysis(video_id: str) -> dict:
    path = ANALYSIS / video_id / "analysis.json"
    if not path.exists():
        raise ValueError("Analysis not found")
    return json.loads(path.read_text(encoding="utf-8"))


def spoken_player_name(player: dict) -> str:
    hint = player.get("pronunciation_hint")
    if hint:
        return f"{player['first_name']} {hint}"
    return player["display_name"]


def build_star_windows(timeline: list[dict], gap_seconds: float = 3.0) -> list[dict]:
    windows: list[dict] = []
    current: dict | None = None

    for item in timeline:
        if not item.get("detected"):
            continue

        time = float(item["time"])
        confidence = float((item.get("star") or {}).get("confidence") or 0)
        anchor = item.get("player_anchor") or {}

        if current is None or time - current["end"] > gap_seconds:
            current = {
                "start": time,
                "end": time,
                "samples": 0,
                "confidence_total": 0.0,
                "x_total": 0.0,
                "y_total": 0.0,
            }
            windows.append(current)

        current["end"] = time
        current["samples"] += 1
        current["confidence_total"] += confidence
        current["x_total"] += float(anchor.get("x") or 0)
        current["y_total"] += float(anchor.get("y") or 0)

    normalized = []
    for window in windows:
        samples = max(window["samples"], 1)
        duration = window["end"] - window["start"]
        normalized.append({
            "start": round(window["start"], 2),
            "end": round(window["end"], 2),
            "duration": round(duration, 2),
            "samples": window["samples"],
            "confidence": round(window["confidence_total"] / samples, 2),
            "player_anchor": {
                "x": round(window["x_total"] / samples),
                "y": round(window["y_total"] / samples),
            },
        })
    return normalized


def line_for_window(index: int, window: dict, player: dict) -> tuple[str, str]:
    display = player["display_name"]
    spoken = spoken_player_name(player)

    if index == 0:
        return (
            f"{display} is getting involved early, looking sharp whenever the ball comes near.",
            f"{spoken} is getting involved early, looking sharp whenever the ball comes near.",
        )
    if window["duration"] >= 8:
        return (
            f"{display} stays right in the middle of the action, demanding the ball and keeping the move alive.",
            f"{spoken} stays right in the middle of the action, demanding the ball and keeping the move alive.",
        )
    if window["confidence"] >= 0.95:
        return (
            f"There's {display}, picked out clearly as the play develops.",
            f"There's {spoken}, picked out clearly as the play develops.",
        )
    return (
        f"{display} is nearby, trying to influence this phase of play.",
        f"{spoken} is nearby, trying to influence this phase of play.",
    )


async def generate_video_commentary(video_id: str, player_id: str, max_cues: int = 8) -> dict:
    analysis = load_analysis(video_id)
    player = get_player(player_id)
    if not player:
        raise ValueError("Player not found")

    windows = build_star_windows(analysis["timeline"])
    cues = []
    output_dir = ANALYSIS / video_id / "commentary"

    for index, window in enumerate(windows[:max_cues]):
        display_line, spoken_line = line_for_window(index, window, player)
        clip_path = await generate_commentary_clip(
            player_id=player_id,
            template_id=f"{video_id}_cue_{index + 1:02d}",
            text=spoken_line,
            style="neutral",
            output_dir=output_dir,
        )
        cues.append({
            "cue_id": f"cue_{index + 1:02d}",
            "start": window["start"],
            "end": window["end"],
            "confidence": window["confidence"],
            "text": display_line,
            "spoken_text": spoken_line,
            "audio_url": f"/video/commentary/{video_id}/{clip_path.name}",
        })

    result = {
        "video_id": video_id,
        "player_id": player_id,
        "player_name": player["display_name"],
        "cues": cues,
    }
    (ANALYSIS / video_id / "commentary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
