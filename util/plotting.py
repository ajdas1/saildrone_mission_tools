



import geopandas as gpd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

import importlib
import conversions
importlib.reload(conversions)
import projection
importlib.reload(projection)



from conversions import get_centroid_coordinates
from datetime import datetime
from matplotlib import rc
from matplotlib.colors import ListedColormap
from matplotlib.gridspec import GridSpec
from projection import proj, set_cartopy_projection_atlantic
from typing import List



def plot_invest_winds(data: pd.DataFrame, filename: str):

    aids_to_use = ["CARQ", "OFCL", "AVNI", "CMCI", "CTCI", "DSHP", "EGRI", "EMXI", "FSSE", "GFSI", "HCCA", "HMNI", "HWFI", "ICON", "IVCN", "LGEM", "NVGI"] 

    data = data[data.FcstCenter.isin(aids_to_use)]
    products = data.FcstCenter.unique()
    colors = plt.cm.turbo(np.linspace(0, 1, len(aids_to_use)))
    pcolors = {aids_to_use[idx]: colors[idx] for idx in range(len(aids_to_use))}
    pcolors["CARQ"] = "k"


    fig = plt.figure(figsize = (8, 4))
    ax_mwsp = fig.add_subplot(111)

    ax_mwsp.grid(True, which="both", linewidth=.5, linestyle="dashed", color=".7")

    ax_mwsp.axhline(34, c="k", lw=1)
    ax_mwsp.axhline(64, c="k", lw=1)
    ax_mwsp.axvline(data[(data.FcstCenter=="CARQ") & (data.FcstHour>=0)].Valid.min(), c="k", lw=.5)
    ax_mwsp.text(data.Valid.max(), 34, "34kt", ha="right", va="bottom", fontweight="semibold")
    ax_mwsp.text(data.Valid.max(), 64, "64kt", ha="right", va="bottom", fontweight="semibold")

    for product in products:
        ax_mwsp.plot(data[(data.FcstCenter==product) & (data.FcstHour>=0)].Valid, data[(data.FcstCenter==product) & (data.FcstHour>=0)].MaxSustainedWind, linewidth=1.5, marker="o", markersize=4, c=pcolors[product], label=product)

    ax_mwsp.plot(data[(data.FcstCenter=="CARQ") & (data.FcstHour<=0)].Valid, data[(data.FcstCenter=="CARQ") & (data.FcstHour<=0)].MaxSustainedWind, c="k", lw=2)

    ax_mwsp.legend(loc=2, fontsize=7, ncol=np.ceil(len(products)/8))

    ax_mwsp.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    ax_mwsp.xaxis.set_minor_locator(mdates.HourLocator(interval=6))
    ax_mwsp.xaxis.set_major_locator(mdates.HourLocator(interval=24))


    ax_mwsp.set_title(f"INVEST AL{data.StormNumber.iloc[0]}: {data.Date.iloc[0].strftime('%Y-%m-%d %H')} UTC - Maximum Sustained Winds (kt)")
    ax_mwsp.set_ylim(bottom=0)
    ax_mwsp.set_xlim(data.Valid.min(), data.Valid.max())
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close("all")







def plot_invest_track(data: pd.DataFrame, filename: str):
    
    aids_to_use = ["CARQ", "OFCL", "NVGI", "AVNI", "GFSI", "EMXI",
                   "EGRI", "CMCI", "HWFI", "CTCI", "HFAI", "HFBI" 
                   "HMNI", "AEMI", "UEMI", "EMN2", "TVCN", "GFEX", "TVCX"] 

    data = data[data.FcstCenter.isin(aids_to_use)]
    products = data.FcstCenter.unique()
    colors = plt.cm.turbo(np.linspace(0, 1, len(aids_to_use)))
    pcolors = {aids_to_use[idx]: colors[idx] for idx in range(len(aids_to_use))}
    pcolors["CARQ"] = "k"


    fig = plt.figure(figsize = (12, 5))
    ax = fig.add_subplot(111, projection=proj)
    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")

    for product in products:
        ax.plot(data[(data.FcstCenter==product) & (data.FcstHour>=0)].Longitude, data[(data.FcstCenter==product) & (data.FcstHour>=0)].Latitude, linewidth=1.5, marker="o", markersize=3, c=pcolors[product], label=product)

    ax.plot(data[(data.FcstCenter=="CARQ") & (data.FcstHour<=0)].Longitude, data[(data.FcstCenter=="CARQ") & (data.FcstHour<=0)].Latitude, c="k", lw=2)
    ax.plot(data[(data.FcstCenter=="CARQ") & (data.FcstHour==0)].Longitude, data[(data.FcstCenter=="CARQ") & (data.FcstHour==0)].Latitude, marker="x", color="r", markersize=7, mew=2)

    ax.legend(loc=1, fontsize=7, ncol=np.ceil(len(products)/25))

    ax.set_title(f"INVEST AL{data.StormNumber.iloc[0]}: {data.Date.iloc[0].strftime('%Y-%m-%d %H')} UTC")
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close("all")




