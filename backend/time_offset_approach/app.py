from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Form
import tempfile, os, subprocess

from match_from_db import identify_song
from db import songs_col
from index_to_db import index_song
from spotify_search import search_spotify, parse_spotify_results

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/identify")
async def identify(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    MAX_FILE_SIZE = 13 * 1024 * 1024  # 13 MB hard limit

    # read file once
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Audio file too large")

    tmp_path = None
    wav_path = None

    try:
        # save to /tmp explicitly (important on Render)
        suffix = os.path.splitext(file.filename)[1] or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
            tmp_path = tmp.name
            tmp.write(contents)

        # convert to small WAV (downsampled)
        wav_path = tmp_path + ".wav"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", tmp_path,
                "-ac", "1",        # mono
                "-ar", "22050",    # downsample
                wav_path
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        # fingerprint & identify
        song_id, votes, status = identify_song(wav_path)

    finally:
        # defensive cleanup
        for p in (tmp_path, wav_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    # lookup song metadata
    song = songs_col.find_one(
        {"song_id": str(song_id)},
        {"_id": 0, "song_id": 0}
    )

    if song:
        return dict(song)

    return {
        "status": "No Match",
        "reason": status
    }


@app.post("/upload")
async def upload_song(
    file: UploadFile = File(...),
    song_title: str = Form(...),
    artist_name: str | None = Form(None)
):
    """
    Upload a new song and index it into the fingerprint database.
    artist_name is optional for backward compatibility.
    """

    # basic validations
    if not file.filename:
        raise HTTPException(status_code=400, detail="No audio file uploaded")

    if not song_title.strip():
        raise HTTPException(status_code=400, detail="song_title is required")

    # Normalize values
    song_title = song_title.strip()
    artist_name = artist_name.strip() if artist_name else None

    # build query safely
    query = song_title if not artist_name else f"{song_title} {artist_name}"
    data = search_spotify(query)
    song_metadata = parse_spotify_results(data)

    if not song_metadata:
        raise HTTPException(status_code=404, detail="No Spotify match found")

    song_id = song_metadata[0]['id']
    spotify_url = f"https://open.spotify.com/track/{song_id}"
    song_name = song_metadata[0]['name']
    cover_art = song_metadata[0]['cover_art']
    album_name = song_metadata[0]['album']
    album_url = f"https://open.spotify.com/album/{song_metadata[0]['album_id']}"
    artists = song_metadata[0]['artists']

    # duplicate check
    existing_song = songs_col.find_one({"song_id": song_id})
    if existing_song:
        raise HTTPException(
            status_code=409,
            detail="Song already exists in database"
        )

    # saving uploaded file
    contents = await file.read()
    MAX_FILE_SIZE = 13 * 1024 * 1024  # 13 MB
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    tmp_path = None
    wav_path = None

    try:
        suffix = os.path.splitext(file.filename)[1] or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
            tmp_path = tmp.name
            tmp.write(contents)

        # to .wav
        wav_path = tmp_path + ".wav"
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_path, "-ac", "1", "-ar", "22050", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        # storing fingerprint
        index_song(wav_path, song_id)

        # Store metadata
        songs_col.insert_one({
            "song_id": song_id,
            "title": song_name,
            "artist": artists,
            "spotify_url": spotify_url,
            "cover_art": cover_art,
            "album_url": album_url,
            "album_name": album_name
        })

    finally:
        # cleanup
        for p in (tmp_path, wav_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    # response
    return {
        "status": "indexed",
        "song_title": song_name,
        "artists": artists
    }