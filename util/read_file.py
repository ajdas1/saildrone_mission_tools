import numpy as np
import os
import pandas as pd
import shapely.geometry as shp
import xarray as xr

import importlib
import atcf_processing

importlib.reload(atcf_processing)
import conversions

importlib.reload(conversions)


from atcf_processing import (
    adecks_datadir,
    bdecks_datadir,
    column_names,
    column_types,
    fix_atcf_latitude,
    fix_atcf_longitude,
    get_atcf_files,
    get_info_from_filename,
)
from conversions import convert_wind_radii_to_polygon
from datetime import datetime
from netCDF4 import Dataset
from typing import Any, List


def remove_atcf_duplicates(data: dict):
    data_clean = {}
    searched = []
    skip = []
    for btk_c in data:
        if btk_c not in skip:
            slon_c = data[btk_c].Longitude.iloc[0]
            slat_c = data[btk_c].Latitude.iloc[0]
            stime_c = data[btk_c].Valid.iloc[0]
            btk_others = [btk for btk in data if not btk in searched + [btk_c]]
            duplicates = [btk_c]
            for btk_o in btk_others:
                slon_o = data[btk_o].Longitude.iloc[0]
                slat_o = data[btk_o].Latitude.iloc[0]
                stime_o = data[btk_o].Valid.iloc[0]
                if (slon_o == slon_c) and (slat_o == slat_c) and (stime_o == stime_c):
                    duplicates.append(btk_o)

            if len(duplicates) == 1:
                data_clean[btk_c] = data[btk_c]
            elif len(duplicates) == 2:
                duplicates = sorted(duplicates)
                data_clean[btk_c] = data[duplicates[0]]
                skip = duplicates[1]

            searched.append(btk_c)

    return data_clean


def read_raw_atcf(filename: str) -> pd.DataFrame:
    df = pd.read_csv(
        filename,
        header=None,
        names=column_names,
        dtype=column_types,
        delimiter=",",
        index_col=False,
        skipinitialspace=True,
        na_values=["Q"],
    )
    df.Date = pd.to_datetime(df.Date, format="%Y%m%d%H")
    df.Latitude = df.Latitude.apply(fix_atcf_latitude)
    df.Longitude = df.Longitude.apply(fix_atcf_longitude)

    return df


def read_all_btks(wr: int = 0) -> list[pd.DataFrame]:
    fls = get_atcf_files()
    btks = []
    for fl in fls:
        _, _, btk = read_atcf_modified_wind_radii(
            filename=fl, wr=wr, fcst=False, btk=True
        )
        if btk is not None:
            btk["Center"] = btk[["Longitude", "Latitude"]].apply(shp.Point, axis=1)
            btk["WindRadii"] = btk.apply(convert_wind_radii_to_polygon, axis=1)
            btks.append(btk)

    return btks


def read_atcf_modified_wind_radii(
    filename: str, wr: int, fcst: bool = True, btk: bool = True
) -> List[Any]:
    storm_info = get_info_from_filename(filename=f"{adecks_datadir}{filename}")

    if fcst:
        current_filename = (
            f"{adecks_datadir}wind_radii/{filename[:-4]}_{wr}kt{filename[-4:]}"
        )
        if os.path.isfile(current_filename):
            df_fcst = pd.read_csv(current_filename, header=0, delimiter=",")
            df_fcst.Date = pd.to_datetime(df_fcst.Date)
            df_fcst["Valid"] = df_fcst.Date + pd.to_timedelta(
                df_fcst.FcstHour, unit="hr"
            )
        else:
            df_fcst = None
    else:
        df_fcst = None

    if btk:
        current_filename = (
            f"{bdecks_datadir}wind_radii/{filename[:-4]}_{wr}kt{filename[-4:]}"
        )
        if os.path.isfile(current_filename):
            df_btk = pd.read_csv(current_filename, header=0, delimiter=",")
            df_btk.Date = pd.to_datetime(df_btk.Date)
            df_btk["Valid"] = df_btk.Date + pd.to_timedelta(df_btk.FcstHour, unit="hr")
        else:
            df_btk = None
    else:
        df_btk = None

    return storm_info, df_fcst, df_btk


def read_saildrone_latest_position():
    datadir = (
        "/Users/asavarin/Desktop/saildrone/scripts/rapid_deployment/saildrone_data"
    )
    fls = sorted(os.listdir(datadir))

    sd_data = {}

    for fl in fls:
        sd_number = fl.split("_")[0][2:]
        data = Dataset(f"{datadir}/{fl}", "r")
        lat = np.array(data["latitude"])
        lon = np.array(data["longitude"])
        data.close()
        lat = lat[~np.isnan(lat)]
        lon = lon[~np.isnan(lon)]
        dlat = lat[-1] - lat[-2]
        dlon = lon[-1] - lon[-2]
        dir = (90 + (360 - (np.rad2deg(np.arctan2(dlat, dlon)) % 360))) % 360

        sd_data[sd_number] = {
            "lon": lon[-1],
            "lat": lat[-1],
            "dir": dir,
        }

    return sd_data


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