def plot_shapefile_btkstart(
        shapefile_data: pd.DataFrame, wind_overlap: dict, 
        n: int, n_storms: int, time: datetime, savedir: str,
        sd_data: dict = None, percentage: bool = False, title_save_add: str = "",
    ) -> plt.figure:

    if not isinstance(shapefile_data, gpd.geodataframe.GeoDataFrame):
        shapefile_data = gpd.GeoDataFrame(shapefile_data).T
        shapefile_data = shapefile_data.set_geometry("geometry")

    if percentage:
        label_title = "%"
        save_add = "perc_"
        vmin = 0
        vmax = 20    
        cmap = plt.cm.tab20b(np.linspace(0, 1, 20))
        cmap = ListedColormap(cmap)
        overlap_column = "percentage"
        title_add = f"\n% of storms starting in area (n={n_storms})"
    else:
        label_title = "#"
        save_add = ""
        vmin = 0
        vmax = 10
        cmap = plt.cm.turbo(np.linspace(0, 1, 10))
        cmap = ListedColormap(cmap)
        overlap_column = "count"
        title_add = f"\n# of storms starting in area (n={n_storms})"
    
    area_colors = find_outlook_area_color(shapefile_data=shapefile_data)
    shapefile_data["coords"] = shapefile_data["geometry"].apply(get_centroid_coordinates)

    fig = plt.figure(figsize = (12, 5))
    ax = fig.add_subplot(111, projection=proj)

    shapefile_data["geometry"].plot(ax=ax, color=area_colors, alpha=.5, edgecolor="k")
    for _, row in shapefile_data.iterrows():
        ax.annotate(text=row['AREA'], xy=row["coords"], ha="center", va="center", fontweight="bold", fontsize=10)

    for idx, row in shapefile_data.iterrows():
        annotate_text = f"Area {row['AREA']}\n2 day: {row['PROB2DAY']}\n7 day: {row['PROB7DAY']}"
        ax.annotate(text=annotate_text, xy=(-110 + idx*20, 3), ha="left", va="top", backgroundcolor=(1, 1, 1, .5), fontsize=10)

    legend_kwds = {"pad": 0.015, "shrink": 0.99, "label": f"storm {label_title}"}
    if len(wind_overlap) > 0:
        wind_overlap.plot(
            column=overlap_column, ax=ax, legend=False, alpha=.8, 
            vmin=vmin, vmax=vmax, legend_kwds=legend_kwds, cmap=cmap
        )

    ax.plot([130, 140], [0, 1], c="yellow", alpha=.5, lw=10, label="Low (<40%)")
    ax.plot([130, 140], [0, 1], c="orange", alpha=.5, lw=10, label="Medium (40-60%)")
    ax.plot([130, 140], [0, 1], c="red", alpha=.5, lw=10, label="High (>60%)")

    if sd_data is not None:
        for sd in sd_data:
            ax.plot(sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10)
            ax.arrow(sd_data[sd]["lon"], sd_data[sd]["lat"], 
                np.cos(np.deg2rad(90-sd_data[sd]["dir"])), np.sin(np.deg2rad(90-sd_data[sd]["dir"])), 
                length_includes_head=True, head_width=0.5, color="m", head_length=0.5, zorder=10)
        ax.plot(130, 0, "om", markersize=2, label="SD")

    plot_saildrone_mission_domains(ax=ax)

    ax.legend(loc=1)
    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")
    ax.set_title(f"7-day outlook areas: {time.strftime('%Y-%m-%d %H:%M')} UTC{title_add} ({title_save_add[1:]})")

    plt.savefig(f"{savedir}{os.sep}outlook_areas_btks_{save_add}area{n}{title_save_add}.png", dpi=200, bbox_inches="tight")
    plt.close("all")



