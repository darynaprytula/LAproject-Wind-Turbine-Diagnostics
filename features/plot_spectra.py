import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from features.amplitude_spectrum import amplitude_spectrum, save_amplitude_spectrum_plot
from features.fsc import (
    rpm_to_hz,
    all_characteristic_frequencies,
    get_peak_near_frequency
)

DARK_BLUE   = "#0B3D91"
MARKER_COLORS = [
    "#E63946",
    "#F4A261",
    "#2A9D8F",
    "#E9C46A",
    "#A8DADC",
    "#FF006E",
    "#8338EC",
    "#FB5607",
]


def clean_name(name):
    name = str(name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.replace(" ", "_")
    return name


def save_fft_plot_from_signal(signal, fs, turbine, sensor, filename, output_root):
    """
    Compute and save amplitude spectrum plot from a signal.

    Parameters:
    signal      : input discrete-time signal x[n].
    fs(float)   : sampling frequency (Hz).
    turbine     : turbine identifier.
    sensor      : sensor identifier.
    filename    : source filename.
    output_root : root directory for plots.
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


def save_fsc_plot_from_processed_signal(
    sig, turbine, sensor, filename, output_root, band=1.0
):
    """
    Compute and save FSC plot with dark-blue spectrum and
    clearly visible per-component colour markers.

    Parameters:
    sig         : dict with signal, sample_rate, raw, meta.
    turbine     : turbine identifier.
    sensor      : sensor identifier.
    filename    : source filename.
    output_root : root directory for plots.
    band(float) : Hz window around target frequency (default 1.0).
    """
    signal = sig["signal"]
    fs     = sig["sample_rate"]
    raw    = sig["raw"]

    time_stamp = (
        sig["meta"].get("time_stamp")
        or sig["meta"].get("Timestamp")
        or raw.get("SignalHeader", {}).get("Timestamp")
        or ""
    )

    rotation_speed = raw.get("RotationSpeed", {}).get("Data", [])
    if not rotation_speed:
        return

    rpm_mean      = sum(rotation_speed) / len(rotation_speed)
    gen_speed_hz  = rpm_to_hz(rpm_mean)

    frequencies, amplitude = amplitude_spectrum(signal, fs)
    target_frequencies     = all_characteristic_frequencies(int(sensor), gen_speed_hz)

    if len(amplitude) == 0:
        return

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(frequencies, amplitude, color=DARK_BLUE, linewidth=0.8, label="_nolegend_")

    ymax = max(amplitude)

    components = {}
    for item in target_frequencies:
        comp = item.get("component", "unknown")
        if comp not in components:
            components[comp] = MARKER_COLORS[len(components) % len(MARKER_COLORS)]

    legend_added = set()

    for item in target_frequencies:
        target_freq = item["frequency"]
        char        = item["characteristic"]
        comp        = item.get("component", "unknown")
        color       = components[comp]

        if target_freq > fs / 2:
            continue

        ax.axvline(target_freq, linestyle="--", linewidth=0.8, alpha=0.5, color=color)

        peak_freq, peak_amp = get_peak_near_frequency(
            frequencies, amplitude, target_freq, band=band
        )

        label = comp if comp not in legend_added else "_nolegend_"
        legend_added.add(comp)

        if peak_freq is not None and peak_amp is not None:
            ax.plot(peak_freq, peak_amp, "o", color=color,
                    markersize=6, zorder=5, label=label)

            ax.annotate(
                char,
                xy=(peak_freq, peak_amp),
                xytext=(0, 10),
                textcoords="offset points",
                fontsize=7,
                color=color,
                rotation=90,
                va="bottom",
                ha="center",
                bbox=dict(
                    boxstyle="round,pad=0.15",
                    facecolor="white",
                    edgecolor=color,
                    alpha=0.85,
                    linewidth=0.7,
                ),
            )
        else:
            ax.plot(target_freq, ymax * 0.05, "^",
                    color=color, markersize=5, zorder=4, label=label)

    ax.set_xlabel("Frequency (Hz)", fontsize=10)
    ax.set_ylabel("Amplitude",      fontsize=10)
    ax.set_title(
        f"{turbine} | sensor {sensor} | {filename} | {time_stamp}",
        fontsize=10
    )
    ax.set_xlim(0, fs / 2)
    ax.set_ylim(0, ymax * 1.15)
    ax.grid(True, linewidth=0.4, alpha=0.5)
    ax.xaxis.set_major_locator(ticker.AutoLocator())

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles, labels,
        loc="upper right",
        fontsize=8,
        framealpha=0.9,
        title="Component",
        title_fontsize=8,
    )

    save_dir = os.path.join(
        output_root,
        "fsc_plots",
        clean_name(turbine),
        f"Sensor_{sensor}"
    )
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{clean_name(filename)}.png")
    fig.savefig(save_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
