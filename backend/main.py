from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import players, events, audio, exports

app = FastAPI(title="NameSlot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(audio.router, prefix="/audio", tags=["audio"])
app.include_router(exports.router, prefix="/exports", tags=["exports"])


@app.get("/health")
def health():
    return {"status": "ok"}
