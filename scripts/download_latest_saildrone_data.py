import os
import sys
import urllib.request
import urllib.error

import importlib
import paths

importlib.reload(paths)
from paths import check_for_dir_create, read_yaml_config, repo_path, saildrone_archive


config_file = f"{repo_path}{os.sep}configs{os.sep}download_saildrone_data.yml"
config = read_yaml_config(config_file)
all_saildrones = config["all_saildrones"].split(", ")
update_saildrones = config["update_saildrones"].split(", ")


if not config["download_saildrone_data"]:
    sys.exit()
elif len(update_saildrones) == 0:
    sys.exit()

saildrone_dir = f"{repo_path}{os.sep}" + f"{config['download_saildrone_data_path']}"

check_for_dir_create(saildrone_dir)

for sd in update_saildrones:
    print(f"Downloading the latest file for SD-{sd}.")
    filename = f"sd{sd}_hurricane_2023.ncCF"
    try:
        urllib.request.urlretrieve(
            f"{saildrone_archive}{filename}", f"{saildrone_dir}{os.sep}{filename[:-2]}"
        )
    except urllib.error.HTTPError:
        print("Could not download the latest data.")
        continue