def find_outlook_area_color(shapefile_data: gpd.GeoDataFrame) -> List:
    colors = []
    for n in range(len(shapefile_data)):
        current_area = shapefile_data.iloc[n]
        if current_area.RISK7DAY == "Low":
            colors.append("yellow")
        elif current_area.RISK7DAY == "Medium":
            colors.append("orange")
        elif current_area.RISK7DAY == "High":
            colors.append("red")
    
    return colors



def plot_shapefile(shapefile_data: gpd.GeoDataFrame, time: datetime, savedir: str, sd_data: dict = None):

    area_colors = find_outlook_area_color(shapefile_data=shapefile_data)


    shapefile_data["coords"] = shapefile_data["geometry"].apply(get_centroid_coordinates)

    fig = plt.figure(figsize = (12, 12))
    ax = fig.add_subplot(111, projection=proj)

    shapefile_data.plot(ax=ax, color=area_colors, alpha=.5, edgecolor="k")
    for _, row in shapefile_data.iterrows():
        ax.annotate(text=row['AREA'], xy=row["coords"], ha="center", va="center", fontweight="bold")

    for idx, row in shapefile_data.iterrows():
        annotate_text = f"Area {row['AREA']}\n2 day: {row['PROB2DAY']}\n7 day: {row['PROB7DAY']}"
        ax.annotate(text=annotate_text, xy=(-110 + idx*20, 1.5), ha="left", va="top", fontweight="semibold", backgroundcolor=(1, 1, 1, .5))

    ax.plot([130, 140], [0, 1], c="yellow", alpha=.5, lw=10, label="Low (<40%)")
    ax.plot([130, 140], [0, 1], c="orange", alpha=.5, lw=10, label="Medium (40-60%)")
    ax.plot([130, 140], [0, 1], c="red", alpha=.5, lw=10, label="High (>60%)")

    if sd_data is not None:
        for sd in sd_data:
            ax.plot(sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10)
            ax.arrow(sd_data[sd]["lon"], sd_data[sd]["lat"], 
                np.cos(np.deg2rad(90-sd_data[sd]["dir"])), np.sin(np.deg2rad(90-sd_data[sd]["dir"])), 
                length_includes_head=True, head_width=0.5, color="m", head_length=0.5, zorder=10)
        ax.plot(130, 0, "om", markersize=2, label="SD")


    ax.legend()

    plot_saildrone_mission_domains(ax=ax)

    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")
    ax.set_title(f"7-day outlook areas: {time.strftime('%Y-%m-%d %H:%M')} UTC")

    plt.savefig(f"{savedir}{os.sep}outlook_areas.png", dpi=200, bbox_inches="tight")
    plt.close("all")







