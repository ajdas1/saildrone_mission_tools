import numpy as np
import pandas as pd
import pytz
import shapely.geometry as shp
import xarray as xr

from cartopy.geodesic import Geodesic     
from datetime import datetime
from typing import List




def convert_time_to_utc(time: datetime, timezone = pytz.timezone("US/Eastern")) -> datetime:
    tz_time = timezone.localize(time, is_dst=True)
    utc_time = tz_time.astimezone(pytz.utc)
    
    return utc_time




def convert_wind_radii_to_polygon(forecast=pd.DataFrame) -> shp.Polygon:
    geod = Geodesic()
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
