from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile, os, subprocess
from fastapi.params import Form
from match_from_db import identify_song
from db import songs_col
from index_to_db import index_song

app = FastAPI(title="Audio Fingerprinting API")



@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/identify")
async def identify(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp_path = tmp.name
        tmp.write(await file.read())

    # convert to wav (important)
    wav_path = tmp_path + ".wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", tmp_path, wav_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        song, votes, offset = identify_song(wav_path)
    finally:
        os.remove(tmp_path)
        os.remove(wav_path)

    if song is None:
        return {
            "match": False,
            "reason": "NO_MATCH"
        }

    return {
        "match": True,
        "song_id": song,
        "votes": votes,
        "offset": offset
    }



@app.post("/upload")
async def upload_song(
    file: UploadFile = File(...),
    song_title: str = Form(...),
    artist_name: str = Form(...)
):
    """
    Upload a new song and index it into the fingerprint database.

    artist_name is optional for backward compatibility.
    """

    #basic validations
    if not file.filename:
        raise HTTPException(status_code=400, detail="No audio file uploaded")

    if not song_title.strip():
        raise HTTPException(status_code=400, detail="song_title is required")

    if not artist_name.strip():
        raise HTTPException(status_code=400, detail="artist_name is required")
    
    # Normalize values
    song_title = song_title.strip()
    artist_name = artist_name.strip() if artist_name else None

    #unique id
    song_id = song_title

    #duplicate check
    existing_song = songs_col.find_one({ "song_id": song_id })
    if existing_song:
        raise HTTPException(
            status_code=409,
            detail="Song already exists in database"
        )

    #saving uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp_path = tmp.name
        tmp.write(await file.read())

    #to .wav
    wav_path = tmp_path + ".wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", tmp_path, wav_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    #storing fingerprint!
    try:
        index_song(wav_path, song_id)

        # Store metadata (artist may be None)
        songs_col.insert_one({
            "song_id": song_id,
            "title": song_title,
            "artist": artist_name
        })

    finally:
        #cleanup
        os.remove(tmp_path)
        os.remove(wav_path)

    #response
    return {
        "status": "indexed",
        "song_id": song_id,
        "title": song_title,
        "artist": artist_name
    }
