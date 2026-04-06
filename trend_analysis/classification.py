def classify_status(trend, z):
    """
    Classify condition based on trend and z-score.

    parameters:
    trend - trend direction
    z - z-score

    returns:
    status string (OK / WARNING / ALARM)
    """

    if trend == "increasing" and z is not None:
        if z >= 3.5:
            return "ALARM"
        elif z >= 1.96:
            return "WARNING"
    return "OK"
