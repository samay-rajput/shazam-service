from peak_picking import find_peaks

def generate_landmarks(audio_path, fanout=5, max_dt=2.0):
    # print("Landmark generation started", flush=True)

    peaks = find_peaks(audio_path)

    print(f"Peaks found: {len(peaks)}", flush=True)

    """
    Generate landmark pairs from peaks.

    Parameters:
        peaks (list): [(time_sec, freq_hz), ...]
        fanout (int): number of target peaks per anchor
        max_dt (float): maximum time difference in seconds

    Returns:
        landmarks (list): [(f1, f2, delta_t), ...]
    """

    # Sort peaks by time
    peaks = sorted(peaks, key=lambda x: x[0])

    landmarks = []

    for i, (t1, f1) in enumerate(peaks):
        targets = 0

        for j in range(i + 1, len(peaks)):
            t2, f2 = peaks[j]
            dt = t2 - t1

            if dt <= 0:
                continue
            if dt > max_dt:
                break

            landmarks.append((f1, f2, dt, t1))
            targets += 1

            if targets >= fanout:
                break

    print("landmarks are generated!")

    return landmarks
