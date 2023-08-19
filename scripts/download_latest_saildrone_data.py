import os
import sys

from paths import check_for_dir_create, read_yaml_config, repo_path, saildrone_archive
from read_url import retrieve_url_file


config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
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
    retrieve_url_file(url=f"{saildrone_archive}{filename}", destination=f"{saildrone_dir}{os.sep}{filename[:-2]}")
