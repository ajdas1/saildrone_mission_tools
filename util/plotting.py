import geopandas as gpd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from conversions import get_centroid_coordinates
from datetime import datetime, timedelta
from matplotlib import rc
from matplotlib.colors import ListedColormap
from matplotlib.gridspec import GridSpec
from projection import proj, set_cartopy_projection_atlantic
from typing import List

track_aids_to_use = [
    "CARQ",
    "OFCI",
    "OFCL",
    "NVGI",
    "AVNI",
    "GFSI",
    "EMXI",
    "EGRI",
    "CMCI",
    "HWFI",
    "CTCI",
    "HFAI",
    "HFBI" "HMNI",
    "AEMI",
    "UEMI",
    "EMN2",
    "TVCN",
    "GFEX",
    "TVCX",
]
intensity_aids_to_use = [
    "CARQ",
    "OFCL",
    "OFCI",
    "AVNI",
    "CMCI",
    "CTCI",
    "DSHP",
    "EGRI",
    "EMXI",
    "FSSE",
    "GFSI",
    "HCCA",
    "HMNI",
    "HWFI",
    "ICON",
    "IVCN",
    "LGEM",
    "NVGI",
]


def plot_aircraft_recon_mission_with_saildrones(
    recon_data: pd.DataFrame,
    sd_data: List[pd.DataFrame],
    drop_data: pd.DataFrame,
    storm: str,
    fig_dir: str,
    aircraft: str
):
    hour_times = recon_data[
        (recon_data.time.dt.minute == 0) & (recon_data.time.dt.second == 0)
    ].time
    first_hour_time = hour_times.iloc[0]
    recon_data["hour"] = recon_data.time - first_hour_time
    recon_data["hr"] = (
        recon_data.hour.dt.days * 24 + recon_data.hour.dt.seconds / 60 / 60
    )
    data_sub = recon_data[
        (recon_data.time.dt.minute.isin([0, 10, 20, 30, 40, 50]))
        & (recon_data.time.dt.second == 0)
    ].reset_index(drop=True)
    data_sub.wind_direction = (90 - (data_sub.wind_direction + 180)) % 360
    data_sub["u"] = data_sub.wind_speed * np.cos(np.deg2rad(data_sub.wind_direction))
    data_sub["v"] = data_sub.wind_speed * np.sin(np.deg2rad(data_sub.wind_direction))

    lon_min, lon_max, lat_min, lat_max = (
        recon_data.lon.min(),
        recon_data.lon.max(),
        recon_data.lat.min(),
        recon_data.lat.max(),
    )

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection=proj)
    f1 = ax.scatter(
        recon_data.lon,
        recon_data.lat,
        s=3,
        c=recon_data.hr,
        cmap="turbo",
        vmin=recon_data.hr.min(),
        vmax=recon_data.hr.max(),
    )
    ax.barbs(data_sub.lon, data_sub.lat, data_sub.u, data_sub.v, length=5)

    if drop_data is not None:
        ax.scatter(
            drop_data.start_lon,
            drop_data.start_lat,
            s=28,
            c=drop_data.hr,
            marker="o",
            cmap="turbo",
            vmin=recon_data.hr.min(),
            vmax=recon_data.hr.max(),
            ec="k",
            lw=1,
        )

    for sd in sd_data:
        ax.scatter(
            sd.longitude,
            sd.latitude,
            s=28,
            c=sd.hr,
            marker="*",
            cmap="turbo",
            vmin=recon_data.hr.min(),
            vmax=recon_data.hr.max(),
        )

    ax.scatter(-130, -20, s=28, c="k", marker="*", label="SD")
    ax.scatter(-130, -20, s=28, c="k", marker="o", label="dropsonde")
    leg = ax.legend(loc=1)

    cbar = plt.colorbar(f1, ticks=np.arange(0, len(hour_times), 1), pad=0.02)
    cbar.ax.set_yticklabels(
        [f"{tm.strftime('%b-%d')}\n{tm.strftime('%H:%M')}" for tm in hour_times]
    )
    set_cartopy_projection_atlantic(
        ax=ax,
        extent=[lon_min - 3, lon_max + 3, lat_min - 3, lat_max + 3],
        xticks=np.arange(
            -110, -30, get_tick_frequency_from_range(min=lon_min, max=lon_max, buffer=3)
        ),
        ylabel="bottom",
        yticks=np.arange(
            0, 90, get_tick_frequency_from_range(min=lat_min, max=lat_max, buffer=3)
        ),
    )
    ax.set_title(
        f"{storm} ({aircraft}) \n{recon_data.time.iloc[0].strftime('%Y-%m-%d %H:%M UTC')} - {recon_data.time.iloc[-1].strftime('%Y-%m-%d %H:%M UTC')}"
    )

    plt.savefig(
        f"{fig_dir}{os.sep}{storm}_{aircraft}_{recon_data.time.iloc[0].strftime('%Y-%m-%d')}.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close("all")


def get_tick_frequency_from_range(min: float, max: float, buffer: float = 3.0) -> int:
    drange = (max - min) + 2 * buffer
    if drange <= 10:
        dval = 1
    elif drange <= 20:
        dval = 2
    elif drange <= 30:
        dval = 3
    elif drange <= 40:
        dval = 4
    else:
        dval = 5

    return dval


def plot_system_winds(btk_data: pd.DataFrame, fcst_data: pd.DataFrame, filename: str):
    name = btk_data.StormName.iloc[-1]
    if name == "INVEST":
        name = f"{btk_data.StormNumber.iloc[-1]}L"
    else:
        name = f"{btk_data.StormType.iloc[-1]} " + name

    fcst_data = fcst_data[fcst_data.FcstCenter.isin(intensity_aids_to_use)]
    products = list(fcst_data.FcstCenter.unique())
    products.pop(products.index("CARQ"))
    if ("OFCL" in products) and ("OFCI" in products):
        products.pop(products.index("OFCI"))
    aids_to_use = [aid for aid in intensity_aids_to_use if not aid in ["CARQ"]]
    colors = plt.cm.turbo(np.linspace(0, 1, len(aids_to_use)))
    pcolors = {aids_to_use[idx]: colors[idx] for idx in range(len(aids_to_use))}
    pcolors["OFCL"] = "k"
    pcolors["OFCI"] = "k"

    fig = plt.figure(figsize=(8, 4))
    ax_mwsp = fig.add_subplot(111)

    ax_mwsp.grid(True, which="both", linewidth=0.5, linestyle="dashed", color=".7")

    ax_mwsp.axhline(34, c="k", lw=1)
    ax_mwsp.axhline(64, c="k", lw=1)
    ax_mwsp.axvline(btk_data.Valid.max(), c="k", lw=0.5)
    ax_mwsp.text(
        btk_data.Valid.min(), 34, "34kt", ha="left", va="bottom", fontweight="semibold"
    )
    ax_mwsp.text(
        btk_data.Valid.min(), 64, "64kt", ha="left", va="bottom", fontweight="semibold"
    )

    ax_mwsp.plot(btk_data.Valid, btk_data.MaxSustainedWind, c="k", lw=2)
    ax_mwsp.plot(
        btk_data.Valid.iloc[-1], btk_data.MaxSustainedWind.iloc[-1], "ok", markersize=4
    )

    if len(products) > 0:
        for product in products:
            fcst_curr = fcst_data[
                (fcst_data.FcstCenter == product) & (fcst_data.FcstHour >= 0)
            ]
            if product in ["OFCL", "OFCI"]:
                ax_mwsp.plot(
                    fcst_curr.Valid,
                    fcst_curr.MaxSustainedWind,
                    linewidth=1.5,
                    marker="o",
                    markersize=3,
                    c=pcolors[product],
                    label=product,
                    zorder=5,
                )
            else:
                ax_mwsp.plot(
                    fcst_curr.Valid,
                    fcst_curr.MaxSustainedWind,
                    linewidth=1.5,
                    marker="o",
                    markersize=3,
                    c=pcolors[product],
                    label=product,
                )
        ax_mwsp.legend(loc=2, fontsize=7, ncol=np.ceil(len(products) / 8))

    ax_mwsp.xaxis.set_tick_params(rotation=45)
    ax_mwsp.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    ax_mwsp.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
    ax_mwsp.xaxis.set_major_locator(mdates.HourLocator(byhour=0))

    ax_mwsp.set_title(
        f"{name}: {fcst_data.Valid.iloc[0].strftime('%Y-%m-%d %H')} UTC\n Max Sustained Winds (kt)"
    )
    ax_mwsp.set_ylim(bottom=0)
    ax_mwsp.set_xlim(btk_data.Valid.min(), fcst_data.Valid.max() + timedelta(hours=3))
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close("all")


def plot_system_track(
    btk_data: pd.DataFrame, fcst_data: pd.DataFrame, filename: str, sd_data: dict = None
):
    name = btk_data.StormName.iloc[-1]
    if name == "INVEST":
        name = f"{btk_data.StormNumber.iloc[-1]}L"
    else:
        name = f"{btk_data.StormType.iloc[-1]} " + name

    fcst_data = fcst_data[fcst_data.FcstCenter.isin(track_aids_to_use)]
    products = list(fcst_data.FcstCenter.unique())
    products.pop(products.index("CARQ"))
    if ("OFCL" in products) and ("OFCI" in products):
        products.pop(products.index("OFCI"))
    aids_to_use = [aid for aid in track_aids_to_use if not aid in ["CARQ"]]
    colors = plt.cm.turbo(np.linspace(0, 1, len(aids_to_use)))
    pcolors = {aids_to_use[idx]: colors[idx] for idx in range(len(aids_to_use))}
    pcolors["OFCL"] = "k"
    pcolors["OFCI"] = "k"

    fig = plt.figure(figsize=(12, 5))
    ax = fig.add_subplot(111, projection=proj)
    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")

    if len(products) > 0:
        for product in products:
            fcst_curr = fcst_data[
                (fcst_data.FcstCenter == product) & (fcst_data.FcstHour >= 0)
            ]
            if product in ["OFCL", "OFCI"]:
                ax.plot(
                    fcst_curr.Longitude,
                    fcst_curr.Latitude,
                    linewidth=1.5,
                    marker="o",
                    markersize=3,
                    c=pcolors[product],
                    label=product,
                    zorder=5,
                )
            else:
                ax.plot(
                    fcst_curr.Longitude,
                    fcst_curr.Latitude,
                    linewidth=1.5,
                    marker="o",
                    markersize=3,
                    c=pcolors[product],
                    label=product,
                )

    # plot btk
    ax.plot(
        btk_data.Longitude,
        btk_data.Latitude,
        c="k",
        lw=1,
        linestyle="--",
        label="Best Track",
    )
    ax.plot(btk_data.Longitude.iloc[-1], btk_data.Latitude.iloc[-1], "ok", markersize=4)
    ax.text(
        btk_data.Longitude.iloc[0],
        btk_data.Latitude.iloc[0],
        name,
        ha="left",
        va="top",
        bbox=dict(facecolor="w", edgecolor="black", boxstyle="round,pad=.1", alpha=0.5),
    )

    plot_saildrone_mission_domains(ax=ax)
    if sd_data is not None:
        for sd in sd_data:
            ax.plot(
                sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10
            )
            ax.arrow(
                sd_data[sd]["lon"],
                sd_data[sd]["lat"],
                np.cos(np.deg2rad(90 - sd_data[sd]["dir"])),
                np.sin(np.deg2rad(90 - sd_data[sd]["dir"])),
                length_includes_head=True,
                head_width=0.5,
                color="m",
                head_length=0.5,
                zorder=10,
            )
        ax.plot(130, 0, "om", markersize=2, label="SD")
    if len(products) > 0:
        ax.legend(loc=1, fontsize=7, ncol=np.ceil(len(products) / 25))

    ax.set_title(f"{name}: {fcst_data.Valid.iloc[0].strftime('%Y-%m-%d %H')} UTC")
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close("all")


def plot_shapefile_btkstart(
    shapefile_data: pd.DataFrame,
    wind_overlap: dict,
    n: int,
    n_storms: int,
    time: datetime,
    savedir: str,
    sd_data: dict = None,
    percentage: bool = False,
    title_save_add: str = "",
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
    shapefile_data["coords"] = shapefile_data["geometry"].apply(
        get_centroid_coordinates
    )

    fig = plt.figure(figsize=(12, 5))
    ax = fig.add_subplot(111, projection=proj)

    shapefile_data["geometry"].plot(ax=ax, color=area_colors, alpha=0.5, edgecolor="k")
    for _, row in shapefile_data.iterrows():
        ax.annotate(
            text=row["AREA"],
            xy=row["coords"],
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=10,
        )

    for idx, row in shapefile_data.iterrows():
        annotate_text = (
            f"Area {row['AREA']}\n2 day: {row['PROB2DAY']}\n7 day: {row['PROB7DAY']}"
        )
        ax.annotate(
            text=annotate_text,
            xy=(-110 + idx * 20, 3),
            ha="left",
            va="top",
            backgroundcolor=(1, 1, 1, 0.5),
            fontsize=10,
        )

    legend_kwds = {"pad": 0.015, "shrink": 0.99, "label": f"storm {label_title}"}
    if len(wind_overlap) > 0:
        wind_overlap.plot(
            column=overlap_column,
            ax=ax,
            legend=False,
            alpha=0.8,
            vmin=vmin,
            vmax=vmax,
            legend_kwds=legend_kwds,
            cmap=cmap,
        )

    ax.plot([130, 140], [0, 1], c="yellow", alpha=0.5, lw=10, label="Low (<40%)")
    ax.plot([130, 140], [0, 1], c="orange", alpha=0.5, lw=10, label="Medium (40-60%)")
    ax.plot([130, 140], [0, 1], c="red", alpha=0.5, lw=10, label="High (>60%)")

    if sd_data is not None:
        for sd in sd_data:
            ax.plot(
                sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10
            )
            ax.arrow(
                sd_data[sd]["lon"],
                sd_data[sd]["lat"],
                np.cos(np.deg2rad(90 - sd_data[sd]["dir"])),
                np.sin(np.deg2rad(90 - sd_data[sd]["dir"])),
                length_includes_head=True,
                head_width=0.5,
                color="m",
                head_length=0.5,
                zorder=10,
            )
        ax.plot(130, 0, "om", markersize=2, label="SD")

    plot_saildrone_mission_domains(ax=ax)

    ax.legend(loc=1)
    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")
    ax.set_title(
        f"7-day outlook areas: {time.strftime('%Y-%m-%d %H:%M')} UTC{title_add} ({title_save_add[1:]})"
    )

    plt.savefig(
        f"{savedir}{os.sep}outlook_areas_btks_{save_add}area{n}{title_save_add}.png",
        dpi=200,
        bbox_inches="tight",
    )
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


def plot_shapefile_with_btks_and_fcsts(
    shapefile_data: gpd.GeoDataFrame,
    btk_data: dict,
    fcst_data: dict,
    time: datetime,
    savedir: str,
    sd_data: dict = None,
):
    area_colors = find_outlook_area_color(shapefile_data=shapefile_data)

    shapefile_data["coords"] = shapefile_data["geometry"].apply(
        get_centroid_coordinates
    )

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection=proj)

    if len(shapefile_data) > 0:
        shapefile_data.plot(ax=ax, color=area_colors, alpha=0.5, edgecolor="k")
        for _, row in shapefile_data.iterrows():
            ax.annotate(
                text=row["AREA"],
                xy=row["coords"],
                ha="center",
                va="center",
                fontweight="bold",
            )
        for idx, row in shapefile_data.iterrows():
            annotate_text = (
                f"Area {row['AREA']}\n2 day: {row['PROB2DAY']}\n7 day: {row['PROB7DAY']}"
            )
            ax.annotate(
                text=annotate_text,
                xy=(-110 + idx * 20, 1.5),
                ha="left",
                va="top",
                fontweight="semibold",
                backgroundcolor=(1, 1, 1, 0.5),
            )

    for btk in btk_data:
        ax.plot(
            btk_data[btk].Longitude, btk_data[btk].Latitude, c="k", lw=1, linestyle="--"
        )
        ax.plot(
            btk_data[btk].Longitude.iloc[-1],
            btk_data[btk].Latitude.iloc[-1],
            "ok",
            markersize=4,
        )
        name = btk_data[btk].StormName.iloc[-1]
        if name == "INVEST":
            name = f"{btk_data[btk].StormNumber.iloc[-1]}L"
        else:
            name = f"{btk_data[btk].StormType.iloc[-1]} " + name
        ax.text(
            btk_data[btk].Longitude.iloc[0],
            btk_data[btk].Latitude.iloc[0],
            name,
            ha="left",
            va="top",
            bbox=dict(
                facecolor="w", edgecolor="black", boxstyle="round,pad=.1", alpha=0.5
            ),
        )

    for fcst in fcst_data:
        tmp = fcst_data[fcst]
        tmp = tmp[tmp.FcstCenter.isin(track_aids_to_use)]
        prods = list(tmp.FcstCenter.unique())
        if ("OFCI" in prods) and ("OFCL" in prods):
            prods.pop(prods.index("OFCI"))
        for prod in prods:
            fcst_prod = tmp[(tmp.FcstCenter == prod) & (tmp.FcstHour >= 0)]
            if prod in ["OFCI", "OFCL"]:
                ax.plot(fcst_prod.Longitude, fcst_prod.Latitude, c="b", lw=2)
            else:
                ax.plot(fcst_prod.Longitude, fcst_prod.Latitude, c="b", lw=0.3)

    if sd_data is not None:
        for sd in sd_data:
            ax.plot(
                sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10
            )
            ax.arrow(
                sd_data[sd]["lon"],
                sd_data[sd]["lat"],
                np.cos(np.deg2rad(90 - sd_data[sd]["dir"])),
                np.sin(np.deg2rad(90 - sd_data[sd]["dir"])),
                length_includes_head=True,
                head_width=0.5,
                color="m",
                head_length=0.5,
                zorder=10,
            )

    ax.plot([130, 140], [0, 1], c="yellow", alpha=0.5, lw=10, label="Low (<40%)")
    ax.plot([130, 140], [0, 1], c="orange", alpha=0.5, lw=10, label="Medium (40-60%)")
    ax.plot([130, 140], [0, 1], c="red", alpha=0.5, lw=10, label="High (>60%)")
    ax.plot(130, 0, "om", markersize=2, label="SD")
    ax.plot([130, 130], [140, 140], c="k", lw=1, linestyle="--", label="Best Track")
    ax.plot([130, 130], [140, 140], c="b", lw=0.3, label="Forecast")
    ax.plot([130, 130], [140, 140], c="b", lw=2, label="OFCL Forecast")

    ax.legend()
    plot_saildrone_mission_domains(ax=ax)
    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")
    ax.set_title(f"7-day outlook areas: {time.strftime('%Y-%m-%d %H:%M')} UTC")

    plt.savefig(
        f"{savedir}{os.sep}outlook_areas_with_btks_and_fcsts.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close("all")


def plot_shapefile_with_fcsts(
    shapefile_data: gpd.GeoDataFrame,
    fcst_data: dict,
    time: datetime,
    savedir: str,
    sd_data: dict = None,
):
    area_colors = find_outlook_area_color(shapefile_data=shapefile_data)

    shapefile_data["coords"] = shapefile_data["geometry"].apply(
        get_centroid_coordinates
    )

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection=proj)

    if len(shapefile_data) > 0:
        shapefile_data.plot(ax=ax, color=area_colors, alpha=0.5, edgecolor="k")
        for _, row in shapefile_data.iterrows():
            ax.annotate(
                text=row["AREA"],
                xy=row["coords"],
                ha="center",
                va="center",
                fontweight="bold",
            )
        for idx, row in shapefile_data.iterrows():
            annotate_text = (
                f"Area {row['AREA']}\n2 day: {row['PROB2DAY']}\n7 day: {row['PROB7DAY']}"
            )
            ax.annotate(
                text=annotate_text,
                xy=(-110 + idx * 20, 1.5),
                ha="left",
                va="top",
                fontweight="semibold",
                backgroundcolor=(1, 1, 1, 0.5),
            )

    name = {}
    for fcst in fcst_data:
        tmp = fcst_data[fcst]
        tmp = tmp[(tmp.FcstCenter == "CARQ") & (tmp.FcstHour == 0)]
        ntmp = tmp.iloc[0].StormName
        if ntmp == "INVEST":
            ntmp = f"{tmp .StormNumber.iloc[0]}L"
        else:
            ntmp = f"{tmp .StormType.iloc[0]} " + ntmp
        name[fcst] = ntmp

    for fcst in fcst_data:
        tmp = fcst_data[fcst]
        tmp = tmp[tmp.FcstCenter.isin(track_aids_to_use)]
        prods = list(tmp.FcstCenter.unique())
        if ("OFCI" in prods) and ("OFCL" in prods):
            prods.pop(prods.index("OFCI"))
        for prod in prods:
            fcst_prod = tmp[(tmp.FcstCenter == prod) & (tmp.FcstHour >= 0)]
            if prod in ["OFCI", "OFCL"]:
                ax.plot(
                    fcst_prod.Longitude.iloc[0],
                    fcst_prod.Latitude.iloc[0],
                    "ob",
                    markersize=4,
                )
                ax.plot(fcst_prod.Longitude, fcst_prod.Latitude, c="b", lw=2)
            elif prod == "CARQ":
                ax.plot(
                    fcst_prod.Longitude.iloc[0],
                    fcst_prod.Latitude.iloc[0],
                    "ob",
                    markersize=4,
                )
                ax.plot(fcst_prod.Longitude, fcst_prod.Latitude, c="b", lw=0.3)
                ax.text(
                    fcst_prod.Longitude.iloc[0],
                    fcst_prod.Latitude.iloc[0],
                    name[fcst],
                    ha="left",
                    va="top",
                    bbox=dict(
                        facecolor="w",
                        edgecolor="black",
                        boxstyle="round,pad=.1",
                        alpha=0.5,
                    ),
                )
            else:
                ax.plot(fcst_prod.Longitude, fcst_prod.Latitude, c="b", lw=0.3)

    if sd_data is not None:
        for sd in sd_data:
            ax.plot(
                sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10
            )
            ax.arrow(
                sd_data[sd]["lon"],
                sd_data[sd]["lat"],
                np.cos(np.deg2rad(90 - sd_data[sd]["dir"])),
                np.sin(np.deg2rad(90 - sd_data[sd]["dir"])),
                length_includes_head=True,
                head_width=0.5,
                color="m",
                head_length=0.5,
                zorder=10,
            )

    ax.plot([130, 140], [0, 1], c="yellow", alpha=0.5, lw=10, label="Low (<40%)")
    ax.plot([130, 140], [0, 1], c="orange", alpha=0.5, lw=10, label="Medium (40-60%)")
    ax.plot([130, 140], [0, 1], c="red", alpha=0.5, lw=10, label="High (>60%)")
    ax.plot(130, 0, "om", markersize=2, label="SD")
    ax.plot([130, 130], [140, 140], c="b", lw=0.3, label="Forecast")
    ax.plot([130, 130], [140, 140], c="b", lw=2, label="OFCL Forecast")

    ax.legend()
    plot_saildrone_mission_domains(ax=ax)
    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")
    ax.set_title(f"7-day outlook areas: {time.strftime('%Y-%m-%d %H:%M')} UTC")

    plt.savefig(
        f"{savedir}{os.sep}outlook_areas_with_fcsts.png", dpi=200, bbox_inches="tight"
    )
    plt.close("all")


def plot_shapefile_with_btks(
    shapefile_data: gpd.GeoDataFrame,
    btk_data: dict,
    time: datetime,
    savedir: str,
    sd_data: dict = None,
):
    area_colors = find_outlook_area_color(shapefile_data=shapefile_data)

    shapefile_data["coords"] = shapefile_data["geometry"].apply(
        get_centroid_coordinates
    )

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection=proj)

    if len(shapefile_data) > 0:
        shapefile_data.plot(ax=ax, color=area_colors, alpha=0.5, edgecolor="k")
        for _, row in shapefile_data.iterrows():
            ax.annotate(
                text=row["AREA"],
                xy=row["coords"],
                ha="center",
                va="center",
                fontweight="bold",
            )
        for idx, row in shapefile_data.iterrows():
            annotate_text = (
                f"Area {row['AREA']}\n2 day: {row['PROB2DAY']}\n7 day: {row['PROB7DAY']}"
            )
            ax.annotate(
                text=annotate_text,
                xy=(-110 + idx * 20, 1.5),
                ha="left",
                va="top",
                fontweight="semibold",
                backgroundcolor=(1, 1, 1, 0.5),
            )

    for btk in btk_data:
        ax.plot(
            btk_data[btk].Longitude, btk_data[btk].Latitude, c="k", lw=1, linestyle="--"
        )
        ax.plot(
            btk_data[btk].Longitude.iloc[-1],
            btk_data[btk].Latitude.iloc[-1],
            "ok",
            markersize=4,
        )
        name = btk_data[btk].StormName.iloc[-1]
        if name == "INVEST":
            name = f"{btk_data[btk].StormNumber.iloc[-1]}L"
        else:
            name = f"{btk_data[btk].StormType.iloc[-1]} " + name
        ax.text(
            btk_data[btk].Longitude.iloc[0],
            btk_data[btk].Latitude.iloc[0],
            name,
            ha="left",
            va="top",
            bbox=dict(
                facecolor="w", edgecolor="black", boxstyle="round,pad=.1", alpha=0.5
            ),
        )

    if sd_data is not None:
        for sd in sd_data:
            ax.plot(
                sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10
            )
            ax.arrow(
                sd_data[sd]["lon"],
                sd_data[sd]["lat"],
                np.cos(np.deg2rad(90 - sd_data[sd]["dir"])),
                np.sin(np.deg2rad(90 - sd_data[sd]["dir"])),
                length_includes_head=True,
                head_width=0.5,
                color="m",
                head_length=0.5,
                zorder=10,
            )
    ax.plot([130, 140], [0, 1], c="yellow", alpha=0.5, lw=10, label="Low (<40%)")
    ax.plot([130, 140], [0, 1], c="orange", alpha=0.5, lw=10, label="Medium (40-60%)")
    ax.plot([130, 140], [0, 1], c="red", alpha=0.5, lw=10, label="High (>60%)")
    ax.plot(130, 0, "om", markersize=2, label="SD")
    ax.plot([130, 140], [0, 1], c="k", lw=1, linestyle="--", label="Best Track")
    ax.legend()
    plot_saildrone_mission_domains(ax=ax)
    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")
    ax.set_title(f"7-day outlook areas: {time.strftime('%Y-%m-%d %H:%M')} UTC")

    plt.savefig(
        f"{savedir}{os.sep}outlook_areas_with_btks.png", dpi=200, bbox_inches="tight"
    )
    plt.close("all")


