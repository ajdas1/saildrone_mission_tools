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

if not config["download_aircraft_recon"]:
    sys.exit()

print("Downloading the flight level and dropsonde data from aircraft reconnaissance.")
# flight level
recon_dir = f"{repo_path}{os.sep}" + f"{config['download_recon_flight_data_path']}"
check_for_dir_create(recon_dir, empty=True)

current_time = convert_time_to_utc(
    datetime.now(), timezone=pytz.timezone(config["local_timezone"])
).replace(tzinfo=None)
tolerance_time = current_time - timedelta(hours=config["aircraft_recon_hours_back"])

all_records = get_files_at_url(
    url=recon_mission_archive_high_density_obs, parse_for="a"
)
all_records = [rec for rec in all_records if ".txt" in rec]
record_time = [
    datetime.strptime(rec.split(".")[-2], "%Y%m%d%H%M") for rec in all_records
]
valid_records = [
    rec for idx, rec in enumerate(all_records) if record_time[idx] >= tolerance_time
]


for file in valid_records:
    filename = file.split("/")[-1]
    retrieve_url_file(file, f"{recon_dir}{os.sep}{filename}")


# dropsonde
recon_dir = f"{repo_path}{os.sep}" + f"{config['download_recon_dropsonde_data_path']}"
check_for_dir_create(recon_dir, empty=True)

all_records = get_files_at_url(url=recon_mission_archive_dropsonde, parse_for="a")
all_records = [rec for rec in all_records if ".txt" in rec]
record_time = [
    datetime.strptime(rec.split(".")[-2], "%Y%m%d%H%M") for rec in all_records
]
valid_records = [
    rec for idx, rec in enumerate(all_records) if record_time[idx] >= tolerance_time
]


for file in valid_records:
    filename = file.split("/")[-1]
    retrieve_url_file(file, f"{recon_dir}{os.sep}{filename}")
