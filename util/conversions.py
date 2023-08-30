import numpy as np
import pandas as pd
import pytz
import shapely.geometry as shp

from cartopy.geodesic import Geodesic
from datetime import datetime


def get_aircraft_recon_position(value: str):

    val = int(value[:-1])
    val_degrees = val // 100
    val_minutes = val % 100
    val = float(val_degrees) + float(val_minutes) / 60

    if ("N" in value) or ("E" in value):
        factor = 1
    elif ("S" in value) or ("W" in value):
        factor = -1

    return val * factor


def get_aircraft_recon_pressure(value: str):
    try:
        val = int(value) / 10.0
        if val < 100.0:
            val += 1000.0
    except ValueError:
        val = np.nan

    return val


def get_mission_names_form_tidbits_link(url: str):
    params = url.split("/")[-1].split("_")[-1].split(".txt")[0].split("-")
    storm = params[2]
    if ".csv" in storm:
        storm = storm.split(".")[0]

    return {"aircraft": params[0], "time": params[1], "storm": storm}


def convert_time_to_utc(
    time: datetime, timezone=pytz.timezone("US/Eastern")
) -> datetime:
    tz_time = timezone.localize(time, is_dst=True)
    utc_time = tz_time.astimezone(pytz.utc)

    return utc_time


def convert_wind_radii_to_polygon(forecast=pd.DataFrame) -> shp.Polygon:
    geod = Geodesic()
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


def get_centroid_coordinates(shapefile_point):
    return shapefile_point.representative_point().coords[:][0]


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
