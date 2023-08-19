import importlib


import os
import re
import sys


import paths
importlib.reload(paths)
import read_url
importlib.reload(read_url)

from datetime import datetime
from paths import atcf_invest_archive, check_for_dir_create, read_yaml_config, repo_path
from read_url import get_files_at_url, retrieve_url_file



config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_nhc_invest_data"]:
    sys.exit()


invest_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_nhc_invest_data_path']}"
)
check_for_dir_create(invest_dir)

current_year = datetime.now().strftime("%Y")
all_records = get_files_at_url(url=atcf_invest_archive)
invest_records = [rec for rec in all_records if re.match(f".*aal9.{current_year}", rec)]
invest_number = [f"AL{rec[-13:-11]}" for rec in invest_records]
invest_records_of_interest = [rec for idx, rec in enumerate(invest_records) if invest_number[idx] in config["invests_of_interest"]]
invest_number_of_interest = [rec for rec in invest_number if rec in config["invests_of_interest"]]

for idx, invest in enumerate(invest_records_of_interest):
    print(f"Downloading ATCF data for invest {invest_number_of_interest[idx]}.")
    filename = invest.split("/")[-1]
    retrieve_url_file(invest, f"{invest_dir}{os.sep}{filename}")
