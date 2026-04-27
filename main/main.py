import os
import sys
from collections import defaultdict
from multiprocessing import Pool, cpu_count
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.signal_loader import load_signal
from features.broadbound_characterístics import compute_broadband_features
from features.fsc import frequency_selective_characteristics
from results_exporter import export
from trend_analysis.fsc_trend import fsc_trend_analysis
from trend_analysis.metrics_trend import metrics_trend_analysis
from trend_analysis.trend_exporter import save_trend_excel
from features.plot_spectra import save_fft_plot_from_signal, save_fsc_plot_from_processed_signal
from trend_analysis.trend_plots import plotting_metrics_trend, plotting_fsc_trend
from features.compare_plots import collect_fft_errors, save_fft_summary_plot

SIGNALS_FOLDER = "signals-by-sensors"
OUTPUT_FILE    = "turbines_analysis.xlsx"
FSC_FILE       = "fsc_results.xlsx"
TREND_FILE     = "trend_summary.xlsx"
OUTPUT_ROOT    = "results"

WORKERS = min(3, cpu_count())


def collect_files(root):
    """
    Collect all .cms signal file paths from the directory structure.

    Parameters:
    root(str) : root directory containing turbine/sensor subfolders.

    Returns:
    list of tuples : (turbine, sensor, filepath)
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
                    items.append((turbine, sensor,
                                  os.path.join(sensor_entry.path, fname)))
    return items


def ask_limit(total: int) -> int:
    """
    Ask how many files to process.

    Parameters:
    total(int) : total number of available signal files.

    Returns:
    int : number of files to process.
    """
    print(
        "WARNING!\n"
        "The dataset contains 4706 signal files. So, processing the full dataset may take a long time.\n"
        "Enter how many files should be processed (between 1 and 4706) or enter anything else to process all files.")
    while True:
        raw = input("  > ").strip()
        if raw == "":
            print(f"Processing all {total} files.\n")
            return total

        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= total:
                print(f"Processing {n} of {total} files.\n")
                return n
            else:
                print(f"  Please enter a number between 1 and {total}.")
        else:
            print("  Please enter a valid number or press Enter.")


def process_full(args):
    """
    Process a single signal file: load, extract features, compute FSC,
    save plots — all in the worker so sig is never sent back through IPC
    and RAM is freed immediately after each file.

    Parameters:
    args(tuple) : (turbine, sensor, filepath, output_root)

    Returns:
    tuple or None : (turbine, row, fsc_rows, fft_error)
    """
    turbine, sensor, filepath, output_root = args

    try:
        sig = load_signal(filepath)
    except Exception as e:
        return None

    try:
        signal   = sig["signal"]
        fs       = sig["sample_rate"]
        meta     = sig["meta"]
        raw      = sig["raw"]
        filename = os.path.basename(filepath)

        bb = compute_broadband_features(signal)

        wind  = raw.get("WindSpeed",     {}).get("Data", [])
        power = raw.get("Power",         {}).get("Data", [])
        rpm   = raw.get("RotationSpeed", {}).get("Data", [])

        condition = (
            meta.get("Operating conditions")
            or raw.get("Operating Conditions")
            or "unknown"
        )

        row = {
            "start_ms":             meta.get("Signal start time (ms)"),
            "end_ms":               meta.get("Signal end time (ms)"),
            "duration":             meta.get("Duration (s)"),
            "operating_conditions": meta.get("Operating conditions"),
            "sensor_num":           sensor,
            "signal_type":          meta.get("Signal type"),
            "resampling_mode":      meta.get("Resampling"),
            "frequency_span":       meta.get("Frequency span"),
            "lor":                  meta.get("Lines of resolution"),

            "filename":  filename,
            "condition": condition,
            "time_stamp": meta.get("Signal start time (ms)"),

            "MaxPeak":       bb["max_peak"],
            "PeakToPeak":    bb["peak_to_peak"],
            "RMS":           bb["rms"],
            "CrestFactor":   bb["crest_factor"],
            "KFactor":       bb["k_factor"],
            "ImpulseFactor": bb["impulse_factor"],
            "Skewness":      bb["skewness"],
            "Kurtosis":      bb["kurtosis"],

            "WindSpeed_mean": sum(wind)  / len(wind)  if wind  else None,
            "Power_mean":     sum(power) / len(power) if power else None,
            "RPM_mean":       sum(rpm)   / len(rpm)   if rpm   else None,
        }

        fsc_rows = frequency_selective_characteristics(
            sig,
            sensor_id=int(sensor),
            turbine_name=turbine,
            file_name=filename
        )

        fft_error = None
        try:
            save_fft_plot_from_signal(signal, fs, turbine, sensor, filename, output_root)
        except Exception:
            pass
        try:
            save_fsc_plot_from_processed_signal(sig, turbine, sensor, filename, output_root)
        except Exception:
            pass
        try:
            fft_error = collect_fft_errors(signal, fs)
        except Exception:
            pass

        return turbine, row, fsc_rows, fft_error

    except Exception as e:
        print(f"  [SKIP] processing error: {os.path.basename(filepath)} — {e}")
        return None


def stage_process(files):
    """
    Run parallel signal processing with live progress output.

    Parameters:
    files(list) : list of (turbine, sensor, filepath) tuples.

    Returns:
    grouped           : dict turbine -> list of row dicts
    all_fsc           : list of FSC row dicts
    errors_by_turbine : dict turbine -> sensor -> list of fft error tuples
    """
    plots_root = os.path.join(OUTPUT_ROOT, "plots")
    args = [
        (turbine, sensor, filepath, plots_root)
        for turbine, sensor, filepath in files
    ]

    total  = len(args)
    done   = 0
    errors = 0

    grouped           = defaultdict(list)
    all_fsc           = []
    errors_by_turbine = defaultdict(lambda: defaultdict(list))

    print(f"Total files: {total}")

    with Pool(WORKERS) as pool:
        for result in pool.imap_unordered(process_full, args, chunksize=4):
            done += 1

            if result is None:
                errors += 1
            else:
                turbine, row, fsc_rows, fft_error = result
                grouped[turbine].append(row)
                all_fsc.extend(fsc_rows)
                if fft_error is not None:
                    sensor = row["sensor_num"]
                    errors_by_turbine[turbine][sensor].append(fft_error)

            if done % 100 == 0 or done == total:
                print(f"  {done}/{total} done")

    print(f"Processing complete: {done} files\n")
    return grouped, all_fsc, errors_by_turbine


def stage_save_tables(grouped, all_fsc):
    """Save main Excel and FSC Excel (one sheet per turbine)."""
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    fsc_df  = pd.DataFrame(all_fsc)
    fsc_csv = os.path.join(OUTPUT_ROOT, "fsc_results.csv")
    fsc_df.to_csv(fsc_csv, index=False)

    export(grouped, os.path.join(OUTPUT_ROOT, OUTPUT_FILE), fsc_csv)

    fsc_path = os.path.join(OUTPUT_ROOT, FSC_FILE)
    with pd.ExcelWriter(fsc_path, engine="openpyxl") as writer:
        for turbine, grp in fsc_df.groupby("turbine"):
            grp.to_excel(writer, sheet_name=str(turbine)[:31], index=False)
    print(f"FSC Excel saved: {fsc_path}")

    return fsc_df


def stage_trends(grouped, fsc_df):
    """Compute trends and save coloured Excel."""
    metric_params = [
        "RMS", "MaxPeak", "PeakToPeak", "CrestFactor",
        "KFactor", "ImpulseFactor", "Skewness", "Kurtosis",
        "WindSpeed_mean", "Power_mean", "RPM_mean",
    ]

    all_metrics = []
    for turbine, rows in grouped.items():
        for row in rows:
            for param in metric_params:
                all_metrics.append({
                    "turbine":    turbine,
                    "sensor":     row.get("sensor_num"),
                    "condition":  row.get("condition", "unknown"),
                    "parameter":  param,
                    "time_stamp": row.get("time_stamp"),
                    "value":      row.get(param),
                })

    metrics_df     = pd.DataFrame(all_metrics)
    print("Metrics DF ready:", metrics_df.shape)

    metrics_trends = metrics_trend_analysis(metrics_df)
    fsc_trends     = fsc_trend_analysis(fsc_df)

    save_trend_excel(
        metrics_trends,
        fsc_trends,
        os.path.join(OUTPUT_ROOT, TREND_FILE)
    )
    print(f"Trend Excel saved: {os.path.join(OUTPUT_ROOT, TREND_FILE)}")


def stage_fft_summaries(errors_by_turbine):
    """Save one FFT compare summary plot per turbine."""
    if not errors_by_turbine:
        return
    plots_root = os.path.join(OUTPUT_ROOT, "plots")
    print("Generating FFT compare summaries...")
    for turbine, sensors_dict in errors_by_turbine.items():
        save_fft_summary_plot(sensors_dict, plots_root, turbine)
    print("FFT summaries done.")


def stage_trend_plots(grouped, fsc_df):
    """Generate trend plots for metrics and FSC."""
    plots_root = os.path.join(OUTPUT_ROOT, "plots")

    metric_params = [
        "RMS", "MaxPeak", "PeakToPeak", "CrestFactor",
        "KFactor", "ImpulseFactor", "Skewness", "Kurtosis",
        "WindSpeed_mean", "Power_mean", "RPM_mean",
    ]

    print("Generating metrics trend plots...")
    all_metrics = []
    for turbine, rows in grouped.items():
        for row in rows:
            for param in metric_params:
                all_metrics.append({
                    "turbine":    turbine,
                    "sensor":     row.get("sensor_num"),
                    "parameter":  param,
                    "time_stamp": row.get("time_stamp"),
                    "value":      row.get(param),
                })

    metrics_df = pd.DataFrame(all_metrics)
    for (turbine, sensor, param), grp in metrics_df.groupby(
            ["turbine", "sensor", "parameter"]):
        plotting_metrics_trend(grp, turbine, sensor, param, plots_root)

    print("Generating FSC trend plots...")
    for (turbine, sensor, comp, char), grp in fsc_df.groupby(
            ["turbine", "sensor", "component", "characteristic"]):
        plotting_fsc_trend(grp, turbine, sensor, comp, char, plots_root)

    print("Trend plots done.")


def main():

    if not os.path.exists(SIGNALS_FOLDER):
        raise ValueError(f"Signals folder not found: {SIGNALS_FOLDER}")

    print(f"\nScanning {SIGNALS_FOLDER}...")
    files = collect_files(SIGNALS_FOLDER)

    limit = ask_limit(len(files))
    files = files[:limit]

    print("Processing signals + generating plots...")
    grouped, all_fsc, errors_by_turbine = stage_process(files)

    print("Saving tables...")
    fsc_df = stage_save_tables(grouped, all_fsc)

    print("Computing trends...")
    stage_trends(grouped, fsc_df)

    stage_fft_summaries(errors_by_turbine)

    print("Generating trend plots...")
    stage_trend_plots(grouped, fsc_df)

    print("\nDONE")


if __name__ == "__main__":
    main()
