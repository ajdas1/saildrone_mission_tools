


import importlib

import paths
importlib.reload(paths)
import read_url
importlib.reload(read_url)

from paths import recon_mission_archive_full_dropsonde

import warnings
warnings.filterwarnings("ignore")

import os
import pytz
import sys

from conversions import convert_time_to_utc
from datetime import datetime, timedelta
from paths import (
    recon_mission_archive_high_density_obs,
    recon_mission_archive_dropsonde,
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from read_url import get_files_at_url, retrieve_url_file


config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_aicraft_recon_dropsonde_full"]:
    sys.exit()

print("Downloading full dropsonde data from aircraft recon.")
drop_dir = f"{repo_path}{os.sep}" + f"{config['download_aircraft_recon_dropsonde_data_path']}"
check_for_dir_create(drop_dir)


start_date = config["dropsonde_download_start_date"]
end_date = config["dropsonde_download_end_date"]
dates = [start_date + timedelta(days=dy) for dy in range(1000) if (start_date + timedelta(days=dy)) <= end_date]
dates_str = [dt.strftime("%Y%m%d") for dt in dates]

all_records = get_files_at_url(url=recon_mission_archive_full_dropsonde, verify=False)
valid_records = [rec for dt in dates_str for rec in all_records if dt in rec]

for rec in valid_records:
    sub_records = get_files_at_url(rec, verify=False)
    sub_drops = [fl for fl in sub_records if ".nc" in fl]
    for drop in sub_drops:
        filename = f"{drop_dir}{os.sep}{drop.split('/')[-1]}"
        dt = datetime.strptime(filename.split(os.sep)[-1].split("_")[0][1:], "%Y%m%d")
        if (not os.path.isfile(filename)) and (start_date <= dt <= end_date):
            retrieve_url_file(url=drop, destination=filename, verify=False)

