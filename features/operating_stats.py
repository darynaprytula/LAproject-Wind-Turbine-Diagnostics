import statistics


def compute_operating_stats(data: dict) -> dict:
    """
    Compute mean operating parameters from signal metadata.

    parameters:
    data (dict):
        Raw JSON data containing:
        - WindSpeed["Data"]
        - Power["Data"]
        - RotationSpeed["Data"]

    returns:
    dict
        Dictionary with mean values:
        - windspeed_mean: average wind speed
        - power_mean: average power
        - rpm_mean: average rotation speed
    """

    windspeed_mean = statistics.mean(float(v) for v in data["WindSpeed"]["Data"])
    power_mean = statistics.mean(float(v) for v in data["Power"]["Data"])
    rpm_mean = statistics.mean(float(v) for v in data["RotationSpeed"]["Data"])

    return {
        "windspeed_mean": windspeed_mean,
        "power_mean": power_mean,
        "rpm_mean": rpm_mean
    }
