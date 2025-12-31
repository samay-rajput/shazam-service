import os
from time_offset_approach.core.landmark_generation import generate_landmarks
from time_offset_approach.core.matching import build_index, match_landmarks

# -------------------------------
# CONFIG
# -------------------------------
DB_DIR = "../chromaprint approach/known_songs"      # directory with known songs
QUERY_AUDIO = "../chromaprint approach/evaluation/Killa Klassic/concertKillaKlassic.mp3"

# MATCH_THRESHOLD = 200    # tune later

# -------------------------------
# STEP 1: Build DB indexes
# -------------------------------
print("Indexing database songs...")

db_indexes = {}   # song_name -> inverted index

for filename in os.listdir(DB_DIR):
    if not filename.lower().endswith(".mp3"):
        continue

    song_path = os.path.join(DB_DIR, filename)
    print(f"Processing {filename}...")

    landmarks = generate_landmarks(song_path)
    index = build_index(landmarks)

    db_indexes[filename] = index

print("Database indexing complete.\n")


# -------------------------------
# STEP 2: Generate query landmarks
# -------------------------------
print("Generating query landmarks...")
query_landmarks = generate_landmarks(QUERY_AUDIO)
print("Query landmarks:", len(query_landmarks), "\n")


# -------------------------------
# STEP 3: Match query against each song
# -------------------------------
results = []

for song_name, db_index in db_indexes.items():
    offset_votes = match_landmarks(query_landmarks, db_index)

    if not offset_votes:
        best_votes = 0
        best_offset = None
    else:
        best_offset, best_votes = offset_votes.most_common(1)[0]

    results.append((song_name, best_votes, best_offset))


# -------------------------------
# STEP 4: Decide best match
# -------------------------------
results.sort(key=lambda x: x[1], reverse=True)

print("Match results:")
for song, votes, offset in results:
    print(f"{song:20s} | votes = {votes:4d} | offset = {offset}")

best_song, best_votes, best_offset = results[0]

print("\nFINAL DECISION:")

# if best_votes >= MATCH_THRESHOLD:
#     print(f"MATCH FOUND → {best_song}")
#     print(f"Offset ≈ {best_offset} seconds")
# else:
#     print("NO MATCH FOUND")

print(f"MATCH FOUND → {best_song}")
print(f"Offset ≈ {best_offset} seconds")
