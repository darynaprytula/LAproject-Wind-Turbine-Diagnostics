import os
from collections import defaultdict
from multiprocessing import Pool, cpu_count
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.signal_loader import load_signal
from features.broadbound_characterístics import compute_broadband_features
from features.fsc import frequency_selective_characteristics
from results_exporter import export
from trend_analysis.fsc_trend import fsc_trend_analysis
from trend_analysis.metrics_trend import metrics_trend_analysis

SIGNALS_FOLDER = "signals-by-sensors"
OUTPUT_FILE = "turbines_analysis.xlsx"
FSC_FILE = "fsc_results.csv"
TREND_FILE = "trend_summary.xlsx"

OUTPUT_ROOT = "results"

def collect_files(root):
    """
    Collect all signal file paths from the directory structure.

    The function traverses the root folder and gathers all .cms files,
    organizing them by turbine and sensor.

    Parameters:
    root(str) : root directory containing turbine folders.

    Returns:
    list of tuples : each tuple contains (turbine, sensor, filepath).
    """
    items = []

    for turbine_entry in os.scandir(root):
        if not turbine_entry.is_dir():
            continue

        turbine = turbine_entry.name

        for sensor_entry in os.scandir(turbine_entry.path):
            if not sensor_entry.is_dir():
                continue

            sensor = sensor_entry.name

            for fname in os.listdir(sensor_entry.path):
                if fname.endswith(".cms"):
                    items.append((
                        turbine,
                        sensor,
                        os.path.join(sensor_entry.path, fname)
                    ))

    return items


def process_full(args):
    """
    Process a single signal file and extract features.

    The function loads signal data, computes broadband features,
    extracts metadata, and calculates frequency-selective characteristics.

    Parameters:
    args(tuple) : (turbine, sensor, filepath).

    Returns:
    tuple or None :
        (turbine, row, fsc_rows) where:
        - turbine : turbine identifier
        - row(dict) : extracted metadata and time-domain features
        - fsc_rows(list) : frequency-selective characteristics
    None is returned if loading fails.
    """
    turbine, sensor, filepath = args

    try:
        sig = load_signal(filepath)
    except:
        return None

    signal = sig["signal"]
    fs = sig["sample_rate"]
    meta = sig["meta"]
    raw = sig["raw"]

    filename = os.path.basename(filepath)

    bb = compute_broadband_features(signal)

    wind = raw.get("WindSpeed", {}).get("Data", [])
    power = raw.get("Power", {}).get("Data", [])
    rpm = raw.get("RotationSpeed", {}).get("Data", [])

    condition = (
        meta.get("Operating Conditions")
        or meta.get("condition")
        or raw.get("Operating Conditions")
        or "unknown"
    )

    row = {
        **meta,
        "filename": filename,
        "sensor_num": sensor,
        "condition": condition,

        "MaxPeak": bb["max_peak"],
        "PeakToPeak": bb["peak_to_peak"],
        "RMS": bb["rms"],
        "CrestFactor": bb["crest_factor"],
        "KFactor": bb["k_factor"],
        "ImpulseFactor": bb["impulse_factor"],
        "Skewness": bb["skewness"],
        "Kurtosis": bb["kurtosis"],

        "WindSpeed_mean": sum(wind)/len(wind) if wind else None,
        "Power_mean": sum(power)/len(power) if power else None,
        "RPM_mean": sum(rpm)/len(rpm) if rpm else None,
    }

    if "time_stamp" not in row:
        row["time_stamp"] = (
            meta.get("time_stamp")
            or meta.get("Timestamp")
            or raw.get("SignalHeader", {}).get("Timestamp")
        )

    start_time = meta.get("Signal start time (ms)")
    end_time = meta.get("Signal end time (ms)")

    condition = meta.get("Operating conditions", "unknown")
    fsc_rows = frequency_selective_characteristics(
        sig,
        sensor_id=int(sensor),
        turbine_name=turbine,
        file_name=filename
    )

    return turbine, row, fsc_rows

def main():
    """
    Run full signal processing and analysis pipeline.

    The function:
    - Collects all signal files
    - Processes them in parallel
    - Computes time-domain and frequency-domain features
    - Saves results to CSV and Excel files
    - Performs trend analysis on extracted features
    """
    if not os.path.exists(SIGNALS_FOLDER):
        raise ValueError("Signals folder not found")

    files = collect_files(SIGNALS_FOLDER)

    print(f"Files: {len(files)}")
    print(f"CPU: {cpu_count()}")

    with Pool(cpu_count()) as pool:
        results = pool.map(process_full, files)

    results = [r for r in results if r is not None]

    grouped = defaultdict(list)
    all_fsc = []

    for turbine, row, fsc_rows in results:
        grouped[turbine].append(row)
        all_fsc.extend(fsc_rows)

    fsc_df = pd.DataFrame(all_fsc)
    fsc_df.to_csv(FSC_FILE, index=False)

    print("FSC saved")

    export(grouped, OUTPUT_FILE, FSC_FILE)

    print("Excel saved")

    print("Preparing metrics dataframe...")

    all_metrics = []

    metric_params = [
        "RMS",
        "MaxPeak",
        "PeakToPeak",
        "CrestFactor",
        "KFactor",
        "ImpulseFactor",
        "Skewness",
        "Kurtosis",
        "WindSpeed_mean",
        "Power_mean",
        "RPM_mean"
    ]

    for turbine, rows in grouped.items():
        for row in rows:
            for param in metric_params:

                value = row.get(param)

                if value is None:
                    continue

                all_metrics.append({
                    "turbine": turbine,
                    "sensor": row.get("sensor_num"),
                    "condition": row.get("condition", "unknown"),
                    "parameter": param,
                    "time_stamp": row.get("time_stamp"),
                    "value": value
                })

    metrics_df = pd.DataFrame(all_metrics)

    print("Metrics DF ready:", metrics_df.shape)

    print("Computing trends...")

    metrics_trends = metrics_trend_analysis(metrics_df)
    fsc_trends = fsc_trend_analysis(fsc_df)

    with pd.ExcelWriter(TREND_FILE) as writer:
        metrics_trends.to_excel(writer, sheet_name="Time Features", index=False)
        fsc_trends.to_excel(writer, sheet_name="Spectral Features", index=False)

    print("Trend tables saved")


if __name__ == "__main__":
    main()
