import os
from db import songs_col, fingerprints_col
from landmark_generation import generate_landmarks
from hashing import hash_landmark

SONGS_DIR = "../chromaprint approach/known_songs"

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
    for filename in os.listdir(SONGS_DIR):
        if not filename.lower().endswith((".wav", ".mp3", ".m4a")):
            continue

        song_id = os.path.splitext(filename)[0]
        song_path = os.path.join(SONGS_DIR, filename)

        print(f"Indexing {song_id}...")

        # store metadata once
        songs_col.update_one(
            {"song_id": song_id},
            {"$set": {"song_id": song_id}},
            upsert=True
        )

        index_song(song_path, song_id)

    print("Indexing complete.")