def plot_shapefile(
    shapefile_data: gpd.GeoDataFrame, time: datetime, savedir: str, sd_data: dict = None
):
    area_colors = find_outlook_area_color(shapefile_data=shapefile_data)

    shapefile_data["coords"] = shapefile_data["geometry"].apply(
        get_centroid_coordinates
    )

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection=proj)

    if len(shapefile_data) > 0:
        shapefile_data.plot(ax=ax, color=area_colors, alpha=0.5, edgecolor="k")
        for _, row in shapefile_data.iterrows():
            ax.annotate(
                text=row["AREA"],
                xy=row["coords"],
                ha="center",
                va="center",
                fontweight="bold",
            )

        for idx, row in shapefile_data.iterrows():
            annotate_text = (
                f"Area {row['AREA']}\n2 day: {row['PROB2DAY']}\n7 day: {row['PROB7DAY']}"
            )
            ax.annotate(
                text=annotate_text,
                xy=(-110 + idx * 20, 1.5),
                ha="left",
                va="top",
                fontweight="semibold",
                backgroundcolor=(1, 1, 1, 0.5),
            )

    ax.plot([130, 140], [0, 1], c="yellow", alpha=0.5, lw=10, label="Low (<40%)")
    ax.plot([130, 140], [0, 1], c="orange", alpha=0.5, lw=10, label="Medium (40-60%)")
    ax.plot([130, 140], [0, 1], c="red", alpha=0.5, lw=10, label="High (>60%)")

    if sd_data is not None:
        for sd in sd_data:
            ax.plot(
                sd_data[sd]["lon"], sd_data[sd]["lat"], "om", markersize=2, zorder=10
            )
            ax.arrow(
                sd_data[sd]["lon"],
                sd_data[sd]["lat"],
                np.cos(np.deg2rad(90 - sd_data[sd]["dir"])),
                np.sin(np.deg2rad(90 - sd_data[sd]["dir"])),
                length_includes_head=True,
                head_width=0.5,
                color="m",
                head_length=0.5,
                zorder=10,
            )
        ax.plot(130, 0, "om", markersize=2, label="SD")

    ax.legend()

    plot_saildrone_mission_domains(ax=ax)

    set_cartopy_projection_atlantic(ax=ax, ylabel="bottom")
    ax.set_title(f"7-day outlook areas: {time.strftime('%Y-%m-%d %H:%M')} UTC")

    plt.savefig(f"{savedir}{os.sep}outlook_areas.png", dpi=200, bbox_inches="tight")
    plt.close("all")


