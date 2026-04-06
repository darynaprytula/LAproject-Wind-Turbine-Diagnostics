import numpy as np
import matplotlib.pyplot as plt
import math


DARK_BLUE = "#0B3D91"


def fft(x):
    N = len(x)
    if N <= 1:
        return x

    even = fft(x[0::2])
    odd = fft(x[1::2])

    T = [math.e ** (-2j * math.pi * k / N) * odd[k] for k in range(N // 2)]

    return [even[k] + T[k] for k in range(N // 2)] + \
           [even[k] - T[k] for k in range(N // 2)]


def next_pow2(n):
    p = 1
    while p < n:
        p *= 2
    return p


def manual_fft(signal, fs):
    signal = [float(x) for x in signal]

    N0 = len(signal)
    N = next_pow2(N0)
    signal_pad = signal + [0.0] * (N - N0)

    fft_output = fft(signal_pad)

    freqs = []
    for k in range(N):
        if k < N // 2:
            freqs.append(k * fs / N)
        else:
            freqs.append((k - N) * fs / N)

    magnitude = [abs(fft_output[k]) for k in range(N)]

    return freqs, magnitude, fft_output, signal_pad


def library_fft(signal, fs):
    signal = np.asarray(signal, dtype=float)

    N0 = len(signal)
    N = next_pow2(N0)
    signal_pad = np.pad(signal, (0, N - N0), mode="constant")

    np_fft = np.fft.fft(signal_pad)
    freqs = np.fft.fftfreq(len(signal_pad), d=1 / fs)
    magnitude = np.abs(np_fft)

    return freqs, magnitude, np_fft, signal_pad


def fft_plot(signal, fs, title="FFT Spectrum"):
    freqs, magnitude, fft_output, signal_pad = manual_fft(signal, fs)

    plt.figure(figsize=(10, 4))
    plt.plot(freqs, magnitude, color=DARK_BLUE)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title(title)
    plt.grid(True)
    plt.show()


def numpy_fft_plot(signal, fs, title="NumPy FFT"):
    freqs, magnitude, np_fft, signal_pad = library_fft(signal, fs)

    plt.figure(figsize=(10, 4))
    plt.plot(freqs, magnitude, color=DARK_BLUE)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title(title)
    plt.grid(True)
    plt.show()


def compare_fft_plot(signal, fs, title="FFT Comparison"):
    manual_freqs, manual_magnitude, my_fft, signal_pad = manual_fft(signal, fs)
    numpy_freqs, numpy_magnitude, np_fft, signal_pad = library_fft(signal, fs)

    max_complex_error = np.max(np.abs(np.array(my_fft) - np.array(np_fft)))
    mean_complex_error = np.mean(np.abs(np.array(my_fft) - np.array(np_fft)))
    is_close = np.allclose(np.array(my_fft), np.array(np_fft), atol=1e-9)

    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(manual_freqs, manual_magnitude, color=DARK_BLUE)
    plt.title(title + " | Manual FFT")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(numpy_freqs, numpy_magnitude, color=DARK_BLUE)
    plt.title(title + " | NumPy FFT")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    text = (
        f"Max complex error: {max_complex_error:.6e}\n"
        f"Mean complex error: {mean_complex_error:.6e}\n"
        f"Allclose: {is_close}"
    )

    plt.gcf().text(
        0.72, 0.02, text,
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray")
    )

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()

    plt.figure(figsize=(10, 4))
    plt.plot(manual_freqs, manual_magnitude, color=DARK_BLUE, label="Manual FFT")
    plt.plot(numpy_freqs, numpy_magnitude, linestyle="--", color="black", label="NumPy FFT")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title(title)
    plt.grid(True)
    plt.legend()

    plt.text(
        0.68, 0.80, text,
        transform=plt.gca().transAxes,
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray")
    )

    plt.show()

    print("max complex error:", max_complex_error)
    print("mean complex error:", mean_complex_error)
    print("allclose:", is_close)
