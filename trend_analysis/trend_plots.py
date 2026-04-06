import os
import re
import numpy as np
import matplotlib.pyplot as plt

from trend_analysis.trend_analisys import mann_kendall_test
from trend_analysis.classification import classify_status
from trend_analysis.thresholds import compute_thresholds


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


def plotting_metrics_trend(group, turbine, sensor, parameter, output_root):
    """
    Plot and save trend analysis for time-domain features.

    The function sorts the data by time, extracts the parameter series,
    applies Mann–Kendall trend test, and visualizes the time evolution.

    Parameters:
    group : dataframe containing:
        - "time_stamp" : timestamps
        - "value" : parameter values
    turbine : turbine identifier/name.
    sensor : sensor identifier.
    parameter : name of the parameter (e.g., RMS, kurtosis).
    output_root(str) : root directory where plots will be saved.

    Returns:
    None
    """
    group = group.sort_values("time_stamp")
    series = group["value"].dropna()

    if len(series) < 15:
        return

    time = group.loc[series.index, "time_stamp"]

    trend, p_value, z = mann_kendall_test(series)
    slope = np.polyfit(np.arange(len(series)), series, 1)[0]
    status = classify_status(trend, z)

    plt.figure(figsize=(12, 6))
    plt.plot(time, series, alpha=0.3, label="Raw")

    plt.title(f"{parameter} | {turbine} | Sensor {sensor}")
    plt.xlabel("Time")
    plt.ylabel(parameter)

    if z is not None:
        text = f"Trend: {trend}\np={p_value:.3f}\nZ={z:.2f}\nStatus={status}"
        plt.text(
            0.02, 0.95, text,
            transform=plt.gca().transAxes,
            verticalalignment="top"
        )

    plt.legend()

    save_dir = os.path.join(
        output_root,
        "trends_results",
        "time_features",
        clean_name(turbine),
        f"Sensor_{sensor}"
        )
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{clean_name(parameter)}.png")
    plt.savefig(save_path)
    plt.close()


def plotting_fsc_trend(group, turbine, sensor, component, characteristic, output_root):
    """
    Plot and save trend analysis for frequency-domain (FSC) features.

    The function analyzes amplitude evolution of characteristic frequencies,
    applies Mann–Kendall test, and visualizes trends with thresholds.

    Parameters:
    group : dataframe containing:
        - "time_stamp" : timestamps
        - "amplitude" : amplitude values of characteristic frequency
    turbine : turbine identifier/name.
    sensor : sensor identifier.
    component : machine component (e.g., bearing, gearbox).
    characteristic : frequency characteristic (e.g., BPFO, BPFI).
    output_root(str) : root directory where plots will be saved.

    Returns:
    None
    """
    group = group.sort_values("time_stamp")
    series = group["amplitude"].dropna()

    if len(series) < 15:
        return

    time = group.loc[series.index, "time_stamp"]

    trend, p_value, z = mann_kendall_test(series)
    slope = np.polyfit(np.arange(len(series)), series, 1)[0]
    status = classify_status(trend, z)

    plt.figure(figsize=(12, 6))
    plt.plot(time, series, alpha=0.3, label="Raw")
    mean, std, warning, alert = compute_thresholds(series)

    plt.axhline(warning, color="orange", linestyle="--", label="Warning")
    plt.axhline(alert, color="red", linestyle="--", label="Alert")

    plt.title(f"{component}_{characteristic} | {turbine} | Sensor {sensor}")
    plt.xlabel("Time")
    plt.ylabel("Amplitude")

    if z is not None:
        text = f"Trend: {trend}\np={p_value:.3f}\nZ={z:.2f}\nStatus={status}"
        plt.text(
            0.02, 0.95, text,
            transform=plt.gca().transAxes,
            verticalalignment="top"
        )

    plt.legend()

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
    plt.savefig(save_path)
    plt.close()
