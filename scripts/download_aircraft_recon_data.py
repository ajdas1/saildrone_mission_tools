import os
import pytz
import sys

from conversions import convert_time_to_utc, get_mission_names_form_tidbits_link
from datetime import datetime, timedelta


from paths import (
    recon_mission_archive,
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from read_url import get_files_at_url, retrieve_url_file


config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_aircraft_recon"]:
    sys.exit()


recon_dir = f"{repo_path}{os.sep}" + f"{config['download_recon_flight_data_path']}"
check_for_dir_create(recon_dir, empty=True)

current_time = convert_time_to_utc(datetime.now(), timezone=pytz.timezone(config["local_timezone"]))

all_records, modified_times = get_files_at_url(url=recon_mission_archive, parse_for="a")
recon_records = [rec for idx, rec in enumerate(all_records) if ("recon_" in rec) and (modified_times[idx] >= (current_time - timedelta(hours=12)).replace(tzinfo=None))]
recon_info = [get_mission_names_form_tidbits_link(rec) for rec in recon_records]

for file in recon_records:
    filename = file.split("/")[-1].split("recon_")[-1]
    retrieve_url_file(file, f"{recon_dir}{os.sep}{filename}")