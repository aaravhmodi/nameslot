from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize

STORAGE = Path(__file__).parent.parent.parent / "storage"
TEMPLATE_DIR = STORAGE / "templates"
OUTPUT_DIR = STORAGE / "final_outputs"


async def stitch_commentary(
    prefix_audio: str | None,
    name_audio: str,
    suffix_audio: str | None,
    template_id: str,
    player_id: str,
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    name_seg = normalize(AudioSegment.from_file(name_audio))

    if prefix_audio and (TEMPLATE_DIR / prefix_audio).exists():
        prefix_seg = normalize(AudioSegment.from_file(TEMPLATE_DIR / prefix_audio))
        result = prefix_seg.append(name_seg, crossfade=40)
    else:
        result = name_seg

    if suffix_audio and (TEMPLATE_DIR / suffix_audio).exists():
        suffix_seg = normalize(AudioSegment.from_file(TEMPLATE_DIR / suffix_audio))
        result = result.append(suffix_seg, crossfade=40)

    out_path = OUTPUT_DIR / f"{player_id}_{template_id}.wav"
    result.export(out_path, format="wav")
    return out_path
