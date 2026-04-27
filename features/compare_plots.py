import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from features.fft import manual_fft, library_fft

DARK_BLUE = "#0B3D91"

def clean_name(name):
    name = str(name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.replace(" ", "_")
    return name


def collect_fft_errors(signal, fs):
    """
    Compute max and mean complex error between manual and numpy FFT.

    Parameters:
    signal : input signal array.
    fs     : sampling frequency (Hz).

    Returns:
    tuple : (max_error, mean_error, allclose)
    """
    _, _, my_fft,  _ = manual_fft(signal, fs)
    _, _, np_fft,  _ = library_fft(signal, fs)

    diff       = np.abs(np.array(my_fft) - np.array(np_fft))
    max_error  = float(np.max(diff))
    mean_error = float(np.mean(diff))
    allclose   = bool(np.allclose(np.array(my_fft), np.array(np_fft), atol=1e-9))

    return max_error, mean_error, allclose


def save_fft_summary_plot(errors_by_sensor: dict, output_root: str, turbine: str):
    """
    Save one summary plot per turbine showing FFT error distribution per sensor.

    Instead of one PNG per signal (4700+ files), produces one plot per turbine
    with subplots for each sensor showing the distribution of max errors.

    Parameters:
    errors_by_sensor : dict  sensor -> list of (max_error, mean_error, allclose)
    output_root      : root directory for plots.
    turbine          : turbine identifier.
    """
    sensors = sorted(errors_by_sensor.keys(), key=lambda x: int(x) if str(x).isdigit() else x)

    if not sensors:
        return

    n = len(sensors)
    cols = min(4, n)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3.5), squeeze=False)
    fig.suptitle(
        f"FFT Error Distribution | {turbine}\n"
        f"(manual vs numpy, max complex error per signal)",
        fontsize=11, y=1.01
    )

    all_close_total = 0
    all_total       = 0

    for idx, sensor in enumerate(sensors):
        ax       = axes[idx // cols][idx % cols]
        records  = errors_by_sensor[sensor]

        max_errors  = [r[0] for r in records]
        allclose_ok = sum(1 for r in records if r[2])

        all_close_total += allclose_ok
        all_total       += len(records)

        ax.hist(max_errors, bins=30, color=DARK_BLUE, edgecolor="white", linewidth=0.4)
        ax.set_title(f"Sensor {sensor}", fontsize=9)
        ax.set_xlabel("Max complex error", fontsize=8)
        ax.set_ylabel("Signals count",    fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, linewidth=0.3, alpha=0.5)

        pct = allclose_ok / len(records) * 100 if records else 0
        ax.text(
            0.97, 0.95,
            f"allclose: {pct:.1f}%\nn={len(records)}",
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=7,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray", linewidth=0.5)
        )

    for idx in range(len(sensors), rows * cols):
        axes[idx // cols][idx % cols].set_visible(False)

    overall_pct = all_close_total / all_total * 100 if all_total else 0
    fig.text(
        0.5, -0.01,
        f"Overall allclose (atol=1e-9): {all_close_total}/{all_total} ({overall_pct:.1f}%)",
        ha="center", fontsize=9,
        bbox=dict(facecolor="#f0f0f0", edgecolor="gray", alpha=0.9)
    )

    plt.tight_layout()

    save_dir = os.path.join(output_root, "fft_compare_plots")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{clean_name(turbine)}_fft_error_summary.png")
    fig.savefig(save_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"  FFT summary saved: {save_path}")
