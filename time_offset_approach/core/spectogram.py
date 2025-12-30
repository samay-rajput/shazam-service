import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# Load one audio file
def plot_spectogram(audio_path): 
    y, sr = librosa.load(audio_path, mono=True)

    print("Duration (sec):", len(y) / sr)
    print("Sample rate:", sr)

    # Compute spectrogram
    S = np.abs(librosa.stft(y))  #returns the 2d array. (freqxtime)

    #converted into the db
    S_db = librosa.amplitude_to_db(S, ref=np.max)

    # Plot
    # plt.figure(figsize=(10, 4))
    # librosa.display.specshow(S_db, sr=sr, x_axis="time", y_axis="hz")
    # plt.colorbar(format="%+2.0f dB")
    # plt.title("Spectrogram")
    # plt.tight_layout()
    # plt.show()

    return S_db, sr

if __name__ == "__main__": 
    y, sr = plot_spectogram("../chromaprint approach/evaluation/Killa Klassic/concertKillaKlassic.mp3")

    print(y)