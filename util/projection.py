
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import requests

from bs4 import BeautifulSoup
from cartopy.feature import COASTLINE, LAND
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from math import radians, sin, cos, acos
from paths import url_buoy_info
from typing import List

proj = ccrs.PlateCarree(central_longitude = 0)


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


def set_cartopy_projection_atlantic(
        ax: plt.Axes,
        extent: List[float] = [-111, 11, -5, 55],
        xticks: np.ndarray = np.arange(-120, 30, 10),
        yticks: np.ndarray = np.arange(-10, 61, 10),
        ylabel: str = "top"
    ):
    #ax.coastlines(color="k", zorder=1)
    ax.add_feature(COASTLINE.with_scale('10m'), edgecolor="k")
    ax.add_feature(LAND.with_scale('10m'), facecolor='.8')
    gl = ax.gridlines(
        crs = proj,
        draw_labels = True,
        linewidth = 1,
        color = "gray",
        alpha = 1,
        linestyle = "--"
    )
    gl.xlocator = mticker.FixedLocator(xticks)
    gl.ylocator = mticker.FixedLocator(yticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    if ylabel == "top":
        gl.top_labels = True
    else:
        gl.top_labels = False

    if ylabel == "bottom":
        gl.bottom_labels = True
    else:
        gl.bottom_labels = False
    gl.right_labels = False

    ax.set_extent(extent, crs=proj)
