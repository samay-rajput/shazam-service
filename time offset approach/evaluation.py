import os
from landmark_generation import generate_landmarks
from matching import build_index, match_landmarks

#config
KNOWN_SONGS_DIR = "../chromaprint approach/known_songs"
EVAL_DIR = "../chromaprint approach/evaluation"

# MATCH_THRESHOLD = 200   # tune later


#loading the known songs
print("Indexing known songs...")

db_indexes = {}   # song_name -> inverted index

for filename in os.listdir(KNOWN_SONGS_DIR):
    if not filename.lower().endswith((".wav", ".mp3", ".m4a")):
        continue

    song_name = os.path.splitext(filename)[0]
    song_path = os.path.join(KNOWN_SONGS_DIR, filename)

    print(f"Indexing {song_name}...")
    landmarks = generate_landmarks(song_path)
    index = build_index(landmarks)

    db_indexes[song_name] = index

print("Indexing complete.\n")


#final evaluation
total_queries = 0
true_positives = 0
false_positives = 0
false_negatives = 0

print("Starting evaluation...\n")

for true_song in os.listdir(EVAL_DIR):
    true_song_dir = os.path.join(EVAL_DIR, true_song)

    if not os.path.isdir(true_song_dir):
        continue

    for query_file in os.listdir(true_song_dir):
        if not query_file.lower().endswith((".wav", ".mp3", "m4a")):
            continue

        query_path = os.path.join(true_song_dir, query_file)
        total_queries += 1

        print(f"Query: {query_file} (GT = {true_song})")

        query_landmarks = generate_landmarks(query_path)

        best_song = None
        best_votes = 0

        for song_name, db_index in db_indexes.items():
            offset_votes = match_landmarks(query_landmarks, db_index)

            if not offset_votes:
                continue

            _, votes = offset_votes.most_common(1)[0]

            if votes > best_votes:
                best_votes = votes
                best_song = song_name

        # decision for logic.
        # if best_song is None or best_votes < MATCH_THRESHOLD:
        #     print("  → NO MATCH")
        #     false_negatives += 1

        if best_song == true_song:
            print(f"  → CORRECT MATCH ({best_song}, votes={best_votes})")
            true_positives += 1

        else:
            print(f"  → WRONG MATCH (pred={best_song}, votes={best_votes})")
            false_positives += 1

        print()

# ----------------------------------
# STEP 3: Metrics
# ----------------------------------
accuracy = true_positives / total_queries if total_queries > 0 else 0

print("========== FINAL RESULTS ==========")
print(f"Total queries     : {total_queries}")
print(f"True Positives    : {true_positives}")
print(f"False Positives   : {false_positives}")
print(f"False Negatives   : {false_negatives}")
print(f"Accuracy          : {accuracy:.3f}")
