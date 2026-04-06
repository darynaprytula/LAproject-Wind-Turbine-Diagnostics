import numpy as np
import pandas as pd
from trend_analysis.classification import classify_status
from trend_analysis.trend_analisys import mann_kendall_test
from trend_analysis.thresholds import compute_thresholds

def metrics_trend_analysis(df):
    """
    Compute trend analysis for time-domain metrics (RMS, Peak, etc.)

    parameters:
    df - metrics dataframe

    returns:
    dataframe with trend results
    """

    results = []

    grouped = df.groupby([
        "turbine",
        "sensor",
        "parameter"
    ])

    for (turbine, sensor, param), group in grouped:

        group = group.sort_values("time_stamp")

        series = group["value"].dropna()

        if len(series) < 15:
            continue

        mean, std, warning, alert = compute_thresholds(series)

        last_value = series.iloc[-1]

        if last_value > alert:
            status = "ALARM"
        elif last_value > warning:
            status = "WARNING"
        else:
            status = "OK"

        trend, p_value, z = mann_kendall_test(series)
        slope = np.polyfit(np.arange(len(series)), series, 1)[0]
        status = classify_status(trend, z)

        results.append({
            "Turbine": turbine,
            "Sensor": sensor,
            "Parameter": param,

            "Mean": mean,
            "Std": std,
            "Warning": warning,
            "Alert": alert,

            "Trend": trend,
            "Z": z,
            "p-value": p_value,
            "Slope": slope,
            "Status": status
        })
    return pd.DataFrame(results)
