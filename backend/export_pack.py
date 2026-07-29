import csv
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from audio.cache import get_player

ROOT = Path(__file__).parent.parent
STORAGE = ROOT / "storage"
EXPORTS = ROOT / "exports"


def slugify(value: str) -> str:
    keep = []
    for char in value.lower():
        if char.isalnum():
            keep.append(char)
        elif char in (" ", "-", "_"):
            keep.append("_")
    return "_".join("".join(keep).split("_")).strip("_") or "player"


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def copy_clip(source: Path, destination: Path) -> Path | None:
    if not source.exists():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def write_manifest(pack_dir: Path, rows: list[dict[str, str]]) -> None:
    manifest_path = pack_dir / "manifest.csv"
    fieldnames = [
        "player_id",
        "player_name",
        "clip_type",
        "event_or_variant",
        "source_file",
        "export_file",
        "format",
        "size_bytes",
        "modding_status",
    ]
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_notes(pack_dir: Path, player: dict, rows: list[dict[str, str]]) -> None:
    notes = f"""# EA FC Commentary Export Pack

Player: {player["display_name"]}
Player ID: {player["player_id"]}
Preferred callout: {player["preferred_callout"]}
Pronunciation hint: {player.get("pronunciation_hint") or ""}

## What this pack contains

- `audio/names/`: generated player-name clips.
- `audio/events/`: generated full commentary event clips.
- `manifest.csv`: local file map for FIFA Editor Tool / RDBM work.

## Local EA FC integration path

1. Keep this pack as the clean source of generated clips.
2. Open the target EA FC/FIFA game in FIFA Editor Tool or a compatible Frostbite editor.
3. Find the English commentary database/assets for your game version.
4. Inspect `fifa_ng.db` tables such as `playernames` and `commentarynames`.
5. Use RDBM or Live Editor to map your created player to a suitable `lastnameid` or `commonnameid`.
6. For true custom audio, import or replace commentary wave assets manually, then test offline.

## Format note

The exported clips are MP3 because that is what the current ElevenLabs generation path
creates. FIFA Editor Tool workflows often expect WAV or game-native wave assets. Install
`ffmpeg` before adding automatic WAV conversion.

## Exported clips

Total clips: {len(rows)}
"""
    (pack_dir / "rdbm-notes.md").write_text(notes, encoding="utf-8")


def zip_pack(pack_dir: Path) -> Path:
    zip_path = pack_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in pack_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(pack_dir.parent))
    return zip_path


def build_eafc_pack(player_id: str) -> dict:
    player = get_player(player_id)
    if not player:
        raise ValueError("Player not found")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pack_name = f"{slugify(player['display_name'])}_{player_id}_{timestamp}"
    pack_dir = EXPORTS / "eafc-commentary-pack" / pack_name
    audio_dir = pack_dir / "audio"
    rows: list[dict[str, str]] = []

    for variant, clip in player.get("clips", {}).items():
        source = Path(clip)
        destination = audio_dir / "names" / f"{variant}{source.suffix}"
        copied = copy_clip(source, destination)
        if copied:
            rows.append({
                "player_id": player_id,
                "player_name": player["display_name"],
                "clip_type": "name",
                "event_or_variant": variant,
                "source_file": relative(source),
                "export_file": relative(copied),
                "format": copied.suffix.lstrip("."),
                "size_bytes": str(copied.stat().st_size),
                "modding_status": "ready_for_manual_mapping",
            })

    for source in sorted((STORAGE / "final_outputs").glob(f"{player_id}_*.mp3")):
        event_name = source.stem.removeprefix(f"{player_id}_")
        destination = audio_dir / "events" / source.name
        copied = copy_clip(source, destination)
        if copied:
            rows.append({
                "player_id": player_id,
                "player_name": player["display_name"],
                "clip_type": "event",
                "event_or_variant": event_name,
                "source_file": relative(source),
                "export_file": relative(copied),
                "format": copied.suffix.lstrip("."),
                "size_bytes": str(copied.stat().st_size),
                "modding_status": "needs_fifa_editor_import",
            })

    write_manifest(pack_dir, rows)
    write_notes(pack_dir, player, rows)
    zip_path = zip_pack(pack_dir)

    return {
        "pack_name": pack_name,
        "pack_path": str(pack_dir),
        "zip_path": str(zip_path),
        "zip_file": zip_path.name,
        "clips_exported": len(rows),
    }
