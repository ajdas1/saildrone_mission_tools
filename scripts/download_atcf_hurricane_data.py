import os
import requests
import subprocess
import sys
import urllib

from bs4 import BeautifulSoup
from paths import atcf_archive, check_for_dir_create, read_yaml_config, repo_path

config_file = (
    f"{repo_path}{os.sep}configs{os.sep}download_and_process_atcf_hurricane_data.yml"
)
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

for year in range(config["start_year"], config["end_year"]):
    print(f"Downloading ATCF data for year {year}")
    current_url = f"{atcf_archive}{year}{os.sep}"
    page = requests.get(current_url).text
    soup = BeautifulSoup(page, "html.parser")
    all_records = [f"{current_url}/{node.get('href')}" for node in soup.find_all("a")]
    a_records = [rec for rec in all_records if "aal" in rec]
    b_records = [rec for rec in all_records if "bal" in rec]

    for num, record in enumerate(a_records):
        filename = record.split("/")[-1]
        if ("aal5" not in filename) and ("aal8" not in filename):
            if not os.path.isfile(f"{adecks_dir}{os.sep}{filename}"):
                try:
                    urllib.request.urlretrieve(
                        record, f"{adecks_dir}{os.sep}{filename}"
                    )

                except urllib.error.HTTPError:
                    continue

            if ".gz" in filename:
                unzip_command = ["gunzip", f"{adecks_dir}{os.sep}{filename}"]
                subprocess.run(unzip_command)

    for num, record in enumerate(b_records):
        filename = record.split("/")[-1]
        if ("bal5" not in filename) and ("bal8" not in filename):
            if not os.path.isfile(f"{bdecks_dir}{os.sep}{filename}"):
                try:
                    urllib.request.urlretrieve(
                        record, f"{bdecks_dir}{os.sep}{filename}"
                    )

                except urllib.error.HTTPError:
                    continue

            if ".gz" in filename:
                unzip_command = ["gunzip", f"{bdecks_dir}{os.sep}{filename}"]
                subprocess.run(unzip_command)

    # adecks_unzip = sorted([fl for fl in os.listdir(adecks_dir) if ".gz" in fl])
    # bdecks_unzip = sorted([fl for fl in os.listdir(bdecks_dir) if ".gz" in fl])

    # for fl in adecks_unzip:
    #     unzip_command = ["gunzip", f"{adecks_dir}{os.sep}{fl}"]
    #     subprocess.run(unzip_command)

    # for fl in bdecks_unzip:
    #     unzip_command = ["gunzip", f"{bdecks_dir}{os.sep}{fl}"]
    #     subprocess.run(unzip_command)
