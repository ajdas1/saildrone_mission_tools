import requests

from bs4 import BeautifulSoup

from math import radians, sin, cos, acos
from paths import url_buoy_info

proj = "A"


def great_circle_distance(
    lon: float, lat: float, lon_point: float, lat_point: float
) -> float:
    lon1, lat1, lon2, lat2 = map(radians, [lon_point, lat_point, lon, lat])
    r_earth = 6371.0
    gc = r_earth * (
        acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
    )

    return gc


def get_ndbc_buoy_position(config: dict) -> dict:
    page = requests.get(f"{url_buoy_info}{config['comparison_buoy']}").text
    soup = BeautifulSoup(page, "html.parser")
    record = [
        node.get("content")
        for node in soup.find_all("meta")
        if f"buoy {config['comparison_buoy']}" in node.get("content")
    ][0]
    buoy_loc = record.split(" - ")[1]
    buoy_loc = buoy_loc[buoy_loc.index("(") + 1 : buoy_loc.index(")")].split(" ")
    buoy_latitude = float(buoy_loc[0][:-1])
    buoy_longitude = float(buoy_loc[1][:-1])
    if buoy_loc[0][-1] == "S":
        buoy_latitude *= -1
    if buoy_loc[1][-1] == "W":
        buoy_longitude *= -1

    return {"lon": buoy_longitude, "lat": buoy_latitude}


def set_cartopy_projection_atlantic():
    ...
