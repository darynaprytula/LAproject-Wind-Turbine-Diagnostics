import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from trend_analysis.classification import classify_status
from trend_analysis.trend_analisys import mann_kendall_test
from trend_analysis.thresholds import compute_thresholds

def fsc_trend_analysis(df):
    """
    Compute trend analysis for FSC amplitudes.

    parameters:
    df - FSC dataframe

    returns:
    dataframe with trend results
    """

    results = []

    grouped = df.groupby([
        "turbine",
        "sensor",
        "component",
        "characteristic"
    ])

    for (turbine, sensor, component, char), group in grouped:

        group = group.sort_values("time_stamp")

        series = group["amplitude"].dropna()

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
            "Parameter": f"{component}_{char}",
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

def plot_fsc_trend(group):
    plt.plot(group["time_stamp"], group["amplitude"])
