import os
from db import songs_col, fingerprints_col
from landmark_generation import generate_landmarks
from hashing import hash_landmark

# SONGS_DIR = "../chromaprint approach/known_songs"

def index_song(song_path, song_id):
    landmarks = generate_landmarks(song_path)

    docs = []
    for f1, f2, dt, t_anchor in landmarks:
        h = hash_landmark(f1, f2, dt)
        docs.append({
            "hash": f"{h[0]}_{h[1]}_{h[2]}",
            "song_id": song_id,
            "t_anchor": t_anchor
        })

    if docs:
        fingerprints_col.insert_many(docs)


if __name__ == "__main__":

    """
    below is the previously sotred song metadata schema
    songs_col.update_one(
            {"song_id": song_id},
            {"$set": {"song_id": song_id}},
            upsert=True
        )

    ---new change--- 
    adding artist names 
    """

    # hence mainly using the /upload endpoint for uploading hence now dropping the songs_col and fingerprint_col.!
    """
    fingerprints_col.drop()
    songs_col.delete_many({})
    """
    #next step: will store the data from the /upload endpoint


    #print the db files.
    songs = songs_col.find_one({'song_id':"2QWFMlyKOlW3LTjv2GFXnG"}, {})

    print(songs)
    