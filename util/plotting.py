import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib import rc
from matplotlib.gridspec import GridSpec


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
