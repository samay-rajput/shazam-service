from collections import defaultdict, Counter
from hashing import hash_landmark

def build_index(landmarks):
    """
    Build an inverted index for a song.

    Parameters:
        landmarks (list):
            [(f1, f2, dt, t_anchor), ...]

    Returns:
        dict:
            hash -> list of anchor times
    """

    index = defaultdict(list)

    for f1, f2, dt, t_anchor in landmarks:
        h = hash_landmark(f1, f2, dt)
        index[h].append(t_anchor)

    return index


def match_landmarks(query_landmarks, db_index):
    """
    Match query landmarks against a database index using time-offset voting.

    Parameters:
        query_landmarks (list):
            [(f1, f2, dt, t_query), ...]
        db_index (dict):
            hash -> list of t_anchor

    Returns:
        Counter:
            offset -> vote count
    """

    offset_votes = Counter()

    for f1, f2, dt, t_query in query_landmarks:
        h = hash_landmark(f1, f2, dt)

        # No similar landmark in DB
        if h not in db_index:
            continue

        # For every place this landmark occurred in DB
        for t_db in db_index[h]:
            offset = round(t_query - t_db, 2)
            offset_votes[offset] += 1

    return offset_votes

