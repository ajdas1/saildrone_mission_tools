import os
import re
import sys
import paths
from paths import (
    atcf_btk_archive,
    atcf_storm_archive,
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from read_url import get_files_at_url, retrieve_url_file


config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not (
    config["download_nhc_invest_data"]
    or config["download_nhc_storm_data"]
    or config["download_nhc_btk_data"]
):
    sys.exit()


invest_dir = f"{repo_path}{os.sep}" + f"{config['download_nhc_invest_data_path']}"
storm_dir = f"{repo_path}{os.sep}" + f"{config['download_nhc_storm_data_path']}"
btk_dir = f"{repo_path}{os.sep}" + f"{config['download_nhc_btk_data_path']}"
check_for_dir_create(invest_dir)
check_for_dir_create(storm_dir)
check_for_dir_create(btk_dir)

# for invest and storm
all_records = get_files_at_url(url=atcf_storm_archive)
invest_records = [rec for rec in all_records if re.match(f".*aal9.", rec)]
storm_records = [rec for rec in all_records if re.match(f".*aal[^9]\d", rec)]

# download all of them, will weed out in the next step
print(f"Downloading ATCF data for invests.")
for invest in invest_records:
    filename = invest.split("/")[-1]
    retrieve_url_file(invest, f"{invest_dir}{os.sep}{filename}")

print(f"Downloading ATCF data for storms.")
for storm in storm_records:
    filename = storm.split("/")[-1]
    retrieve_url_file(storm, f"{storm_dir}{os.sep}{filename}")

# for best track
all_records = get_files_at_url(url=atcf_btk_archive)
btk_records = [rec for rec in all_records if ".dat" in rec and "bal" in rec]
print(f"Downloading ATCF best track data.")
for btk in btk_records:
    filename = btk.split("/")[-1]
    retrieve_url_file(btk, f"{btk_dir}{os.sep}{filename}")
