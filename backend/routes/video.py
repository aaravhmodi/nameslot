from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from video.analyzer import STORAGE, analyze_star_timeline, save_upload
from video.commentary import ANALYSIS, generate_video_commentary

router = APIRouter()


class CommentaryRequest(BaseModel):
    player_id: str
    max_cues: int = 8


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


@router.post("/{video_id}/commentary")
async def create_video_commentary(video_id: str, body: CommentaryRequest):
    try:
        return await generate_video_commentary(video_id, body.player_id, body.max_cues)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/commentary/{video_id}/{filename}")
def get_commentary_clip(video_id: str, filename: str):
    path = ANALYSIS / video_id / "commentary" / filename
    if Path(filename).name != filename or not path.exists() or path.suffix.lower() != ".mp3":
        raise HTTPException(status_code=404, detail="Commentary clip not found")
    return FileResponse(path, media_type="audio/mpeg")
