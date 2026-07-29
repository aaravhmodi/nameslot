# NameSlot

AI-generated custom player-name audio for sports-game commentary.

## Structure

```
nameslot/
  backend/           FastAPI server
    audio/           TTS generation + audio stitching + cache
    routes/          players, events, audio endpoints
    data/            template loader
    main.py
    requirements.txt
    .env.example
  frontend/          Next.js app
    app/
    components/
  data/
    templates.json   Commentary event templates
  storage/
    generated_names/ Cached per-player name clips
    templates/       Prerecorded commentary fragment WAVs
    final_outputs/   Stitched final audio
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env         # fill in your keys
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## FIFA overlay scaffold

The first integration target is an external soundboard overlay:

1. Run the backend and frontend locally.
2. Create a player with a pronunciation hint if needed.
3. Keep the NameSlot Commentary Desk open beside FIFA.
4. Use hotkeys `1`-`8` to trigger event commentary clips.
5. Route browser audio into your capture/game audio stack with a virtual audio device
   such as VB-CABLE or Voicemeeter.

This avoids modifying EA FC game files while the commentary pipeline is still being
tuned. True in-game replacement can be explored later through PC modding tools.

## EA FC mod export scaffold

Use the **Export EA FC pack** button after creating a player and generating any event
clips you want to keep. The backend writes a local pack under:

```text
exports/eafc-commentary-pack/
```

Each pack contains:

```text
audio/names/      Cached player-name clips
audio/events/     Full commentary event clips
manifest.csv      Clip map for manual modding work
rdbm-notes.md     Local notes for FIFA Editor Tool / RDBM mapping
```

The export does not call ElevenLabs. It only packages files that already exist in
`storage/generated_names/` and `storage/final_outputs/`.

## APIs needed

| Service | What for | Tier |
|---------|----------|------|
| **ElevenLabs** | TTS name clip generation | Starter $5/mo |

### ElevenLabs setup
1. Sign up at elevenlabs.io
2. Go to Voices → find or clone a sports-commentator style voice
3. Copy the Voice ID and your API key into `backend/.env`

## Template audio

Event clicks currently generate the full commentary line directly with ElevenLabs using
the selected template text and the player's pronunciation hint.

`storage/templates/` is optional legacy support for prerecorded WAV files used by the
stitching helper. If you use stitched template audio later, install `ffmpeg` first;
without it, `pydub` may not be able to combine MP3/WAV files.

For stitched template audio, generate these yourself with ElevenLabs or any TTS using
the same voice:

| File | Text |
|------|------|
| `what_a_finish_from.wav` | "What a finish from" |
| `incredible_strike_by.wav` | "Incredible strike by" |
| `that_could_be_the_winner.wav` | "That could be the winner!" |
| `is_through_on_goal.wav` | "is through on goal!" |
| `good_effort_from.wav` | "Good effort from" |
| `but_the_keeper_saves_it.wav` | "but the keeper saves it." |
| `brilliant_vision_from.wav` | "Brilliant vision from" |
| `a_late_challenge_there_by.wav` | "A late challenge there by" |
| `and_here_comes.wav` | "And here comes" |
| `a_hat_trick_on_a_night_to_remember.wav` | "A hat trick on a night to remember." |

## Flow

1. User enters a player name
2. Backend calls ElevenLabs → generates 4 name variants (full neutral, last neutral, last excited, goal call)
3. Clips are cached per player
4. User clicks a game event (Goal, Through Ball, etc.)
5. Backend picks a template and generates the full commentary line
6. Frontend plays the final audio
