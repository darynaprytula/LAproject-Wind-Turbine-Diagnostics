import os
import csv
import statistics
import matplotlib.pyplot as plt
from config.parameters import BEARINGS, GEARS
from features.amplitude_spectrum import amplitude_spectrum

def rpm_to_hz(rpm):
    """
    Convert rotation speed from RPM to Hz.

    parameters:
    rpm - rotation speed in RPM

    returns:
    rotation speed in Hz
    """
    return rpm / 60.0


def get_amplitude_at_frequency(frequencies, amplitude, target_freq, band=0.156):
    """
    Find maximum amplitude near target frequency.

    parameters:
    frequencies - frequency axis (Hz)
    amplitude - amplitude spectrum values
    target_freq - target frequency (Hz)
    band - search band around frequency (+/- Hz)

    returns:
    maximum amplitude in band or None
    """
    values = []

    for i in range(len(frequencies)):
        if target_freq - band <= frequencies[i] <= target_freq + band:
            values.append(amplitude[i])

    if len(values) == 0:
        return None

    return max(values)


def bearing_frequencies(sensor_id, gen_speed_hz):
    """
    Compute bearing characteristic frequencies.

    parameters:
    sensor_id - sensor identifier
    gen_speed_hz - generator speed (Hz)

    returns:
    list of dictionaries with component, characteristic, frequency
    """
    result = []

    if sensor_id not in BEARINGS:
        return result

    for item in BEARINGS[sensor_id]:
        shaft_speed_hz = item["TR"] * gen_speed_hz

        result.append({
            "component": item["Name"],
            "characteristic": "BPFO",
            "frequency": item["BPFO"] * shaft_speed_hz
        })
        result.append({
            "component": item["Name"],
            "characteristic": "BPFI",
            "frequency": item["BPFI"] * shaft_speed_hz
        })
        result.append({
            "component": item["Name"],
            "characteristic": "FTF",
            "frequency": item["FTF"] * shaft_speed_hz
        })
        result.append({
            "component": item["Name"],
            "characteristic": "BSF2",
            "frequency": item["BSF2"] * shaft_speed_hz
        })

    return result


def gear_frequencies(sensor_id, gen_speed_hz):
    """
    Compute gear mesh frequencies.

    parameters:
    sensor_id - sensor identifier
    gen_speed_hz - generator speed (Hz)

    returns:
    list of dictionaries with component, characteristic, frequency
    """
    result = []

    if sensor_id not in GEARS:
        return result

    for item in GEARS[sensor_id]:
        if item["Mode"] == "gear_teeth":
            gmf1 = item["Teeth_Number"] * item["TR"] * gen_speed_hz
        elif item["Mode"] == "gear_tr_only":
            gmf1 = item["TR"] * gen_speed_hz
        else:
            continue

        for h in item["Harmonics"]:
            result.append({
                "component": item["Name"],
                "characteristic": f"GMF{h}x",
                "frequency": h * gmf1
            })

    return result


def all_characteristic_frequencies(sensor_id, gen_speed_hz):
    """
    Combine all characteristic frequencies (bearings + gears).

    parameters:
    sensor_id - sensor identifier
    gen_speed_hz - generator speed (Hz)

    returns:
    list of all characteristic frequencies
    """
    result = []
    result += bearing_frequencies(sensor_id, gen_speed_hz)
    result += gear_frequencies(sensor_id, gen_speed_hz)
    return result


def frequency_selective_characteristics(sig, sensor_id, turbine_name="", file_name="", band=1.0):
    """
    Compute frequency selective characteristics (FSC).

    parameters:
    sig          - signal dictionary from load_signal()
    sensor_id    - sensor identifier
    turbine_name - turbine name
    file_name    - file name (used as row identifier and for timestamp extraction)
    band         - frequency search band (+/- Hz)

    returns:
    list of dictionaries with:
        - turbine, sensor, time_stamp, name
        - component, characteristic
        - target_frequency_hz, amplitude
    """
    signal = sig["signal"]
    fs     = sig["sample_rate"]
    raw    = sig["raw"]
    meta   = sig["meta"]

    rotation_speed_rpm = None
    if "RotationSpeed" in raw and "Data" in raw["RotationSpeed"]:
        values = raw["RotationSpeed"]["Data"]
        if len(values) > 0:
            rotation_speed_rpm = statistics.mean(values)

    if rotation_speed_rpm is None:
        return []

    gen_speed_hz = rpm_to_hz(rotation_speed_rpm)

    frequencies, amplitude = amplitude_spectrum(signal, fs)
    target_frequencies     = all_characteristic_frequencies(sensor_id, gen_speed_hz)

    raw_ts = meta.get("Signal start time (ms)")
    time_stamp = str(int(raw_ts)) if raw_ts is not None else ""

    rows = []

    for item in target_frequencies:
        if item["frequency"] > fs / 2:
            amp = None
        else:
            amp = get_amplitude_at_frequency(
                frequencies,
                amplitude,
                item["frequency"],
                band
            )

        rows.append({
            "turbine":             turbine_name,
            "sensor":              sensor_id,
            "time_stamp":          time_stamp,
            "name":                file_name,
            "component":           item["component"],
            "characteristic":      item["characteristic"],
            "target_frequency_hz": item["frequency"],
            "amplitude":           amp,
        })

    return rows


def get_peak_near_frequency(frequencies, amplitude, target_freq, band=1.0):
    """
    Find peak frequency and amplitude near target frequency.

    parameters:
    frequencies - frequency axis
    amplitude   - amplitude spectrum
    target_freq - target frequency (Hz)
    band        - search band (+/- Hz)

    returns:
    tuple : (peak_frequency, peak_amplitude) or (None, None)
    """
    best_freq = None
    best_amp  = None

    for i in range(len(frequencies)):
        if target_freq - band <= frequencies[i] <= target_freq + band:
            if best_amp is None or amplitude[i] > best_amp:
                best_amp  = amplitude[i]
                best_freq = frequencies[i]

    return best_freq, best_amp
