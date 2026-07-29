from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from video.analyzer import STORAGE, analyze_star_timeline, save_upload
from video.commentary import ANALYSIS, generate_video_commentary
from video.replacer import replace_commentary_phrase
from video.renderer import export_proof_clips
from video.transcriber import transcribe_video_with_whisper_cpp

router = APIRouter()


class CommentaryRequest(BaseModel):
    player_id: str
    max_cues: int = 8


class ProofClipRequest(BaseModel):
    padding_seconds: float = 2.0
    max_clips: int = 6


class ReplacePhraseRequest(BaseModel):
    player_id: str
    start: float
    end: float
    replacement_text: str
    padding_seconds: float = 2.0


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


@router.post("/{video_id}/proof-clips")
def create_proof_clips(video_id: str, body: ProofClipRequest):
    try:
        return export_proof_clips(video_id, body.padding_seconds, body.max_clips)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/proof/{video_id}/{filename}")
def get_proof_clip(video_id: str, filename: str):
    path = ANALYSIS / video_id / "proof_clips" / filename
    if Path(filename).name != filename or not path.exists() or path.suffix.lower() != ".mp4":
        raise HTTPException(status_code=404, detail="Proof clip not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)


@router.post("/{video_id}/replace-phrase")
async def create_replacement_clip(video_id: str, body: ReplacePhraseRequest):
    try:
        return await replace_commentary_phrase(
            video_id=video_id,
            player_id=body.player_id,
            start=body.start,
            end=body.end,
            replacement_text=body.replacement_text,
            padding_seconds=body.padding_seconds,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/replacement/{video_id}/{filename}")
def get_replacement_clip(video_id: str, filename: str):
    path = ANALYSIS / video_id / "replacements" / filename
    if Path(filename).name != filename or not path.exists() or path.suffix.lower() != ".mp4":
        raise HTTPException(status_code=404, detail="Replacement clip not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)


@router.get("/replacement-audio/{video_id}/{filename}")
def get_replacement_audio(video_id: str, filename: str):
    path = ANALYSIS / video_id / "replacements" / filename
    if Path(filename).name != filename or not path.exists() or path.suffix.lower() != ".mp3":
        raise HTTPException(status_code=404, detail="Replacement audio not found")
    return FileResponse(path, media_type="audio/mpeg", filename=filename)


@router.post("/{video_id}/transcribe")
def transcribe_video(video_id: str):
    try:
        return transcribe_video_with_whisper_cpp(video_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
