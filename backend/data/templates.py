import json
from pathlib import Path

TEMPLATES_FILE = Path(__file__).parent.parent.parent / "data" / "templates.json"


def load_templates() -> list[dict]:
    return json.loads(TEMPLATES_FILE.read_text())
