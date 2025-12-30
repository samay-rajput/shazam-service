from landmark_generation import generate_landmarks
from matching import build_index, match_landmarks

# -------------------------------
# PATHS
# -------------------------------
DB_AUDIO = audio_path = "../chromaprint approach/known_songs/That Shit Hard.mp3" 
QUERY_AUDIO = audio_path = "../chromaprint approach/evaluation/Uchhal Matt/noisyUchhalMat.m4a"



# -------------------------------
# STEP 1: Generate landmarks
# -------------------------------
print("Generating DB landmarks...")
db_landmarks = generate_landmarks(DB_AUDIO)

print("Generating QUERY landmarks...")
query_landmarks = generate_landmarks(QUERY_AUDIO)

print("DB landmarks:", len(db_landmarks))
print("Query landmarks:", len(query_landmarks))


# -------------------------------
# STEP 2: Build DB index
# -------------------------------
print("Building inverted index...")
db_index = build_index(db_landmarks)


# -------------------------------
# STEP 3: Match & vote
# -------------------------------
print("Matching and voting...")
offset_votes = match_landmarks(query_landmarks, db_index)


# -------------------------------
# STEP 4: Inspect result
# -------------------------------
print("\nTop offset votes:")
for offset, count in offset_votes.most_common(10):
    print(offset, count)
