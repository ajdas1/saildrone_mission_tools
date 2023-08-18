import os
import pandas as pd
import sys


from metpy.calc import relative_humidity_from_dewpoint
from metpy.units import units
from paths import check_for_dir_create, read_yaml_config, repo_path
from projection import get_ndbc_buoy_position, great_circle_distance
from plotting import plot_saildrone_buoy_comparison
from read_file import read_ndbc_buoy_format, read_saildrone_format


config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["compare_buoy_saildrone"]:
    sys.exit()

buoy_dir = f"{repo_path}{os.sep}" + f"{config['download_buoy_data_path']}"
buoy_position = get_ndbc_buoy_position(config=config)
saildrone_dir = f"{repo_path}{os.sep}" + f"{config['download_saildrone_data_path']}"
figure_dir = f"{repo_path}{os.sep}" + f"{config['figure_path']}{os.sep}" + f"{config['comparison_figure_path']}"
check_for_dir_create(figure_dir)
fl_buoy = f"buoy_{config['comparison_buoy']}.txt"
fl_saildrone = f"sd{config['comparison_saildrone']}_hurricane_2023.nc"
if not fl_buoy in os.listdir(buoy_dir):
    print(f"Data for buoy {config['comparison_buoy']} not found.")
    sys.exit()
if not fl_saildrone in os.listdir(saildrone_dir):
    print(f"Data for saildrone {config['comparison_saildrone']} not found.")
    sys.exit()

print(f"Comparing SD-{config['comparison_saildrone']} and buoy {config['comparison_buoy']} observations.")

# read in and process data
buoy_data = read_ndbc_buoy_format(filename=f"{buoy_dir}{os.sep}{fl_buoy}")
buoy_data["air_temperature"] = buoy_data.air_temperature.apply(
    lambda x: units.Quantity(x, units.degC)
)
buoy_data["dewpoint_temperature"] = buoy_data.dewpoint_temperature.apply(
    lambda x: units.Quantity(x, units.degC)
)
buoy_data["relative_humidity"] = buoy_data.apply(
    lambda x: relative_humidity_from_dewpoint(
        x["air_temperature"], x["dewpoint_temperature"]
    ).to("percent"),
    axis=1,
)
buoy_data["relative_humidity"] = buoy_data.relative_humidity.apply(
    lambda x: x.magnitude
)
buoy_data["air_temperature"] = buoy_data.air_temperature.apply(lambda x: x.magnitude)
buoy_data["dewpoint_temperature"] = buoy_data.dewpoint_temperature.apply(
    lambda x: x.magnitude
)
buoy_data = buoy_data.drop(
    columns=[
        "dewpoint_temperature",
        "wind_gust",
        "average_wave_period",
        "dwpd_direction",
        "visibility",
        "pressure_tendency",
        "tide_level",
    ]
)

sd_data = read_saildrone_format(filename=f"{saildrone_dir}{os.sep}{fl_saildrone}")
sd_data = sd_data.drop(columns=["sea_surface_salinity"])

data = pd.merge(sd_data, buoy_data, on="date", how="outer", suffixes=["_sd", "_buoy"])
data = data.sort_values(by="date")
data["distance"] = data.apply(
    lambda x: great_circle_distance(
        x.longitude, x.latitude, buoy_position["lon"], buoy_position["lat"]
    ),
    axis=1,
)

data = data[
    (data.date >= config["comparison_start_time"])
    & (data.date <= config["comparison_end_time"])
].reset_index(drop=True)


filename = (
    f"{figure_dir}{os.sep}"
    + f"Comparison_SD{config['comparison_saildrone']}_B{config['comparison_buoy']}_" + f"{config['comparison_start_time'].strftime('%Y-%m-%d')}_{config['comparison_end_time'].strftime('%Y-%m-%d')}.png"
)
plot_saildrone_buoy_comparison(data=data, config=config, filename=filename)
