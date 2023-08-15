
import numpy as np
import os
import pandas as pd
import shapely.geometry as shp

from cartopy.geodesic import Geodesic
from paths import repo_path
from typing import Any, List 

geod = Geodesic()

adecks_datadir = f"{repo_path}{os.sep}data{os.sep}hurricane_forecasts{os.sep}atcf_a{os.sep}"
bdecks_datadir = f"{repo_path}{os.sep}data{os.sep}hurricane_forecasts{os.sep}atcf_b{os.sep}"

adecks_datadir = f"/Users/asavarin/Desktop/saildrone/data/hurricane_forecasts/atcf_a/preprocessed/"
bdecks_datadir = "/Users/asavarin/Desktop/saildrone/data/hurricane_forecasts/atcf_b/preprocessed/"


def convert_wind_radii_to_polygon(forecast=pd.DataFrame) -> shp.Polygon:

    if forecast.WSPRadius1 > 0:
        cp_ne = np.asarray(geod.circle(lon=forecast.Center.x, lat=forecast.Center.y, radius=forecast.WSPRadius1*1852., endpoint=True, n_samples=1000))[750:]
    else: 
        cp_ne = np.array([forecast.Center.x, forecast.Center.y])
    if forecast.WSPRadius2 > 0:
        cp_se = np.asarray(geod.circle(lon=forecast.Center.x, lat=forecast.Center.y, radius=forecast.WSPRadius2*1852., endpoint=True, n_samples=1000))[500:751]
    else: 
        cp_se = np.array([forecast.Center.x, forecast.Center.y])
    if forecast.WSPRadius3 > 0:
        cp_sw = np.asarray(geod.circle(lon=forecast.Center.x, lat=forecast.Center.y, radius=forecast.WSPRadius3*1852., endpoint=True, n_samples=1000))[250:501]
    else: 
        cp_sw = np.array([forecast.Center.x, forecast.Center.y])
    if forecast.WSPRadius4 > 0:
        cp_nw = np.asarray(geod.circle(lon=forecast.Center.x, lat=forecast.Center.y, radius=forecast.WSPRadius4*1852., endpoint=True, n_samples=1000))[:251]
    else: 
        cp_nw = np.array([forecast.Center.x, forecast.Center.y])

    all_pts = np.vstack((cp_nw, cp_sw, cp_se, cp_ne))

    return shp.Polygon(all_pts)





def get_atcf_files(wr=False) -> List:

    fls_a = sorted([fl for fl in os.listdir(adecks_datadir) if ".dat" in fl])
    fls_b = sorted([fl for fl in os.listdir(bdecks_datadir) if ".dat" in fl])

    fls = [fl for fl in fls_a if fl in fls_b]

    return fls


def get_info_from_filename(filename:str):
    if "/" in filename:
        filename = filename.split("/")[-1]
    
    storm_basin = filename[0:2]
    storm_number = int(filename[8:10])
    storm_year = int(filename[3:7])


    return {
        "basin": storm_basin,
        "number": storm_number,
        "year": storm_year
    }


def read_atcf_modified_wind_radii(filename: str, wr: int) -> List[Any]:

    storm_info = get_info_from_filename(filename=f"{adecks_datadir}{filename}")

    df_fcst = pd.read_csv(f"{adecks_datadir[:-13]}wind_radii/wr_{wr:02d}/{filename}", header=0, delimiter=",")
    df_fcst.Date = pd.to_datetime(df_fcst.Date)
    df_fcst.Valid = pd.to_datetime(df_fcst.Valid)

    df_btk = pd.read_csv(f"{bdecks_datadir[:-13]}wind_radii/wr_{wr:02d}/{filename}", header=0, delimiter=",")
    df_btk.Date = pd.to_datetime(df_btk.Date)
    df_btk.Valid = pd.to_datetime(df_btk.Valid)

    return storm_info, df_fcst, df_btk
