import numpy as np
import pandas as pd
import xarray as xr

from datetime import datetime


def read_saildrone_format(filename: str) -> pd.DataFrame:
    data = (
        xr.open_dataset(filename, drop_variables=["trajectory", "obs", "rowSize"])
        .to_dataframe()
        .reset_index(drop=True)
    )

    try:
        data = data.rename(columns={"time": "date"})
    except:
        pass

    try:
        data = data.rename(columns={"WIND_FROM_MEAN": "wind_direction"})
    except:
        pass

    try:
        data = data.rename(columns={"WIND_SPEED_MEAN": "wind_speed"})
    except:
        pass

    try:
        data = data.rename(columns={"TEMP_AIR_MEAN": "air_temperature"})
    except:
        pass

    try:
        data = data.rename(columns={"RH_MEAN": "relative_humidity"})
    except:
        pass

    try:
        data = data.rename(columns={"BARO_PRES_MEAN": "sea_level_pressure"})
    except:
        pass

    try:
        data = data.rename(columns={"WAVE_DOMINANT_PERIOD": "dominant_wave_period"})
    except:
        pass

    try:
        data = data.rename(
            columns={"WAVE_SIGNIFICANT_HEIGHT": "significant_wave_height"}
        )
    except:
        pass

    try:
        data = data.rename(columns={"TEMP_SBE37_MEAN": "sea_surface_temperature"})
    except:
        pass

    try:
        data = data.rename(columns={"SAL_SBE37_MEAN": "sea_surface_salinity"})
    except:
        pass

    return data


def read_ndbc_buoy_format(filename: str) -> pd.DataFrame:
    with open(filename, "r") as fl:
        data = fl.readlines()
    data = [line.rstrip().split() for line in data]

    header = data[:2]
    data = data[2:]
    date = [
        datetime.strptime(line[0] + line[1] + line[2] + line[3] + line[4], "%Y%m%d%H%M")
        for line in data
    ]
    wdir = [float(line[5]) if line[5] != "MM" else np.nan for line in data]
    wspd = [float(line[6]) if line[6] != "MM" else np.nan for line in data]
    gst = [float(line[7]) if line[7] != "MM" else np.nan for line in data]
    wvht = [float(line[8]) if line[8] != "MM" else np.nan for line in data]
    dpd = [float(line[9]) if line[9] != "MM" else np.nan for line in data]
    apd = [float(line[10]) if line[10] != "MM" else np.nan for line in data]
    mwd = [float(line[11]) if line[11] != "MM" else np.nan for line in data]
    pres = [float(line[12]) if line[12] != "MM" else np.nan for line in data]
    atmp = [float(line[13]) if line[13] != "MM" else np.nan for line in data]
    wtmp = [float(line[14]) if line[14] != "MM" else np.nan for line in data]
    dewp = [float(line[15]) if line[15] != "MM" else np.nan for line in data]
    vis = [float(line[16]) if line[16] != "MM" else np.nan for line in data]
    ptdy = [float(line[17]) if line[17] != "MM" else np.nan for line in data]
    tide = [float(line[18]) if line[18] != "MM" else np.nan for line in data]

    df = pd.DataFrame([])
    df["date"] = date
    df["wind_direction"] = wdir
    df["wind_speed"] = wspd
    df["wind_gust"] = gst
    df["significant_wave_height"] = wvht
    df["dominant_wave_period"] = dpd
    df["average_wave_period"] = apd
    df["dwpd_direction"] = mwd
    df["sea_level_pressure"] = pres
    df["air_temperature"] = atmp
    df["sea_surface_temperature"] = wtmp
    df["dewpoint_temperature"] = dewp
    df["visibility"] = vis
    df["pressure_tendency"] = ptdy
    df["tide_level"] = tide

    return df


def coordinate_degrees_minutes_to_decimal(string: str):
    """
    Args:
    - string: location in format DDMM.MMM

    Returns:
    - decimal representation of given location: DD.DDDD
    """

    flt = float(string)

    if flt > 0:
        deg = int(flt / 100.0)
        min = flt % 100
        res = float(deg) + float(min) / 60
    elif flt < 0:
        deg = abs(int(flt / 100))
        min = abs(flt) % 100
        res = -(float(deg) + float(min) / 60)

    return res