def plot_saildrone_mission_domains(ax: plt.axis):

    # Mission Domain A
    ax.plot([-55.11, -46.83], [20.40, 20.40], c="k", lw=.7)
    ax.plot([-46.83, -46.85], [20.40, 13.50], c="k", lw=.7)
    ax.plot([-46.85, -55.14], [13.50, 13.50], c="k", lw=.7)
    ax.plot([-55.14, -55.11], [13.50, 20.40], c="k", lw=.7)
    ax.text(-46.83, 20.40, "A", fontweight="semibold", ha="right", va="top", fontsize=6, zorder=20)
    # Mission Domain B
    ax.plot([-67.56, -65.50], [17.63, 17.63], c="k", lw=.7)
    ax.plot([-65.50, -65.51], [17.63, 16.09], c="k", lw=.7)
    ax.plot([-65.51, -67.57], [16.09, 16.09], c="k", lw=.7)
    ax.plot([-67.57, -67.56], [16.09, 17.63], c="k", lw=.7)
    ax.text(-65.50, 17.63, "B", fontweight="semibold", ha="right", va="top", fontsize=6, zorder=20)
    # Mission Domain C
    ax.plot([-66.80, -65.94], [21.80, 21.79], c="k", lw=.7)
    ax.plot([-65.94, -65.90], [21.79, 18.77], c="k", lw=.7)
    ax.plot([-65.90, -66.84], [18.77, 18.76], c="k", lw=.7)
    ax.plot([-66.84, -66.80], [18.76, 21.80], c="k", lw=.7)
    ax.text(-65.94, 21.79, "C", fontweight="semibold", ha="right", va="top", fontsize=6, zorder=20)
    # Mission Domain D
    ax.plot([-66.24, -63.23], [28.50, 28.51], c="k", lw=.7)
    ax.plot([-63.23, -63.22], [28.51, 26.27], c="k", lw=.7)
    ax.plot([-63.22, -66.22], [26.27, 26.26], c="k", lw=.7)
    ax.plot([-66.22, -66.24], [26.26, 28.50], c="k", lw=.7)
    ax.text(-63.23, 28.51, "D", fontweight="semibold", ha="right", va="top", fontsize=6, zorder=20)
    # Mission Domain EE
    ax.plot([-75.5, -74], [33, 33], c="k", lw=.7)
    ax.plot([-74, -74], [33, 31.5], c="k", lw=.7)
    ax.plot([-74, -75.5], [31.5, 31.5], c="k", lw=.7)
    ax.plot([-75.5, -75.5], [31.5, 33], c="k", lw=.7)
    ax.text(-74, 33, "EE", fontweight="semibold", ha="right", va="top", fontsize=6, zorder=20)
    # Mission Domain F
    ax.plot([-89, -83.85], [28, 28.74], c="k", lw=.7)
    ax.plot([-83.85, -82.23], [28.74, 25.52], c="k", lw=.7)
    ax.plot([-82.23, -88.34], [25.52, 25.80], c="k", lw=.7)
    ax.plot([-88.34, -89], [25.80, 28], c="k", lw=.7)
    ax.text(-88.34, 25.80, "F", fontweight="semibold", ha="right", va="top", fontsize=6, zorder=20)

    # Mission Domain E
    ax.plot([-78.87, -77.49], [32.66, 33.39], c="k", lw=.7)
    ax.plot([-77.49, -76.68], [33.39, 34.07], c="k", lw=.7)
    ax.plot([-76.68, -75.79], [34.07, 34.52], c="k", lw=.7)
    ax.plot([-75.79, -75.50], [34.52, 34.40], c="k", lw=.7)
    ax.plot([-75.50, -76.28], [34.40, 33.63], c="k", lw=.7)
    ax.plot([-76.28, -77.17], [33.63, 32.84], c="k", lw=.7)
    ax.plot([-77.17, -78.29], [32.84, 32.01], c="k", lw=.7)
    ax.plot([-78.29, -79.02], [32.01, 31.54], c="k", lw=.7)
    ax.plot([-79.02, -79.39], [31.54, 31.10], c="k", lw=.7)
    ax.plot([-79.39, -79.73], [31.10, 30.65], c="k", lw=.7)
    ax.plot([-79.73, -80.19], [30.65, 31.17], c="k", lw=.7)
    ax.plot([-80.19, -79.77], [31.17, 31.94], c="k", lw=.7)
    ax.plot([-79.77, -78.87], [31.94, 32.66], c="k", lw=.7)
    ax.text(-75.50, 34.40, "E", fontweight="semibold", ha="left", va="bottom", fontsize=6, zorder=20)




