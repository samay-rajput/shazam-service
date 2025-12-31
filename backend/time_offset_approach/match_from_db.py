from collections import defaultdict
from db import fingerprints_col
from landmark_generation import generate_landmarks
from hashing import hash_landmark

MAX_DB_MATCHES_PER_HASH = 50
MIN_VOTES_TO_KEEP = 10
OFFSET_ROUND = 2

def identify_song(query_audio, min_vote_threshold=100, ratio_threshold=2.5):
    query_landmarks = generate_landmarks(query_audio)

    # 1. Group & deduplicate query hashes
    query_hash_map = defaultdict(set)
    for f1, f2, dt, t_query in query_landmarks:
        h = hash_landmark(f1, f2, dt)
        h_str = f"{h[0]}_{h[1]}_{h[2]}"
        query_hash_map[h_str].add(round(t_query, OFFSET_ROUND))

    votes = defaultdict(lambda: defaultdict(int))

    # 2. Batch DB lookup per hash
    # for h_str, t_queries in query_hash_map.items():
    #     matches = fingerprints_col.find(
    #         { "hash": h_str },
    #         { "song_id": 1, "t_anchor": 1, "_id": 0 }
    #     ).limit(MAX_DB_MATCHES_PER_HASH)

    #     for m in matches:
    #         song_id = m["song_id"]
    #         t_db = m["t_anchor"]

    #         for t_query in t_queries:
    #             offset = round(t_query - t_db, OFFSET_ROUND)
    #             votes[song_id][offset] += 1

    all_hashes = list(query_hash_map.keys())

    # db lookup (only one queryy to  get all the hashes).
    cursor = fingerprints_col.find(
        { "hash": { "$in": all_hashes } },
        { "hash": 1, "song_id": 1, "t_anchor": 1, "_id": 0 }
    )

    for m in cursor:
        h_str = m["hash"]
        song_id = m["song_id"]
        t_db = m["t_anchor"]

        for t_query in query_hash_map[h_str]:
            offset = round(t_query - t_db, OFFSET_ROUND)
            votes[song_id][offset] += 1


    # decide best song
    best_id, best_votes, best_offset = None, 0, None

    second_best_votes = 0
    for song_id, offset_map in votes.items():
        local_best_offset = max(offset_map, key=offset_map.get)
        local_best_votes = offset_map[local_best_offset]

        if local_best_votes > best_votes:
            best_id = song_id
            second_best_votes = best_votes
            best_votes = local_best_votes
            # best_offset = local_best_offset

    
    if second_best_votes > 0 and best_votes/second_best_votes < ratio_threshold:
        return None, best_votes, "Song Not in DB"

    if best_votes < min_vote_threshold:
        return None , best_votes, "LOW CONFIDENCE"
    return best_id, best_votes, "MATCHED!"


if __name__ == "__main__":
    print("Starting identification...", flush=True)
    audio_path = "../chromaprint_approach/evaluation/REd/highVolumeRed.m4a"

    id, votes, status = identify_song(audio_path)
    print(type(id))
    print(str(id))

    