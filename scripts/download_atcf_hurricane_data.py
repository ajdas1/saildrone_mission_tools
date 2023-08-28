import os
import subprocess
import sys

from paths import atcf_archive, check_for_dir_create, read_yaml_config, repo_path
from read_url import get_files_at_url, retrieve_url_file

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_nhc_atcf_data"]:
    sys.exit()

# forecasts
adecks_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_nhc_atcf_data_path']}{os.sep}"
    + f"adecks{os.sep}downloaded"
)
# best track
bdecks_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_nhc_atcf_data_path']}{os.sep}"
    + f"bdecks{os.sep}downloaded"
)
check_for_dir_create(adecks_dir)
check_for_dir_create(bdecks_dir)

for year in range(config["atcf_start_year"], config["atcf_end_year"]):
    print(f"Downloading ATCF data for year {year}")
    all_records, _ = get_files_at_url(url=f"{atcf_archive}{year}{os.sep}")
    a_records = [rec for rec in all_records if "aal" in rec]
    b_records = [rec for rec in all_records if "bal" in rec]

    for num, record in enumerate(a_records):
        filename = record.split("/")[-1]
        if ("aal5" not in filename) and ("aal8" not in filename):
            if not os.path.isfile(f"{adecks_dir}{os.sep}{filename}"):
                retrieve_url_file(record, f"{adecks_dir}{os.sep}{filename}")

            if ".gz" in filename:
                unzip_command = ["gunzip", f"{adecks_dir}{os.sep}{filename}"]
                subprocess.run(unzip_command)

    for num, record in enumerate(b_records):
        filename = record.split("/")[-1]
        if ("bal5" not in filename) and ("bal8" not in filename):
            if not os.path.isfile(f"{bdecks_dir}{os.sep}{filename}"):
                retrieve_url_file(record, f"{bdecks_dir}{os.sep}{filename}")

            if ".gz" in filename:
                unzip_command = ["gunzip", f"{bdecks_dir}{os.sep}{filename}"]
                subprocess.run(unzip_command)
