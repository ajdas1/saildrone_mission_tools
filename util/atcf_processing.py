import numpy as np
import os
import pandas as pd
import shapely.geometry as shp

from cartopy.geodesic import Geodesic
from paths import repo_path
from typing import Any, Dict, List

geod = Geodesic()

adecks_datadir = (
    f"{repo_path}{os.sep}data{os.sep}hurricane_forecasts{os.sep}adecks{os.sep}"
)
bdecks_datadir = (
    f"{repo_path}{os.sep}data{os.sep}hurricane_forecasts{os.sep}bdecks{os.sep}"
)

column_names = [
    "Basin",
    "StormNumber",
    "Date",
    "Technum",
    "FcstCenter",
    "FcstHour",
    "Latitude",
    "Longitude",
    "MaxSustainedWind",
    "MinSLP",
    "StormType",
    "WindIntensityForRadii",
    "WindCode",
    "WSPRadius1",
    "WSPRadius2",
    "WSPRadius3",
    "WSPRadius4",
    "PressureOfLastClosedIsobar",
    "RadiusOfLastClosedIsobar",
    "RMW",
    "Gust",
    "EyeDiameter",
    "SubregionCode",
    "MaxSeas",
    "ForecasterInitials",
    "StormDirection",
    "StormSpeed",
    "StormName",
    "StormDepth",
    "WaveHeightForRadius",
    "RadiusQuadrantCode",
    "SeasRadius1",
    "SeasRadius2",
    "SeasRadius3",
    "SeasRadius4",
    "x",
    "xx",
    "xxx",
    "xxxx",
    "xxxxx",
    "xxxxxx",
    "xxxxxxx",
    "xxxxxxxx",
    "xxxxxxxxx",
    "y",
    "yy",
]
column_types = {
    "Basin": str,
    "StormNumber": "Int64",
    "Date": str,
    "Technum": "Int64",
    "FcstCenter": str,
    "FcstHour": "Int64",
    "Latitude": str,
    "Longitude": str,
    "MaxSustainedWind": float,
    "MinSLP": "Int64",
    "StormType": str,
    "WindIntensityForRadii": "Int64",
    "WindCode": str,
    "WSPRadius1": float,
    "WSPRadius2": float,
    "WSPRadius3": float,
    "WSPRadius4": float,
    "PressureOfLastClosedIsobar": "Int64",
    "RadiusOfLastClosedIsobar": "Int64",
    "RMW": "Int64",
    "Gust": "Int64",
    "EyeDiameter": "Int64",
    "SubregionCode": str,
    "MaxSeas": str,
    "ForecasterInitials": str,
    "StormDirection": "Int64",
    "StormSpeed": "Int64",
    "StormName": str,
    "StormDepth": str,
    "WaveHeightForRadius": "Int64",
    "RadiusQuadrantCode": str,
    "SeasRadius1": "Int64",
    "SeasRadius2": "Int64",
    "SeasRadius3": "Int64",
    "SeasRadius4": "Int64",
    "x": str,
    "xx": str,
    "xxx": str,
    "xxxx": str,
    "xxxxx": str,
    "xxxxxx": str,
    "xxxxxxx": str,
    "xxxxxxxx": str,
    "xxxxxxxxx": str,
    "y": str,
    "yy": str,
}


def fix_atcf_latitude(val: str) -> float:
    """
    Converts latitude values from ATCF to floats.

    Arguments:
    - val: string

    Returns:
    - float
    """
    if val.endswith("S"):
        x = -float(val.strip("S"))
    elif val.endswith("N"):
        x = float(val.strip("N"))
    else:
        x = float(val.strip())
    return x / 10.0


def fix_atcf_longitude(val: str) -> float:
    """
    Converts longitude values from ATCF to floats.

    Arguments:
    - val: string

    Returns:
    - float
    """
    if val.endswith("W"):
        x = -float(val.strip("W"))
    elif val.endswith("E"):
        x = float(val.strip("E"))
    else:
        x = float(val.strip(""))
    return x / 10.0


def convert_wind_radii_to_polygon(forecast: pd.DataFrame) -> shp.Polygon:
    """
    Converts four given wind radii into a polygon.

    Arguments:
    - forecast: pd.DataFrame

    Returns:
    - shapely Polygon
    """

    if forecast.WSPRadius1 > 0:
        cp_ne = np.asarray(
            geod.circle(
                lon=forecast.Center.x,
                lat=forecast.Center.y,
                radius=forecast.WSPRadius1 * 1852.0,
                endpoint=True,
                n_samples=1000,
            )
        )[750:]
    else:
        cp_ne = np.array([forecast.Center.x, forecast.Center.y])
    if forecast.WSPRadius2 > 0:
        cp_se = np.asarray(
            geod.circle(
                lon=forecast.Center.x,
                lat=forecast.Center.y,
                radius=forecast.WSPRadius2 * 1852.0,
                endpoint=True,
                n_samples=1000,
            )
        )[500:751]
    else:
        cp_se = np.array([forecast.Center.x, forecast.Center.y])
    if forecast.WSPRadius3 > 0:
        cp_sw = np.asarray(
            geod.circle(
                lon=forecast.Center.x,
                lat=forecast.Center.y,
                radius=forecast.WSPRadius3 * 1852.0,
                endpoint=True,
                n_samples=1000,
            )
        )[250:501]
    else:
        cp_sw = np.array([forecast.Center.x, forecast.Center.y])
    if forecast.WSPRadius4 > 0:
        cp_nw = np.asarray(
            geod.circle(
                lon=forecast.Center.x,
                lat=forecast.Center.y,
                radius=forecast.WSPRadius4 * 1852.0,
                endpoint=True,
                n_samples=1000,
            )
        )[:251]
    else:
        cp_nw = np.array([forecast.Center.x, forecast.Center.y])

    all_pts = np.vstack((cp_nw, cp_sw, cp_se, cp_ne))

    return shp.Polygon(all_pts)


def get_atcf_files() -> List:
    """
    Finds a list of storms that have both forecast and best track data.

    Returns:
    - list
    """

    fls_a = sorted(
        [fl for fl in os.listdir(f"{adecks_datadir}{os.sep}downloaded") if ".dat" in fl]
    )
    fls_b = sorted(
        [fl for fl in os.listdir(f"{bdecks_datadir}{os.sep}downloaded") if ".dat" in fl]
    )

    fls = [fl for fl in fls_a if fl in fls_b]

    return fls


# def get_info_from_filename(filename: str) -> Dict:
#     if "/" in filename:
#         filename = filename.split("/")[-1]

#     storm_basin = filename[0:2]
#     storm_number = int(filename[8:10])
#     storm_year = int(filename[3:7])


#     return {
#         "basin": storm_basin,
#         "number": storm_number,
#         "year": storm_year
#     }


# def read_atcf_modified_wind_radii(filename: str, wr: int) -> List[Any]:

#     storm_info = get_info_from_filename(filename=f"{adecks_datadir}{filename}")

#     df_fcst = pd.read_csv(f"{adecks_datadir[:-13]}wind_radii/wr_{wr:02d}/{filename}", header=0, delimiter=",")
#     df_fcst.Date = pd.to_datetime(df_fcst.Date)
#     df_fcst.Valid = pd.to_datetime(df_fcst.Valid)

#     df_btk = pd.read_csv(f"{bdecks_datadir[:-13]}wind_radii/wr_{wr:02d}/{filename}", header=0, delimiter=",")
#     df_btk.Date = pd.to_datetime(df_btk.Date)
#     df_btk.Valid = pd.to_datetime(df_btk.Valid)

#     return storm_info, df_fcst, df_btk
