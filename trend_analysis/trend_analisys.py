import numpy as np
from scipy.stats import kendalltau


def mann_kendall_test(series):
    """
    Perform Mann-Kendall trend test.

    parameters:
    series - time series values

    returns:
    trend, p_value, z_score
    """

    x = np.array(series)
    n = len(x)

    if n < 10:
        return None, None, None

    tau, p_value = kendalltau(np.arange(n), x)
    z = tau * np.sqrt((9*n*(n-1))/(2*(2*n+5)))

    if p_value < 0.05:
        trend = "increasing" if tau > 0 else "decreasing"
    else:
        trend = "no trend"

    return trend, p_value, z
