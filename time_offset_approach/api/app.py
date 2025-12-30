from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile, os, subprocess
from fastapi.params import Form
from time_offset_approach.db.match_from_db import identify_song
from time_offset_approach.db.db import songs_col
from time_offset_approach.db.index_to_db import index_song
from time_offset_approach.integrations.spotify_search import search_spotify , parse_spotify_results

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
        id, votes, status = identify_song(wav_path)
    finally:
        os.remove(tmp_path)
        os.remove(wav_path)

    #find the song with id in songs collection
    song = songs_col.find_one({'song_id': str(id)},{'song_id': 0, '_id': 0})

    if song:
        return dict(song)
    
    return {
        "status" : "No Match", 
        "reason" : status
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

    #basic validations
    if not file.filename:
        raise HTTPException(status_code=400, detail="No audio file uploaded")

    if not song_title.strip():
        raise HTTPException(status_code=400, detail="song_title is required")
    
    # Normalize values
    song_title = song_title.strip()
    artist_name = artist_name.strip() if artist_name else None

    #get the metadata from spotify
    data = search_spotify(song_title + " " + artist_name)
    song_metadata = parse_spotify_results(data)

    song_id = song_metadata[0]['id']
    spotify_url = f"https://open.spotify.com/track/{song_id}"
    song_name = song_metadata[0]['name']
    cover_art = song_metadata[0]['cover_art']
    album_name = song_metadata[0]['album']
    album_url = f"https://open.spotify.com/album/{song_metadata[0]['album_id']}"
    artists = song_metadata[0]['artists']

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
            "title": song_name,
            "artist": artists,
            "spotify_url": spotify_url,
            "cover_art" : cover_art, 
            "album_url": album_url,  
            "album_name": album_name
        })

    finally:
        #cleanup
        os.remove(tmp_path)
        os.remove(wav_path)

    #response
    return {
        "status": "indexed",
        "song_title":song_name,
        "artists": artists
    }
