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


def build_star_windows(
    timeline: list[dict],
    gap_seconds: float = 3.0,
    max_window_seconds: float = 6.0,
) -> list[dict]:
    windows: list[dict] = []
    current: dict | None = None

    for item in timeline:
        if not item.get("detected"):
            continue

        time = float(item["time"])
        confidence = float((item.get("star") or {}).get("confidence") or 0)
        anchor = item.get("player_anchor") or {}

        anchor_x = float(anchor.get("x") or 0)
        anchor_y = float(anchor.get("y") or 0)

        current_duration = time - current["start"] if current else 0
        should_start_window = (
            current is None
            or time - current["end"] > gap_seconds
            or current_duration >= max_window_seconds
        )

        if should_start_window:
            current = {
                "start": time,
                "end": time,
                "samples": 0,
                "confidence_total": 0.0,
                "x_total": 0.0,
                "y_total": 0.0,
                "points": [],
            }
            windows.append(current)

        current["end"] = time
        current["samples"] += 1
        current["confidence_total"] += confidence
        current["x_total"] += anchor_x
        current["y_total"] += anchor_y
        current["points"].append({"time": time, "x": anchor_x, "y": anchor_y})

    normalized = []
    for window in windows:
        samples = max(window["samples"], 1)
        duration = window["end"] - window["start"]
        activity = classify_activity(window["points"], window["end"] - window["start"])
        normalized.append({
            "start": round(window["start"], 2),
            "end": round(window["end"], 2),
            "duration": round(duration, 2),
            "samples": window["samples"],
            "confidence": round(window["confidence_total"] / samples, 2),
            "activity": activity,
            "player_anchor": {
                "x": round(window["x_total"] / samples),
                "y": round(window["y_total"] / samples),
            },
        })
    return normalized


def classify_activity(points: list[dict], duration: float) -> dict:
    if len(points) < 2 or duration <= 0:
        return {
            "type": "located",
            "label": "player located",
            "detail": "The marker is visible, but there is not enough motion to classify the action.",
        }

    total_distance = 0.0
    net_x = points[-1]["x"] - points[0]["x"]
    net_y = points[-1]["y"] - points[0]["y"]
    for previous, current in zip(points, points[1:]):
        dx = current["x"] - previous["x"]
        dy = current["y"] - previous["y"]
        total_distance += (dx * dx + dy * dy) ** 0.5

    speed = total_distance / duration
    horizontal_bias = abs(net_x) - abs(net_y)

    if speed >= 95:
        return {
            "type": "driving_run",
            "label": "driving run",
            "detail": "The controlled player is moving quickly through the phase of play.",
        }
    if speed >= 45 and horizontal_bias > 20:
        return {
            "type": "wide_movement",
            "label": "wide movement",
            "detail": "The controlled player is shifting laterally across the pitch.",
        }
    if speed >= 35:
        return {
            "type": "moving_into_space",
            "label": "moving into space",
            "detail": "The controlled player is active and changing position.",
        }
    if duration >= 8:
        return {
            "type": "sustained_involvement",
            "label": "sustained involvement",
            "detail": "The controlled player stays involved for an extended spell.",
        }
    return {
        "type": "holding_position",
        "label": "holding position",
        "detail": "The controlled player is visible but moving only slightly.",
    }


def line_for_window(index: int, window: dict, player: dict) -> tuple[str, str]:
    display = player["display_name"]
    spoken = spoken_player_name(player)
    activity_type = window["activity"]["type"]

    if index == 0:
        if activity_type == "driving_run":
            return (
                f"{display} bursts into the action early, carrying the play forward with real purpose.",
                f"{spoken} bursts into the action early, carrying the play forward with real purpose.",
            )
        return (
            f"{display} is getting involved early, trying to find space and influence the game.",
            f"{spoken} is getting involved early, trying to find space and influence the game.",
        )
    if activity_type == "driving_run":
        return (
            f"{display} is on the move here, driving forward and asking questions of the defence.",
            f"{spoken} is on the move here, driving forward and asking questions of the defence.",
        )
    if activity_type == "wide_movement":
        return (
            f"{display} drifts across the pitch, looking for a better angle to open the play up.",
            f"{spoken} drifts across the pitch, looking for a better angle to open the play up.",
        )
    if activity_type == "moving_into_space":
        return (
            f"Good movement from {display}, always trying to make himself available.",
            f"Good movement from {spoken}, always trying to make himself available.",
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
        clip_key = (
            f"{video_id}_cue_{index + 1:02d}_"
            f"{window['activity']['type']}_{str(window['start']).replace('.', '_')}"
        )
        clip_path = await generate_commentary_clip(
            player_id=player_id,
            template_id=clip_key,
            text=spoken_line,
            style="neutral",
            output_dir=output_dir,
        )
        cues.append({
            "cue_id": f"cue_{index + 1:02d}",
            "start": window["start"],
            "end": window["end"],
            "confidence": window["confidence"],
            "activity": window["activity"],
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
