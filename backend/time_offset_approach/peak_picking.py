import numpy as np
from spectogram import plot_spectogram


def find_peaks(
    audio_path,
    n_fft=2048,
    hop_length=512,
    neighborhood_size=15,
    threshold_db=-40
):
    """
    Detect spectral peaks from a spectrogram.
    Returns:
        peaks (list of tuples): [(time_sec, freq_hz), ...]
    """

    S_db, sr = plot_spectogram(audio_path)

    # Numpy only
    # A point is a peak if it is greater than all its neighbors
    # in a square neighborhood (approximation of maximum_filter)

    pad = neighborhood_size // 2
    padded = np.pad(S_db, pad_width=pad, mode="constant", constant_values=-np.inf)

    local_max = np.ones_like(S_db, dtype=bool)

    for i in range(-pad, pad + 1):
        for j in range(-pad, pad + 1):
            if i == 0 and j == 0:
                continue
            local_max &= S_db > padded[
                pad + i : pad + i + S_db.shape[0],
                pad + j : pad + j + S_db.shape[1]
            ]

    # loudness thresholding
    peaks_mask = local_max & (S_db > threshold_db)

    # convert indices to time & freq
    freq_idxs, time_idxs = np.where(peaks_mask)

    times = (time_idxs * hop_length) / sr
    freqs = (freq_idxs * sr) / n_fft

    # (time, freq)
    peaks = list(zip(times, freqs))

    return peaks


if __name__ == "__main__":
    plot_spectogram("../chromaprint approach/evaluation/Killa Klassic/concertKillaKlassic.mp3")
