import random
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from audio.cache import get_player
from audio.tts import generate_commentary_clip
from data.templates import load_templates

router = APIRouter()

_recently_used: list[str] = []


class EventTrigger(BaseModel):
    player_id: str
    event_id: str
    intensity: str = "medium"


TOKEN_TO_PLAYER_FIELD = {
    "FULL_NEUTRAL": "display_name",
    "LAST_NEUTRAL": "preferred_callout",
    "LAST_EXCITED": "preferred_callout",
    "GOAL_CALL": "display_name",
}

VARIANT_STYLE = {
    "full_neutral": "neutral",
    "last_neutral": "neutral",
    "last_excited": "excited",
    "goal_call": "dramatic",
}


def render_line(template: str, player: dict, spoken: bool = False) -> str:
    line = template
    spoken_callout = player.get("pronunciation_hint") or player["preferred_callout"]
    spoken_full = player["display_name"]
    if player.get("pronunciation_hint") and spoken_full.endswith(player["last_name"]):
        spoken_full = f"{player['first_name']} {player['pronunciation_hint']}"

    for token, field in TOKEN_TO_PLAYER_FIELD.items():
        if spoken:
            value = spoken_full if token in ("FULL_NEUTRAL", "GOAL_CALL") else spoken_callout
        else:
            value = player[field]
        line = line.replace(f"{{{token}}}", value)
    return line


@router.post("/trigger")
async def trigger_event(body: EventTrigger):
    player = get_player(body.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    templates = load_templates()
    candidates = [
        t for t in templates
        if t["event_id"] == body.event_id and t["intensity"] == body.intensity
    ]
    if not candidates:
        candidates = [t for t in templates if t["event_id"] == body.event_id]
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No templates for event {body.event_id}")

    fresh = [t for t in candidates if t["template_id"] not in _recently_used]
    chosen = random.choice(fresh if fresh else candidates)

    _recently_used.append(chosen["template_id"])
    if len(_recently_used) > 5:
        _recently_used.pop(0)

    variant = chosen["name_variant"]
    clip_path = player["clips"].get(variant)
    if not clip_path:
        raise HTTPException(status_code=422, detail=f"Missing clip variant: {variant}")

    display_line = render_line(chosen["text_preview"], player)
    spoken_line = render_line(chosen["text_preview"], player, spoken=True)
    output_path = await generate_commentary_clip(
        player_id=body.player_id,
        template_id=chosen["template_id"],
        text=spoken_line,
        style=VARIANT_STYLE.get(variant, "neutral"),
    )

    return {
        "template_id": chosen["template_id"],
        "text_preview": display_line,
        "audio_url": f"/audio/final/{output_path.name}",
    }
