import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from audio.tts import generate_name_clips
from audio.cache import get_player, save_player

router = APIRouter()


class PlayerCreate(BaseModel):
    first_name: str
    last_name: str
    preferred_callout: str | None = None
    pronunciation_hint: str | None = None


@router.post("/")
async def create_player(body: PlayerCreate):
    player_id = f"player_{uuid.uuid4().hex[:8]}"
    callout = body.preferred_callout or body.last_name

    clips = await generate_name_clips(
        player_id=player_id,
        full_name=f"{body.first_name} {body.last_name}",
        callout=callout,
        pronunciation_hint=body.pronunciation_hint,
    )

    player = {
        "player_id": player_id,
        "first_name": body.first_name,
        "last_name": body.last_name,
        "display_name": f"{body.first_name} {body.last_name}",
        "preferred_callout": callout,
        "pronunciation_hint": body.pronunciation_hint,
        "clips": clips,
    }
    save_player(player_id, player)
    return player


@router.get("/{player_id}")
def get_player_route(player_id: str):
    player = get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
