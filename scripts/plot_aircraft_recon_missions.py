import os
import pandas as pd
import pytz
import sys

from conversions import convert_time_to_utc
from datetime import datetime
from paths import (
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from plotting import plot_aircraft_recon_mission_with_saildrones
from read_file import read_saildrone_format

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["plot_aircraft_recon"]:
    sys.exit()
print("Plotting aircraft recon data with saildrones.")

current_time = convert_time_to_utc(
    datetime.now(), timezone=pytz.timezone(config["local_timezone"])
).replace(tzinfo=None)

recon_aircraft_dir = (
    f"{repo_path}{os.sep}" + f"{config['download_recon_flight_data_path']}"
)
recon_drop_dir = (
    f"{repo_path}{os.sep}" + f"{config['download_recon_dropsonde_data_path']}"
)
saildrone_dir = f"{repo_path}{os.sep}" + f"{config['download_saildrone_data_path']}"
fig_dir = f"{repo_path}{os.sep}" + f"{config['aircraft_recon_figure_path']}"
check_for_dir_create(recon_aircraft_dir)
check_for_dir_create(recon_drop_dir)
check_for_dir_create(fig_dir)
check_for_dir_create(saildrone_dir)

recon_fls = sorted([fl for fl in os.listdir(recon_aircraft_dir) if ".csv" in fl])

sd_fls = sorted(os.listdir(saildrone_dir))


for fl in recon_fls:
    print(fl)
    aircraft = fl.split("_")[2].split("-")[0]
    number = fl.split("_")[2].split("-")[1]
    storm = fl.split("_")[2].split("-")[2][:-4]
    flight_data = pd.read_csv(f"{recon_aircraft_dir}{os.sep}{fl}")
    flight_data.time = pd.to_datetime(flight_data.time)
    if os.path.isfile(f"{recon_drop_dir}{os.sep}{fl}"):
        drop_data = pd.read_csv(f"{recon_drop_dir}{os.sep}{fl}")
        drop_data.start_time = pd.to_datetime(drop_data.start_time)
        drop_data.end_time = pd.to_datetime(drop_data.end_time)
    else:
        drop_data = None

    hour_times = flight_data[
        (flight_data.time.dt.minute == 0) & (flight_data.time.dt.second == 0)
    ].time
    if len(hour_times) > 0:
        first_hour_time = hour_times.iloc[0]

        sd_data = []
        for sd in sd_fls:
            tmp = read_saildrone_format(filename=f"{saildrone_dir}{os.sep}{sd}")
            tmp = tmp[["latitude", "longitude", "date"]]
            tmp = tmp[
                (tmp.date >= flight_data.time.min())
                & (tmp.date <= flight_data.time.max())
            ].reset_index(drop=True)
            tmp["hour"] = tmp.date - first_hour_time
            tmp["hr"] = tmp.hour.dt.days * 24 + tmp.hour.dt.seconds / 60 / 60

            sd_data.append(tmp)

        if drop_data is not None:
            drop_data = drop_data[["start_lon", "start_lat", "start_time"]]
            drop_data = drop_data.groupby("start_time").first().reset_index()
            drop_data["hour"] = drop_data.start_time - first_hour_time
            drop_data["hr"] = (
                drop_data.hour.dt.days * 24 + drop_data.hour.dt.seconds / 60 / 60
            )

        plot_aircraft_recon_mission_with_saildrones(
            recon_data=flight_data,
            sd_data=sd_data,
            drop_data=drop_data,
            storm=storm,
            fig_dir=fig_dir,
            aircraft=aircraft
        )
