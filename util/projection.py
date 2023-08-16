
import pandas as pd
from math import radians, sin, cos, acos


proj="A"


def great_circle_distance(lon: float, lat: float, lon_point: float, lat_point: float) -> float:

    lon1, lat1, lon2, lat2 = map(radians, [lon_point, lat_point, lon, lat])
    r_earth = 6371.
    gc = r_earth * (acos(sin(lat1) * sin(lat2) + cos(lat1)*cos(lat2)*cos(lon1-lon2)))

    return gc


def set_cartopy_projection_atlantic():
    ...

