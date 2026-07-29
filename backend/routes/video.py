from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from video.analyzer import STORAGE, analyze_star_timeline, save_upload

router = APIRouter()


@router.post("/analyze-star")
async def analyze_star(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".mp4", ".mov", ".avi", ".mkv"):
        raise HTTPException(status_code=400, detail="Upload an MP4, MOV, AVI, or MKV gameplay clip.")

    try:
        video_id, video_path = save_upload(file.file, suffix)
        return analyze_star_timeline(video_path, video_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/frame/{path:path}")
def get_frame(path: str):
    frame_path = STORAGE / path
    try:
        frame_path.relative_to(STORAGE)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Frame not found") from exc

    if not frame_path.exists() or frame_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
        raise HTTPException(status_code=404, detail="Frame not found")
    return FileResponse(frame_path, media_type="image/jpeg")
