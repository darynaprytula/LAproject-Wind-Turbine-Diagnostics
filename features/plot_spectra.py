import os
import re
import matplotlib.pyplot as plt

from features.amplitude_spectrum import amplitude_spectrum, save_amplitude_spectrum_plot
from features.fsc import (
    rpm_to_hz,
    all_characteristic_frequencies,
    get_peak_near_frequency
)

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


def save_fft_plot_from_signal(signal, fs, turbine, sensor, filename, output_root):
    """
    Compute and save amplitude spectrum plot from a signal.

    The function generates a file path based on turbine and sensor identifiers
    and saves the amplitude spectrum plot using save_amplitude_spectrum_plot.

    Parameters:
    signal : input discrete-time signal x[n].
    fs(float) : sampling frequency of the signal (in Hz).
    turbine : turbine identifier/name.
    sensor : sensor identifier (e.g., sensor number).
    filename : name of the source file.
    output_root(str) : root directory where plots will be saved.

    Returns:
    None
    """
    save_path = os.path.join(
        output_root,
        "fft_plots",
        clean_name(turbine),
        f"Sensor_{sensor}",
        f"{clean_name(filename)}.png"
    )

    save_amplitude_spectrum_plot(
        signal=signal,
        fs=fs,
        title=f"{turbine} | sensor {sensor} | amplitude spectrum",
        save_path=save_path
    )


def save_fsc_plot_from_processed_signal(sig, turbine, sensor, filename, output_root, band=1.0):
    """
    Compute and save frequency-selective characteristics (FSC) plot.

    The function extracts signal and metadata, computes the amplitude spectrum,
    determines characteristic frequencies based on rotation speed, and highlights
    peaks near those frequencies.

    Parameters:
    sig : dictionary containing processed signal data:
        - "signal" : signal values
        - "sample_rate" : sampling frequency
        - "raw" : original raw data
        - "meta" : metadata (optional)
    turbine : turbine identifier/name.
    sensor : sensor identifier (used to select bearing characteristics).
    filename : name of the source file.
    output_root(str) : root directory where plots will be saved.
    band(float) : frequency search window around target frequencies (default is 1.0 Hz).

    Returns:
    None
    """
    signal = sig["signal"]
    fs = sig["sample_rate"]
    raw = sig["raw"]

    time_stamp = (
        sig["meta"].get("time_stamp")
        or sig["meta"].get("Timestamp")
        or raw.get("SignalHeader", {}).get("Timestamp")
        or ""
    )

    rotation_speed = raw.get("RotationSpeed", {}).get("Data", [])
    if not rotation_speed:
        return

    rpm_mean = sum(rotation_speed) / len(rotation_speed)
    gen_speed_hz = rpm_to_hz(rpm_mean)

    frequencies, amplitude = amplitude_spectrum(signal, fs)
    target_frequencies = all_characteristic_frequencies(int(sensor), gen_speed_hz)

    if len(amplitude) == 0:
        return

    plt.figure(figsize=(12, 5))
    plt.plot(frequencies, amplitude, color=DARK_BLUE)

    ymax = max(amplitude)

    for item in target_frequencies:
        target_freq = item["frequency"]

        if target_freq > fs / 2:
            continue

        plt.axvline(target_freq, linestyle="--", alpha=0.6, color=DARK_BLUE)

        peak_freq, peak_amp = get_peak_near_frequency(
            frequencies,
            amplitude,
            target_freq,
            band=band
        )

        if peak_freq is not None and peak_amp is not None:
            plt.plot(peak_freq, peak_amp, "o", color="red")

            plt.text(
                peak_freq,
                peak_amp,
                item["characteristic"],
                fontsize=8,
                rotation=90,
                verticalalignment="bottom"
            )

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title(f"{turbine} | sensor {sensor} | {filename} | {time_stamp}")
    plt.xlim(0, fs / 2)
    plt.ylim(0, ymax * 1.1)
    plt.grid(True)

    save_dir = os.path.join(
        output_root,
        "fsc_plots",
        clean_name(turbine),
        f"Sensor_{sensor}"
    )
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{clean_name(filename)}.png")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
