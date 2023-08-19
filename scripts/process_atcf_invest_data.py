import os
import pandas as pd
import sys

import importlib
import read_file
importlib.reload(read_file)


from atcf_processing import column_names, column_types
from paths import check_for_dir_create, read_yaml_config, repo_path
from read_file import read_raw_atcf

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

invest_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_nhc_invest_data_path']}"
)
check_for_dir_create(invest_dir)

if not config["download_nhc_invest_data"]:
    sys.exit()

invest_fls = [fl for fl in os.listdir(invest_dir) if "aal" in fl]

for fl in invest_fls:
    df = read_raw_atcf(filename=f"{invest_dir}{os.sep}{fl}")
    df = df[["StormNumber", "Date", "FcstCenter", "FcstHour", "Latitude", "Longitude", "MaxSustainedWind", "MinSLP"]]
    df.to_csv(f"{invest_dir}{os.sep}{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat", index=False)
    os.remove(f"{invest_dir}{os.sep}{fl}")

    