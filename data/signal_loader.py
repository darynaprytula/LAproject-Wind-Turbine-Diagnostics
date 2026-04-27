import json
import numpy as np
from pathlib import Path


def load_signal(file_path: str) -> dict:
    """
    Load signal data from JSON file and extract basic information.

    parameters:
    file_path - path to .cms JSON file.

    returns:
    dictionary containing:
        - signal: numpy array of vibration signal
        - sample_rate: sampling frequency (Hz)
        - n_points: number of samples in signal
        - meta: parsed metadata from filename
        - raw: full original JSON data
    """

    file_path = Path(file_path)

    with open(file_path, "r") as f:
        data = json.load(f)

    signal = np.array(data["VibrationSignal"]["Data"])
    sample_rate = data["VibrationSignal"]["SampleRate"]
    n_points = len(signal)

    metadata = parse_filename(file_path.name)

    return {
        "signal": signal,
        "sample_rate": sample_rate,
        "n_points": n_points,
        "meta": metadata,
        "raw": data
    }


def parse_filename(filename: str) -> dict:
    """
    Parse filename and extract measurement metadata.

    parameters:
    filename - name of the file (string).

    returns:
    dictionary containing:
        - Signal start time (ms): measurement start timestamp
        - Signal end time (ms): measurement end timestamp
        - Duration (s): signal duration in seconds
        - Operating conditions: operating mode (e.g. LPC)
        - sensor_num: sensor identifier
        - Signal type: signal type (e.g. acceleration)
        - Resampling: resampling mode
        - Frequency span: frequency range (e.g. 1K)
        - Lines of resolution: line of resolution (scaled by 100)
    """

    parts = filename.split("_")
    start_time, end_time, duration = parts[:3]

    other = parts[3].split(".")

    operating_conditions = other[0]
    sensor_num = other[1]
    signal_type = other[2][1]
    resampling_mode = other[2][2]
    frequency_span = other[2][3:]
    lor = int(other[3])

    return {
        "Signal start time (ms)": start_time,
        "Signal end time (ms)":   end_time,
        "Duration (s)":           int(duration),
        "Operating conditions":   operating_conditions,
        "sensor_num":             sensor_num,
        "Signal type":            signal_type,
        "Resampling":             resampling_mode,
        "Frequency span":         frequency_span,
        "Lines of resolution":    lor * 100,
    }
