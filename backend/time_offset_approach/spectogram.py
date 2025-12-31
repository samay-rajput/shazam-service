import numpy as np
import soundfile as sf

# Load one audio file
def plot_spectogram(audio_path):
    y, sr = sf.read(audio_path)

    # convert to mono if stereo
    if y.ndim > 1:
        y = np.mean(y, axis=1)

    print("Duration (sec):", len(y) / sr)
    print("Sample rate:", sr)

    # Compute spectrogram
    n_fft = 2048
    hop_length = 512

    # frame the signal
    frames = []
    for i in range(0, len(y) - n_fft, hop_length):
        frames.append(y[i : i + n_fft])

    frames = np.array(frames)

    # apply FFT
    S = np.abs(np.fft.rfft(frames, axis=1)).T  # freq x time

    # converted into the db
    S_db = 20 * np.log10(S + 1e-10)  # avoid log(0)

    return S_db, sr


if __name__ == "__main__":
    y, sr = plot_spectogram("../chromaprint approach/evaluation/Killa Klassic/concertKillaKlassic.mp3")
    print(y)
