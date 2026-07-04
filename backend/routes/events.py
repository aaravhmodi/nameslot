import random
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from audio.cache import get_player
from audio.stitch import stitch_commentary
from data.templates import load_templates

router = APIRouter()

_recently_used: list[str] = []


class EventTrigger(BaseModel):
    player_id: str
    event_id: str
    intensity: str = "medium"


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

    output_path = await stitch_commentary(
        prefix_audio=chosen.get("prefix_audio"),
        name_audio=clip_path,
        suffix_audio=chosen.get("suffix_audio"),
        template_id=chosen["template_id"],
        player_id=body.player_id,
    )

    return {
        "template_id": chosen["template_id"],
        "text_preview": chosen["text_preview"],
        "audio_url": f"/audio/final/{output_path.name}",
    }
