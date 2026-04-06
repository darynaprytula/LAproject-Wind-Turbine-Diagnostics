import os
import re
import numpy as np
import matplotlib.pyplot as plt
from features.fft import manual_fft, library_fft

DARK_BLUE = "#0B3D91"


def clean_name(name):
    """
    Clean a string to make it safe for file and directory names.

    The function replaces invalid filesystem characters and spaces
    to ensure compatibility across operating systems.

    Parameters:
    name : input string (e.g., turbine name, filename).

    Returns:
    name(str) : cleaned string with invalid characters replaced by "_".
    """
    name = str(name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.replace(" ", "_")
    return name


def save_compare_fft_plot(signal, fs, turbine, sensor, filename, output_root):
    """
    Compare manual FFT and NumPy FFT results and save the plot.

    The function computes FFT using both manual implementation and NumPy,
    compares their complex outputs, and visualizes magnitude spectra.
    It also calculates error metrics between the two methods and displays them on the plot.

    Parameters:
    signal : input discrete-time signal x[n].
    fs(float) : sampling frequency of the signal (in Hz).
    turbine : turbine identifier/name.
    sensor : sensor identifier (e.g., sensor number).
    filename : name of the source file.
    output_root(str) : root directory where plots will be saved.

    Returns:
    None

    Notes:
    - The function computes max and mean complex error between FFT results.
    - It checks numerical equivalence using np.allclose with tolerance 1e-9.
    - The plot contains two subplots: manual FFT and NumPy FFT magnitude spectra.
    - Output is saved in a structured directory:
      output_root/fft_compare_plots/{turbine}/Sensor_{sensor}/
    """
    manual_freqs, manual_magnitude, my_fft, signal_pad = manual_fft(signal, fs)
    numpy_freqs, numpy_magnitude, np_fft, signal_pad = library_fft(signal, fs)

    max_complex_error = np.max(np.abs(np.array(my_fft) - np.array(np_fft)))
    mean_complex_error = np.mean(np.abs(np.array(my_fft) - np.array(np_fft)))
    is_close = np.allclose(np.array(my_fft), np.array(np_fft), atol=1e-9)

    text = (
        f"Max complex error: {max_complex_error:.6e}\n"
        f"Mean complex error: {mean_complex_error:.6e}\n"
        f"Allclose: {is_close}"
    )

    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(manual_freqs, manual_magnitude, color=DARK_BLUE)
    plt.title(f"{turbine} | sensor {sensor} | {filename} | Manual FFT")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(numpy_freqs, numpy_magnitude, color=DARK_BLUE)
    plt.title(f"{turbine} | sensor {sensor} | {filename} | NumPy FFT")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)

    plt.gcf().text(
        0.70, 0.03, text,
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray")
    )

    plt.tight_layout(rect=[0, 0.06, 1, 1])

    save_dir = os.path.join(
        output_root,
        "fft_compare_plots",
        clean_name(turbine),
        f"Sensor_{sensor}"
    )
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{clean_name(filename)}.png")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
