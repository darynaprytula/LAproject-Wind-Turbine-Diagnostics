import numpy as np
from scipy.stats import skew, kurtosis

def compute_broadband_features(signal: np.ndarray) -> dict:
    """
    Compute basic broadband statistical features of a vibration signal.

    parameters:
    signal - 1D array containing vibration signal values.

    returns:
    dictionary with broadband features:
        - max_peak: maximum absolute amplitude
        - peak_to_peak: difference between max and min values
        - rms: root mean square value
        - crest_factor: ratio of max_peak to rms
        - k_factor: product of max_peak and rms
        - impulse_factor: ratio of max_peak to mean absolute value
        - skewness: signal asymmetry
        - kurtosis: signal peakedness (Pearson definition)
    """

    max_peak = np.max(np.abs(signal))
    peak_to_peak = np.max(signal) - np.min(signal)
    rms = np.sqrt(np.mean(signal**2))
    mean_abs = np.mean(np.abs(signal))

    if rms == 0 or mean_abs == 0:
        crest_factor = 0
        k_factor = 0
        impulse_factor = 0
    else:
        crest_factor = max_peak / rms
        k_factor = max_peak * rms
        impulse_factor = max_peak / mean_abs

    skewness = skew(signal)
    kurt = kurtosis(signal, fisher=False)

    return {
        "max_peak": max_peak,
        "peak_to_peak": peak_to_peak,
        "rms": rms,
        "crest_factor": crest_factor,
        "k_factor": k_factor,
        "impulse_factor": impulse_factor,
        "skewness": skewness,
        "kurtosis": kurt
    }
