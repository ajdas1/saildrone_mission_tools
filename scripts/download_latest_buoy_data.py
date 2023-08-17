import os
import sys
import urllib.request
import urllib.error

import importlib
import paths

importlib.reload(paths)
from paths import check_for_dir_create, read_yaml_config, repo_path, buoy_archive

config_file = f"{repo_path}{os.sep}configs{os.sep}download_buoy_data.yml"
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
        try:
            urllib.request.urlretrieve(
                f"{buoy_archive}{buoy}.txt", f"{buoy_dir}{os.sep}buoy_{buoy}.txt"
            )
        except urllib.error.HTTPError:
            print("Could not download the latest data.")
            continue
