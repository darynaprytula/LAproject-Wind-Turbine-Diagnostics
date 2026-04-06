import numpy as np
import matplotlib.pyplot as plt
from features.fft import manual_fft


DARK_BLUE = "#0B3D91"


def amplitude_spectrum(signal, fs):
    """
    Compute the amplitude spectrum of a signal using FFT.

    The function applies manual FFT (via function manual_fft) and converts
    the complex FFT output into a one-sided amplitude spectrum.

    Parameters:
    signal : input discrete-time signal x[n].
    fs(float) : sampling frequency of the signal (in Hz).

    Returns:
    frequencies(list of float) : frequency bins corresponding to the amplitude values (0 to fs/2).
    amplitude(list of float) : one-sided amplitude spectrum values.
    """
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
    """
    Plot the amplitude spectrum of a signal.
    
    The function computes the amplitude spectrum using function amplitude_spectrum
    and visualizes it using Matplotlib.
    
    Parameters:
    signal : input discrete-time signal x[n].
    fs(float) : sampling frequency of the signal (in Hz).
    title(str) : title of the plot (default is "Amplitude Spectrum").
    
    Returns:
    None
    """
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
    """
    Compute and save (or display) the amplitude spectrum plot.
    
    The function computes the amplitude spectrum using function amplitude_spectrum
    and either saves the plot to a file or displays it.
    
    Parameters:
    signal : input discrete-time signal x[n].
    fs(float) : sampling frequency of the signal (in Hz).
    title(str) : title of the plot (default is "Amplitude Spectrum").
    save_path(str or None) : path to save the plot image; if None, the plot is displayed.
    
    Returns:
    None
    """
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
