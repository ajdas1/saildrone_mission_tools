import os
import pandas as pd
import pytz
import sys

import importlib
import read_file

importlib.reload(read_file)


from atcf_processing import column_names, column_types
from conversions import convert_time_to_utc
from datetime import datetime, timedelta
from paths import check_for_dir_create, read_yaml_config, repo_path
from read_file import read_raw_atcf

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


invest_fls = sorted([fl for fl in os.listdir(invest_dir) if "aal" in fl])
storm_fls = sorted([fl for fl in os.listdir(storm_dir) if "aal" in fl])
btk_fls = sorted([fl for fl in os.listdir(btk_dir) if "bal" in fl])

current_time = convert_time_to_utc(
    time=datetime.now(), timezone=pytz.timezone(config["local_timezone"])
)
fcst_time_last = current_time.replace(
    hour=current_time.hour // 6 * 6, minute=0, second=0, microsecond=0, tzinfo=None
)
fcst_time_plast = fcst_time_last - timedelta(hours=6)


for fl in btk_fls:
    new_name = f"{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat"
    df = read_raw_atcf(filename=f"{btk_dir}{os.sep}{fl}")
    df["Valid"] = df.Date
    df = df[
        [
            "StormName",
            "StormNumber",
            "Valid",
            "FcstCenter",
            "Latitude",
            "Longitude",
            "MaxSustainedWind",
            "MinSLP",
            "StormType",
        ]
    ]
    if df.Valid.iloc[-1] in [fcst_time_plast, fcst_time_last]:
        df.to_csv(f"{btk_dir}{os.sep}{new_name}", index=False)
    os.remove(f"{btk_dir}{os.sep}{fl}")

relevant_btk_fls = sorted(os.listdir(btk_dir))

for fl in storm_fls:
    new_name = f"{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat"
    if new_name in relevant_btk_fls:
        df = read_raw_atcf(filename=f"{storm_dir}{os.sep}{fl}")
        df = df[
            [
                "StormName",
                "StormNumber",
                "Date",
                "FcstCenter",
                "FcstHour",
                "Latitude",
                "Longitude",
                "MaxSustainedWind",
                "MinSLP",
                "StormType",
            ]
        ]
        df.to_csv(f"{storm_dir}{os.sep}{new_name}", index=False)
    os.remove(f"{storm_dir}{os.sep}{fl}")


for fl in invest_fls:
    new_name = f"{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat"
    if new_name in relevant_btk_fls:
        df = read_raw_atcf(filename=f"{invest_dir}{os.sep}{fl}")
        df = df[
            [
                "StormName",
                "StormNumber",
                "Date",
                "FcstCenter",
                "FcstHour",
                "Latitude",
                "Longitude",
                "MaxSustainedWind",
                "MinSLP",
                "StormType",
            ]
        ]
        df.to_csv(f"{invest_dir}{os.sep}{new_name}", index=False)
    os.remove(f"{invest_dir}{os.sep}{fl}")
