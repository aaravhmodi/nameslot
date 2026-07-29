import os
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import save

STORAGE = Path(__file__).parent.parent.parent / "storage" / "generated_names"
FINAL_OUTPUTS = Path(__file__).parent.parent.parent / "storage" / "final_outputs"
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing ELEVENLABS_API_KEY in backend/.env")
if not VOICE_ID:
    raise RuntimeError("Missing ELEVENLABS_VOICE_ID in backend/.env")

client = ElevenLabs(api_key=API_KEY)

VARIANTS = {
    "full_neutral": ("{full_name}", "neutral"),
    "last_neutral": ("{callout}", "neutral"),
    "last_excited": ("{callout}!", "excited"),
    "goal_call": ("{callout}!", "dramatic"),
}

STYLE_SETTINGS = {
    "neutral": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0},
    "excited": {"stability": 0.35, "similarity_boost": 0.75, "style": 0.6},
    "dramatic": {"stability": 0.20, "similarity_boost": 0.75, "style": 0.9},
}


async def generate_name_clips(
    player_id: str,
    full_name: str,
    callout: str,
    pronunciation_hint: str | None,
) -> dict[str, str]:
    out_dir = STORAGE / player_id
    out_dir.mkdir(parents=True, exist_ok=True)

    clips: dict[str, str] = {}
    spoken_callout = pronunciation_hint or callout
    spoken_full_name = full_name
    if pronunciation_hint and full_name.endswith(callout):
        spoken_full_name = f"{full_name[: -len(callout)].rstrip()} {pronunciation_hint}"

    for variant_key, (text_template, style) in VARIANTS.items():
        text = text_template.format(full_name=spoken_full_name, callout=spoken_callout)

        settings = STYLE_SETTINGS[style]
        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=settings,
            output_format="mp3_44100_128",
        )

        out_path = out_dir / f"{variant_key}.mp3"
        save(audio, str(out_path))
        clips[variant_key] = str(out_path)

    return clips


async def generate_commentary_clip(
    player_id: str,
    template_id: str,
    text: str,
    style: str,
    output_dir: Path | None = None,
) -> Path:
    target_dir = output_dir or FINAL_OUTPUTS
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / f"{player_id}_{template_id}.mp3"
    if out_path.exists():
        return out_path

    settings = STYLE_SETTINGS[style]
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=settings,
        output_format="mp3_44100_128",
    )

    save(audio, str(out_path))
    return out_path
