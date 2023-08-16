
import os
import requests
import sys
import urllib
import xarray as xr

from bs4 import BeautifulSoup
from paths import check_for_dir_create, jason3_archive, read_yaml_config, repo_path


config_file = (
    f"{repo_path}{os.sep}configs{os.sep}download_predict_jason_path.yml"
)
config = read_yaml_config(config_file)

if not config["download_jason3_data"]:
    sys.exit()

jason_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_jason3_data_path']}"
)

check_for_dir_create(jason_dir)

page = requests.get(jason3_archive).text
soup = BeautifulSoup(page, "html.parser")
all_records = [f"{jason3_archive}{node.get('href')}" for node in soup.find_all("a")]
all_records = [fl for fl in all_records if "/cycle" in fl]
all_records = all_records[-config["number_most_recent_cycles_to_download"]:]
for record in range(config["number_most_recent_cycles_to_download"]):
    current_record = all_records[record]
    print(f"Downloading JASON-3 data for cycle {current_record}")
    page = requests.get(current_record).text
    soup = BeautifulSoup(page, "html.parser")
    current_records = [f"{current_record}{node.get('href')}" for node in soup.find_all("a")]
    current_records = [fl for fl in current_records if fl[-3:] == ".nc"]
    for num, file in enumerate(current_records):
        filename = file.split("/")[-1]
        if not os.path.isfile(f"{jason_dir}{os.sep}{filename}"):
            try:
                urllib.request.urlretrieve(file, f"{jason_dir}{os.sep}{filename}")
                # data = xr.open_dataset(f"{jason_dir}{os.sep}{filename}", engine="netcdf4")
                # if data.variables == {}:
                #     os.remove(f"{jason_dir}{os.sep}{filename}")
            except urllib.error.HTTPError:
                continue

