import json
from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "players.json"


def _load() -> dict:
    if not CACHE_FILE.exists():
        return {}
    return json.loads(CACHE_FILE.read_text())


def _dump(data: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def save_player(player_id: str, player: dict):
    data = _load()
    data[player_id] = player
    _dump(data)


def get_player(player_id: str) -> dict | None:
    return _load().get(player_id)