def plot_saildrone_buoy_comparison(data: pd.DataFrame, config: dict, filename: str):
    rc("text", usetex=True)
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3)
    gs.update(hspace=0.3)
    ax_dist = fig.add_subplot(gs[0, 0])
    ax_wdir = fig.add_subplot(gs[0, 1], sharex=ax_dist)
    ax_wspd = fig.add_subplot(gs[0, 2], sharex=ax_dist)
    ax_atmp = fig.add_subplot(gs[1, 0], sharex=ax_dist)
    ax_rhum = fig.add_subplot(gs[1, 1], sharex=ax_dist)
    ax_pres = fig.add_subplot(gs[1, 2], sharex=ax_dist)
    ax_otmp = fig.add_subplot(gs[2, 0], sharex=ax_dist)
    ax_dwpd = fig.add_subplot(gs[2, 1], sharex=ax_dist)
    ax_wvht = fig.add_subplot(gs[2, 2], sharex=ax_dist)

    ax_dist.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_wdir.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_wspd.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_atmp.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_rhum.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_pres.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_otmp.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_dwpd.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")
    ax_wvht.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")

    ax_dist.plot(data.date, data.distance, marker=".", color="k", markersize=1)
    ax_wdir.plot(
        data.date[~pd.isna(data.wind_direction_sd)],
        data.wind_direction_sd[~pd.isna(data.wind_direction_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        linewidth=0.3,
    )
    ax_wdir.plot(
        data.date[~pd.isna(data.wind_direction_buoy)],
        data.wind_direction_buoy[~pd.isna(data.wind_direction_buoy)],
        marker=".",
        color="red",
        markersize=1,
        linewidth=0.3,
    )
    ax_wspd.plot(
        data.date[~pd.isna(data.wind_speed_sd)],
        data.wind_speed_sd[~pd.isna(data.wind_speed_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        linewidth=0.3,
    )
    ax_wspd.plot(
        data.date[~pd.isna(data.wind_speed_buoy)],
        data.wind_speed_buoy[~pd.isna(data.wind_speed_buoy)],
        marker=".",
        color="red",
        markersize=1,
        linewidth=0.3,
    )
    ax_atmp.plot(
        data.date[~pd.isna(data.air_temperature_sd)],
        data.air_temperature_sd[~pd.isna(data.air_temperature_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        linewidth=0.3,
    )
    ax_atmp.plot(
        data.date[~pd.isna(data.air_temperature_buoy)],
        data.air_temperature_buoy[~pd.isna(data.air_temperature_buoy)],
        marker=".",
        color="red",
        markersize=1,
        linewidth=0.3,
    )
    ax_rhum.plot(
        data.date[~pd.isna(data.relative_humidity_sd)],
        data.relative_humidity_sd[~pd.isna(data.relative_humidity_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        linewidth=0.3,
    )
    ax_rhum.plot(
        data.date[~pd.isna(data.relative_humidity_buoy)],
        data.relative_humidity_buoy[~pd.isna(data.relative_humidity_buoy)],
        marker=".",
        color="red",
        markersize=1,
        linewidth=0.3,
    )
    ax_pres.plot(
        data.date[~pd.isna(data.sea_level_pressure_sd)],
        data.sea_level_pressure_sd[~pd.isna(data.sea_level_pressure_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        linewidth=0.3,
    )
    ax_pres.plot(
        data.date[~pd.isna(data.sea_level_pressure_buoy)],
        data.sea_level_pressure_buoy[~pd.isna(data.sea_level_pressure_buoy)],
        marker=".",
        color="red",
        markersize=1,
        linewidth=0.3,
    )
    ax_otmp.plot(
        data.date[~pd.isna(data.sea_surface_temperature_sd)],
        data.sea_surface_temperature_sd[~pd.isna(data.sea_surface_temperature_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        linewidth=0.3,
    )
    ax_otmp.plot(
        data.date[~pd.isna(data.sea_surface_temperature_buoy)],
        data.sea_surface_temperature_buoy[~pd.isna(data.sea_surface_temperature_buoy)],
        marker=".",
        color="red",
        markersize=1,
        linewidth=0.3,
    )
    ax_dwpd.plot(
        data.date[~pd.isna(data.dominant_wave_period_sd)],
        data.dominant_wave_period_sd[~pd.isna(data.dominant_wave_period_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        lw=0,
    )
    ax_dwpd.plot(
        data.date[~pd.isna(data.dominant_wave_period_buoy)],
        data.dominant_wave_period_buoy[~pd.isna(data.dominant_wave_period_buoy)],
        marker=".",
        color="red",
        markersize=1,
        lw=0,
    )
    ax_wvht.plot(
        data.date[~pd.isna(data.significant_wave_height_sd)],
        data.significant_wave_height_sd[~pd.isna(data.significant_wave_height_sd)],
        marker=".",
        color="dodgerblue",
        markersize=1,
        linewidth=0.3,
    )
    ax_wvht.plot(
        data.date[~pd.isna(data.significant_wave_height_buoy)],
        data.significant_wave_height_buoy[~pd.isna(data.significant_wave_height_buoy)],
        marker=".",
        color="red",
        markersize=1,
        linewidth=0.3,
    )

    ax_dist.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    ax_dist.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax_dist.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax_dist.set_xlim(config["comparison_start_time"], config["comparison_end_time"])
    ax_dist.set_ylim(bottom=0)
    ax_wdir.set_ylim(0, 360)
    ax_wspd.set_ylim(bottom=0)
    ax_dwpd.set_ylim(bottom=0)
    ax_wvht.set_ylim(bottom=0)

    ax_dist.set_title(r"\textbf{Distance (km)}" + f"\n")
    ax_wdir.set_title(
        r"\textbf{Wind From (°)}"
        + f"\n Mean Difference: {(data.wind_direction_sd - data.wind_direction_buoy).mean():.2f}°"
        + r" $\pm$ "
        + f"{(data.wind_direction_sd - data.wind_direction_buoy).std():.2f}°"
    )
    ax_wspd.set_title(
        r"\textbf{Wind Speed (m/s)}"
        + f"\n Mean Difference: {(data.wind_speed_sd - data.wind_speed_buoy).mean():.2f} m/s"
        + r" $\pm$ "
        + f"{(data.wind_speed_sd - data.wind_speed_buoy).std():.2f} m/s"
    )
    ax_atmp.set_title(
        r"\textbf{Air Temperature (°C)}"
        + f"\n Mean Difference: {(data.air_temperature_sd - data.air_temperature_buoy).mean():.2f}°C"
        + r" $\pm$ "
        + f"{(data.air_temperature_sd - data.air_temperature_buoy).std():.2f}°C"
    )
    ax_rhum.set_title(
        r"\textbf{Relative Humidity (\%)}"
        + f"\n Mean Difference: {(data.relative_humidity_sd - data.relative_humidity_buoy).mean():.2f} "
        + r"\% $\pm$ "
        + f"{(data.relative_humidity_sd - data.relative_humidity_buoy).std():.2f} "
        + r"\%"
    )
    ax_pres.set_title(
        r"\textbf{Sea Level Pressure (hPa)}"
        + f"\n Mean Difference: {(data.sea_level_pressure_sd - data.sea_level_pressure_buoy).mean():.2f} hPa"
        + r" $\pm$ "
        + f"{(data.sea_level_pressure_sd - data.sea_level_pressure_buoy).std():.2f} hPa"
    )
    ax_otmp.set_title(
        r"\textbf{Sea Surface Temperature (°C)}"
        + f"\n Mean Difference: {(data.sea_surface_temperature_sd - data.sea_surface_temperature_buoy).mean():.2f}°C"
        + r" $\pm$ "
        + f"{(data.sea_surface_temperature_sd - data.sea_surface_temperature_buoy).std():.2f}°C"
    )
    ax_dwpd.set_title(
        r"\textbf{Dominant Wave Period (s)}"
        + f"\n Mean Difference: {(data.dominant_wave_period_sd - data.dominant_wave_period_buoy).mean():.2f} s"
        + r" $\pm$ "
        + f"{(data.dominant_wave_period_sd - data.dominant_wave_period_buoy).std():.2f} s"
    )
    ax_wvht.set_title(
        r"\textbf{Significant Wave Height (m)}"
        + f"\n Mean Difference: {(data.significant_wave_height_sd - data.significant_wave_height_buoy).mean():.2f} m"
        + r" $\pm$ "
        + f"{(data.significant_wave_height_sd - data.significant_wave_height_buoy).std():.2f} m"
    )

    fig.suptitle(
        r"\textbf{"
        + f"Comparison of SD-{config['comparison_saildrone']} (blue) and buoy {config['comparison_buoy']} (red)"
        + r"}",
        y=0.94,
        fontsize=18,
    )
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close("all")
