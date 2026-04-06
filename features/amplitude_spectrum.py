import numpy as np
import matplotlib.pyplot as plt
from features.fft import manual_fft


DARK_BLUE = "#0B3D91"


def amplitude_spectrum(signal, fs):
    freqs, magnitude, fft_output, signal_pad = manual_fft(signal, fs)

    N = len(signal_pad)

    amplitude = []
    for k in range(N // 2 + 1):
        if k == 0 or k == N // 2:
            amplitude.append(abs(fft_output[k]) / N)
        else:
            amplitude.append(2.0 * abs(fft_output[k]) / N)

    frequencies = [(k * fs) / N for k in range(N // 2 + 1)]

    return frequencies, amplitude


def amplitude_spectrum_plot(signal, fs, title="Amplitude Spectrum"):
    frequencies, amplitude = amplitude_spectrum(signal, fs)

    plt.figure(figsize=(10, 4))
    plt.plot(frequencies, amplitude, color=DARK_BLUE)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title(title)
    plt.xlim(0, fs / 2)
    plt.grid(True)
    plt.show()


def save_amplitude_spectrum_plot(signal, fs, title="Amplitude Spectrum", save_path=None):
    frequencies, amplitude = amplitude_spectrum(signal, fs)

    plt.figure(figsize=(10, 4))
    plt.plot(frequencies, amplitude, color=DARK_BLUE)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title(title)
    plt.xlim(0, fs / 2)
    plt.grid(True)

    if save_path is not None:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
