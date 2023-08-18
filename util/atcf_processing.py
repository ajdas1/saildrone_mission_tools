import geopandas as gpd
import numpy as np
import os
import pandas as pd
import pytz
import shapely.geometry as shp
import urllib.error
import urllib.request
import zipfile


import importlib
import paths
importlib.reload(paths)
import conversions
importlib.reload(conversions)

from bs4 import BeautifulSoup
from cartopy.geodesic import Geodesic
from conversions import convert_time_to_utc
from datetime import datetime, timedelta
from paths import nhc_outlook_archive, repo_path
from shapely.ops import polygonize
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


def count_overlapping_features(geo_dataset: gpd.geopandas.GeoDataFrame):

    polygon_bounds = geo_dataset.geometry.convex_hull.exterior.buffer(1e6).unary_union
    polygon_bounds = geo_dataset.geometry.exterior.unary_union
    new_polygons = list(polygonize(polygon_bounds))
    new_gdf = gpd.GeoDataFrame(geometry=new_polygons)
    new_gdf["id"] = range(len(new_gdf))

    new_gdf_centroid = new_gdf.copy()
    new_gdf_centroid['geometry'] = new_gdf.centroid
    new_gdf_centroid = new_gdf_centroid.set_crs("epsg:3857")
    overlapcount = gpd.sjoin(new_gdf_centroid, geo_dataset)
    overlapcount = overlapcount.groupby(['id'])['index_right'].count().rename('count').reset_index()
    out_gdf = pd.merge(new_gdf,overlapcount)

    return out_gdf





def split_storms_into_wind_radii(storm_wr: gpd.geopandas.GeoDataFrame):
    storm_wr = [gpd.GeoDataFrame(bdw) for bdw in storm_wr]
    storm_wr = [bdw.set_geometry("WindRadii") for bdw in storm_wr]
    tmp = []
    for storm in storm_wr:
        tmp_union = storm.WindRadii.unary_union
        if isinstance(tmp_union, shp.polygon.Polygon):
            tmp.append([tmp_union])
        elif tmp_union is not None:
            tmp_independent = [geom for geom in tmp_union.geoms]
            tmp.append(tmp_independent)
    tmp = [i for j in tmp for i in j]
    storm = gpd.GeoDataFrame(tmp, columns=["Storms"])
    storm = storm.set_geometry("Storms")
    storm = storm.set_crs("epsg:3857")

    return storm



def subset_btk_in_region(btk: pd.DataFrame, target_region: shp.Polygon, wr: int = 0, verbose: bool = True) -> dict:
    btks_track = []
    btks_start = []
    for _, btk in enumerate(btk):
        btk["InRange"] = btk["Center"].apply(target_region.contains)
        if btk.InRange.sum() > 0:
            btks_track.append(btk)
            if btk.InRange.iloc[0]:
                btks_start.append(btk)
    
    if verbose:
        print(f"Storms that start in region: {len(btks_start)}")

    return {
        "start": btks_start,
        "track": btks_track
        }





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



def read_shapefile_areas(directory: str) -> gpd.GeoDataFrame:

    fls = [fl for fl in os.listdir(directory) if ".shp" in fl and ".xml" not in fl]
    fl_areas = [fl for fl in fls if "areas" in fl][0]

    df_areas = gpd.read_file(f"{directory}/{fl_areas}")
    df_areas = df_areas.set_geometry("geometry")

    return df_areas


def unzip_shapefile(filename: str, savefile: str = "", overwrite: bool = True, remove: bool = True) -> str:

    if savefile == "":
        savefile = filename[:-4]
    
    if not os.path.isdir(savefile):
        os.mkdir(savefile)
    else:
        if not overwrite:
            print("Directory for zip extraction exists. Did not overwrite.")
            return

    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(savefile)

    if remove:
        os.remove(filename)
    
    return savefile



def download_outlook_shapefile(time: str, savedir: str) -> List[str]:
    url_data = urllib.request.urlopen(nhc_outlook_archive).read()
    soup = BeautifulSoup(url_data, "html.parser")    
    files = [nhc_outlook_archive + node.get('href') for node in soup.find_all("a")]
    files = [path for path in files if len(path.split("/")) == 8 and "latest" not in path]
    modified_time = [convert_time_to_utc(time=datetime.strptime(tm.split("/")[-2], "%Y%m%d%H%M"), timezone=pytz.timezone("UTC")) for tm in files]

    time_threshold_hours = 24
    matching_times = [tm for tm in modified_time if tm >= (time - timedelta(hours=time_threshold_hours))]
    if len(matching_times) > 0:
        most_recent_time = max(matching_times)
        most_recent_idx = modified_time.index(most_recent_time)
        most_recent_file = files[most_recent_idx]
        filename = f"{savedir}/{most_recent_time.strftime('%Y%m%d%H%M')}.zip"

        try:
            urllib.request.urlretrieve(most_recent_file+"gtwo_shapefiles.zip", filename)
            return filename, most_recent_time
        except urllib.error.HTTPError:
            pass
    
    else:
        return None, None



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
