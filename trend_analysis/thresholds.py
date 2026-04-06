import numpy as np
def compute_thresholds(series):
    mean = np.mean(series)
    std = np.std(series)

    warning = mean + 3 * std
    alert = mean + 6 * std

    return mean, std, warning, alert
