import importlib



import os
import re
import sys

import paths
importlib.reload(paths)
from paths import (
    recon_mission_archive,
    atcf_storm_archive,
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from read_url import get_files_at_url, retrieve_url_file


config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_aircraft_recon"]:
    sys.exit()

all_records, modified_times = get_files_at_url(url=recon_mission_archive, parse_for="a")
# recon_records = [rec for rec in all_records if "recon_" in rec]