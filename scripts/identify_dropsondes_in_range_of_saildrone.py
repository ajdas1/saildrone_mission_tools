import os
import pandas as pd
import sys
import warnings

from datetime import datetime, timedelta
from paths import (
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from projection import great_circle_distance
from read_file import read_dropsonde_data, read_saildrone_format


warnings.filterwarnings("ignore")

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["identify_dropsondes_in_range_of_saildrone"]:
    sys.exit()

saildrone = config['saildrone_for_dropsonde_comparison']
dt = config['saildrone_time_tolerance_minutes']
distance_range = config['saildrone_distance_tolerance_km']
print(f"Identify dropsondes in the vicininty of SD-{saildrone}")
start_date = config['dropsonde_start_date']
end_date = config['dropsonde_end_date']
print(f"Start date: {start_date.strftime('%Y-%m-%d')}")
print(f"End date: {end_date.strftime('%Y-%m-%d')}")
drop_dir = f"{repo_path}{os.sep}" + f"{config['download_aircraft_recon_dropsonde_data_path']}"
summary_dir =  f"{drop_dir}_SD{config['saildrone_for_dropsonde_comparison']}_" + f"{start_date.strftime('%Y%m%d')}-" + f"{end_date.strftime('%Y%m%d')}"
saildrone_dir = f"{repo_path}{os.sep}" + f"{config['download_saildrone_data_path']}"
check_for_dir_create(drop_dir)
check_for_dir_create(summary_dir)

fls = sorted(os.listdir(drop_dir))
drop_time = {fl: datetime.strptime(fl[1:16], "%Y%m%d_%H%M%S") for fl in fls}
relevant_drops = [key for key in drop_time if drop_time[key]]

sd_fls = os.listdir(saildrone_dir)
sd_filename = [fl for fl in sd_fls if f"{saildrone}" in fl][0]
sd = read_saildrone_format(filename=f"{saildrone_dir}{os.sep}{sd_filename}").round(2)
sd = sd[(start_date <= sd.date) & (sd.date <= end_date)].reset_index(drop=True)

csv_filename = f"{summary_dir}{os.sep}" + f"aircraft_recon_dropsonde_summary_" + f"{saildrone}.csv"
fl = open(csv_filename, "w")
add_text = "drop_file,min_distance_km,max_distance_km,note\n"
fl.write(add_text)
fl.close()
# check distance for all drops
for drop in relevant_drops:
    fl = open(csv_filename, "a")
    add_text = f"{drop},"
    current_drop_time = drop_time[drop]
    current_drop_start = current_drop_time - timedelta(minutes=dt)
    current_drop_end = current_drop_time + timedelta(minutes=dt)
    current_sd = sd[(current_drop_start <= sd.date) & (sd.date <= current_drop_end)].reset_index(drop=True)
    current_sd = current_sd[["date", "latitude", "longitude"]]
    current_sd = current_sd.dropna(thresh=3).reset_index(drop=True)
    if len(current_sd) == 0:
        add_text += ",,no saildrone data\n"
        fl.write(add_text)
        continue # move to next dropsonde as no saildrone data

    filename = f"{drop_dir}{os.sep}{drop}"
    drop_data = read_dropsonde_data(filename=filename)
    drop_data = drop_data[["time", "lat", "lon"]]
    drop_data = drop_data.dropna(thresh=3).reset_index(drop=True)
    if len(drop_data) == 0:
        add_text += ",,no dropsonde data\n"
        fl.write(add_text)
        continue # move to next dropsonde as no dropsonde data

    sd_lon = sd.longitude.mean()
    sd_lat = sd.latitude.mean()
    drop_data["distance"] = drop_data.apply(lambda x: great_circle_distance(x.lon, x.lat, sd_lon, sd_lat), axis=1,)
    min_distance = drop_data.distance.min()
    max_distance = drop_data.distance.max()
    add_text += f"{min_distance:.2f},{max_distance:.2f},\n"
    fl.write(add_text)
    fl.close()


# check distance within threshold
csv_filename_range = f"{summary_dir}{os.sep}" + f"aircraft_recon_dropsonde_summary_" + f"{saildrone}_{distance_range}km.csv"
data = pd.read_csv(csv_filename, header=0)
data = data[data.min_distance_km <= distance_range].reset_index()
data.to_csv(path_or_buf=csv_filename_range, index=False)









