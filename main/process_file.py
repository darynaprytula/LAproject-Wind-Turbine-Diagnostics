from data.signal_loader import load_signal
from features.broadbound_characterístics import compute_broadband_features
import os


def process_file(filepath: str) -> dict | None:
    try:
        sig = load_signal(filepath)
    except Exception as e:
        print(f"❌ load error: {filepath}")
        print(e)
        return None

    try:
        signal = sig["signal"]
        meta = sig["meta"]
        raw = sig["raw"]

        bb = compute_broadband_features(signal)

        wind = raw.get("WindSpeed", {}).get("Data", [])
        power = raw.get("Power", {}).get("Data", [])
        rpm = raw.get("RotationSpeed", {}).get("Data", [])

        start_time = meta.get("Signal start time (ms)")
        end_time = meta.get("Signal end time (ms)")

        if start_time is None or end_time is None:
            print(f"⚠️ Missing time in meta: {filepath}")
            print(meta)

        row = {
            "start_ms": meta.get("Signal start time (ms)"),
            "end_ms": meta.get("Signal end time (ms)"),
            "duration": meta.get("Duration (s)"),
            "operating_conditions": meta.get("Operating conditions"),
            "sensor_num": meta.get("Sensor №"),
            "signal_type": meta.get("Signal type"),
            "resampling_mode": meta.get("Resampling"),
            "frequency_span": meta.get("Frequency span"),
            "lor": meta.get("Lines of resolution"),

            "filename": os.path.basename(filepath),

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
        return row

    except Exception as e:
        print(f"⚠️ processing error: {filepath}")
        print(e)
        return None
