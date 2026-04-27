import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from trend_analysis.trend_analisys import mann_kendall_test
from trend_analysis.classification import classify_status
from trend_analysis.thresholds import compute_thresholds

DARK_BLUE = "#0B3D91"

def clean_name(name):
    """
    Clean a string to make it safe for file and directory names.

    Parameters:
    name : input string.

    Returns:
    str : cleaned string with invalid characters replaced by "_".
    """
    name = str(name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.replace(" ", "_")
    return name


def _make_time_axis(time_series):
    """
    Convert time_stamp series to readable datetime labels.

    time_stamp values are Unix milliseconds stored as strings
    (e.g. "1454824800000"). Converts to pandas DatetimeIndex
    so matplotlib shows readable dates like "Jan 2016".

    Parameters:
    time_series : pandas Series of time_stamp strings or ints.

    Returns:
    tuple : (DatetimeIndex or numpy array, x_label string)
    """
    import pandas as pd

    try:
        ts = time_series.astype(str).str.strip()
        ts_int = ts[ts != ""].astype(float)

        if ts_int.empty:
            return np.arange(len(time_series)), "Signal index"

        dates = pd.to_datetime(ts_int, unit="ms")
        dates = dates + pd.DateOffset(years=10)
        return dates.values, "Date"

    except Exception:
        return np.arange(len(time_series)), "Signal index"


def plotting_metrics_trend(group, turbine, sensor, parameter, output_root):
    """
    Plot and save trend analysis for time-domain features.

    Parameters:
    group       : dataframe with "time_stamp" and "value" columns.
    turbine     : turbine identifier.
    sensor      : sensor identifier.
    parameter   : parameter name (e.g. RMS, Kurtosis).
    output_root : root directory for plots.
    """
    group  = group.sort_values("time_stamp")
    series = group["value"].dropna()

    if len(series) < 15:
        return

    x, x_label = _make_time_axis(group.loc[series.index, "time_stamp"])

    trend, p_value, z = mann_kendall_test(series)
    slope  = np.polyfit(np.arange(len(series)), series.values, 1)[0]
    status = classify_status(trend, z)

    trend_line = np.poly1d(np.polyfit(np.arange(len(series)), series.values, 1))(
        np.arange(len(series))
    )

    mean, std, warning, alert = compute_thresholds(series)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x, series.values, color=DARK_BLUE, alpha=0.5,
            linewidth=0.8, label="Raw")
    ax.plot(x, trend_line, color="#555555", linewidth=1.5,
            linestyle="--", label="Trend line")

    ax.axhline(warning, color="orange", linewidth=1.2,
               linestyle="--", label=f"Warning ({warning:.3f})")
    ax.axhline(alert, color="red", linewidth=1.2,
               linestyle="--", label=f"Alert ({alert:.3f})")

    ax.set_title(f"{parameter} | {turbine} | Sensor {sensor}", fontsize=11)
    ax.set_xlabel(x_label, fontsize=10)
    ax.set_ylabel(parameter, fontsize=10)
    ax.grid(True, linewidth=0.4, alpha=0.5)

    if z is not None:
        text = f"Trend: {trend}  |  p={p_value:.3f}  |  Z={z:.2f}  |  Slope={slope:.2e}  |  Status={status}"
        ax.set_title(
            f"{parameter} | {turbine} | Sensor {sensor}\n{text}",
            fontsize=10
        )

    ax.legend(fontsize=9, loc="upper right",
              framealpha=0.9, ncol=2)

    save_dir = os.path.join(
        output_root,
        "trends_results",
        "time_features",
        clean_name(turbine),
        f"Sensor_{sensor}"
    )
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{clean_name(parameter)}.png")
    fig.savefig(save_path, bbox_inches="tight", dpi=120)
    plt.close(fig)


def plotting_fsc_trend(group, turbine, sensor, component, characteristic, output_root):
    """
    Plot and save trend analysis for FSC amplitude evolution.

    Parameters:
    group          : dataframe with "time_stamp" and "amplitude" columns.
    turbine        : turbine identifier.
    sensor         : sensor identifier.
    component      : machine component name.
    characteristic : frequency characteristic (e.g. BPFO, BPFI).
    output_root    : root directory for plots.
    """
    group  = group.sort_values("time_stamp")
    series = group["amplitude"].dropna()

    if len(series) < 15:
        return

    x, x_label = _make_time_axis(group.loc[series.index, "time_stamp"])

    trend, p_value, z = mann_kendall_test(series)
    slope  = np.polyfit(np.arange(len(series)), series.values, 1)[0]
    status = classify_status(trend, z)

    mean, std, warning, alert = compute_thresholds(series)

    trend_line = np.poly1d(np.polyfit(np.arange(len(series)), series.values, 1))(
        np.arange(len(series))
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x, series.values, color=DARK_BLUE, alpha=0.5,
            linewidth=0.8, label="Raw")
    ax.plot(x, trend_line, color="#555555", linewidth=1.5,
            linestyle="--", label="Trend line")

    ax.axhline(warning, color="orange", linewidth=1.2,
               linestyle="--", label=f"Warning ({warning:.3f})")
    ax.axhline(alert,   color="red",    linewidth=1.2,
               linestyle="--", label=f"Alert ({alert:.3f})")

    ax.set_xlabel(x_label, fontsize=10)
    ax.set_ylabel("Amplitude", fontsize=10)
    ax.grid(True, linewidth=0.4, alpha=0.5)

    if z is not None:
        text = f"Trend: {trend}  |  p={p_value:.3f}  |  Z={z:.2f}  |  Slope={slope:.2e}  |  Status={status}"
        ax.set_title(
            f"{component}_{characteristic} | {turbine} | Sensor {sensor}\n{text}",
            fontsize=10
        )
    else:
        ax.set_title(
            f"{component}_{characteristic} | {turbine} | Sensor {sensor}",
            fontsize=11
        )

    ax.legend(fontsize=9, loc="upper right",
              framealpha=0.9, ncol=2)

    save_dir = os.path.join(
        output_root,
        "trends_results",
        "spectral_features",
        clean_name(turbine),
        f"Sensor_{sensor}",
        clean_name(component)
    )
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{clean_name(characteristic)}.png")
    fig.savefig(save_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
