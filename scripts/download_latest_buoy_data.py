import os
import sys

from paths import check_for_dir_create, read_yaml_config, repo_path, buoy_archive
from read_url import retrieve_url_file

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)
buoys = config["buoys"].split(", ")

if not config["download_buoy_data"]:
    sys.exit()
elif len(buoys) == 0:
    sys.exit()

buoy_dir = f"{repo_path}{os.sep}" + f"{config['download_buoy_data_path']}"

check_for_dir_create(buoy_dir)

for buoy in buoys:
    if len(buoy) > 0:
        print(f"Downloading the latest data for buoy {buoy}.")
        retrieve_url_file(
            f"{buoy_archive}{buoy}.txt", f"{buoy_dir}{os.sep}buoy_{buoy}.txt"
        )
