import numpy as np
import librosa
from scipy.ndimage import maximum_filter
from .spectogram import plot_spectogram

def find_peaks(
    audio_path, 
    n_fft=2048, 
    hop_length=512,
    neighborhood_size=15,
    threshold_db=-40
):
    S_db, sr = plot_spectogram(audio_path)
    """
    Detect spectral peaks from a spectrogram.
    Returns:
        peaks (list of tuples): [(time_sec, freq_hz), ...]
    """
    #sparsity check!
    local_max = maximum_filter(S_db, size=neighborhood_size) == S_db

    #loud value check!
    peaks_mask = local_max & (S_db > threshold_db)

    freq_idxs, time_idxs = np.where(peaks_mask)

    # convert indices to real units
    times = librosa.frames_to_time(time_idxs, sr=sr, hop_length=hop_length)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)[freq_idxs]

    # listOf (time, freq)
    peaks = list(zip(times, freqs))

    return peaks


if __name__ == "__main__": 
    plot_spectogram("../chromaprint approach/evaluation/Killa Klassic/concertKillaKlassic.mp3")