def plot_saildrone_mission_domains(ax: plt.axis):
    # Mission Domain A
    ax.plot([-55.11, -46.83], [20.40, 20.40], c="k", lw=0.7)
    ax.plot([-46.83, -46.85], [20.40, 13.50], c="k", lw=0.7)
    ax.plot([-46.85, -55.14], [13.50, 13.50], c="k", lw=0.7)
    ax.plot([-55.14, -55.11], [13.50, 20.40], c="k", lw=0.7)
    ax.text(
        -46.83,
        20.40,
        "A",
        fontweight="semibold",
        ha="right",
        va="top",
        fontsize=6,
        zorder=20,
    )
    # Mission Domain B
    ax.plot([-67.56, -65.50], [17.63, 17.63], c="k", lw=0.7)
    ax.plot([-65.50, -65.51], [17.63, 16.09], c="k", lw=0.7)
    ax.plot([-65.51, -67.57], [16.09, 16.09], c="k", lw=0.7)
    ax.plot([-67.57, -67.56], [16.09, 17.63], c="k", lw=0.7)
    ax.text(
        -65.50,
        17.63,
        "B",
        fontweight="semibold",
        ha="right",
        va="top",
        fontsize=6,
        zorder=20,
    )
    # Mission Domain C
    ax.plot([-66.80, -65.94], [21.80, 21.79], c="k", lw=0.7)
    ax.plot([-65.94, -65.90], [21.79, 18.77], c="k", lw=0.7)
    ax.plot([-65.90, -66.84], [18.77, 18.76], c="k", lw=0.7)
    ax.plot([-66.84, -66.80], [18.76, 21.80], c="k", lw=0.7)
    ax.text(
        -65.94,
        21.79,
        "C",
        fontweight="semibold",
        ha="right",
        va="top",
        fontsize=6,
        zorder=20,
    )
    # Mission Domain D
    ax.plot([-66.24, -63.23], [28.50, 28.51], c="k", lw=0.7)
    ax.plot([-63.23, -63.22], [28.51, 26.27], c="k", lw=0.7)
    ax.plot([-63.22, -66.22], [26.27, 26.26], c="k", lw=0.7)
    ax.plot([-66.22, -66.24], [26.26, 28.50], c="k", lw=0.7)
    ax.text(
        -63.23,
        28.51,
        "D",
        fontweight="semibold",
        ha="right",
        va="top",
        fontsize=6,
        zorder=20,
    )
    # Mission Domain EE
    ax.plot([-75.5, -74], [33, 33], c="k", lw=0.7)
    ax.plot([-74, -74], [33, 31.5], c="k", lw=0.7)
    ax.plot([-74, -75.5], [31.5, 31.5], c="k", lw=0.7)
    ax.plot([-75.5, -75.5], [31.5, 33], c="k", lw=0.7)
    ax.text(
        -74,
        33,
        "EE",
        fontweight="semibold",
        ha="right",
        va="top",
        fontsize=6,
        zorder=20,
    )
    # Mission Domain F
    ax.plot([-89, -83.85], [28, 28.74], c="k", lw=0.7)
    ax.plot([-83.85, -82.23], [28.74, 25.52], c="k", lw=0.7)
    ax.plot([-82.23, -88.34], [25.52, 25.80], c="k", lw=0.7)
    ax.plot([-88.34, -89], [25.80, 28], c="k", lw=0.7)
    ax.text(
        -88.34,
        25.80,
        "F",
        fontweight="semibold",
        ha="right",
        va="top",
        fontsize=6,
        zorder=20,
    )

    # Mission Domain E
    ax.plot([-78.87, -77.49], [32.66, 33.39], c="k", lw=0.7)
    ax.plot([-77.49, -76.68], [33.39, 34.07], c="k", lw=0.7)
    ax.plot([-76.68, -75.79], [34.07, 34.52], c="k", lw=0.7)
    ax.plot([-75.79, -75.50], [34.52, 34.40], c="k", lw=0.7)
    ax.plot([-75.50, -76.28], [34.40, 33.63], c="k", lw=0.7)
    ax.plot([-76.28, -77.17], [33.63, 32.84], c="k", lw=0.7)
    ax.plot([-77.17, -78.29], [32.84, 32.01], c="k", lw=0.7)
    ax.plot([-78.29, -79.02], [32.01, 31.54], c="k", lw=0.7)
    ax.plot([-79.02, -79.39], [31.54, 31.10], c="k", lw=0.7)
    ax.plot([-79.39, -79.73], [31.10, 30.65], c="k", lw=0.7)
    ax.plot([-79.73, -80.19], [30.65, 31.17], c="k", lw=0.7)
    ax.plot([-80.19, -79.77], [31.17, 31.94], c="k", lw=0.7)
    ax.plot([-79.77, -78.87], [31.94, 32.66], c="k", lw=0.7)
    ax.text(
        -75.50,
        34.40,
        "E",
        fontweight="semibold",
        ha="left",
        va="bottom",
        fontsize=6,
        zorder=20,
    )


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
    ax_dist.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
    ax_dist.xaxis.set_major_locator(mdates.HourLocator(byhour=0))
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
