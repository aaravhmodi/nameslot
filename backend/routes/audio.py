from pathlib import Path
import mimetypes
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

STORAGE = Path(__file__).parent.parent.parent / "storage"


@router.get("/final/{filename}")
def serve_final(filename: str):
    path = STORAGE / "final_outputs" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type)


@router.get("/generated/{player_id}/{filename}")
def serve_generated(player_id: str, filename: str):
    path = STORAGE / "generated_names" / player_id / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type)
