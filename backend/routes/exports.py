from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from export_pack import EXPORTS, build_eafc_pack

router = APIRouter()


@router.post("/eafc/{player_id}")
def create_eafc_export(player_id: str):
    try:
        return build_eafc_pack(player_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/download/{filename}")
def download_export(filename: str):
    path = EXPORTS / "eafc-commentary-pack" / filename
    if Path(filename).name != filename or path.suffix != ".zip" or not path.exists():
        raise HTTPException(status_code=404, detail="Export not found")
    return FileResponse(path, media_type="application/zip", filename=filename)
