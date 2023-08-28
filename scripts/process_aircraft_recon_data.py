import os
import pytz
import sys

from conversions import convert_time_to_utc
from datetime import datetime
from paths import (
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from read_file import read_aircraft_recon_hdob_file

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_aircraft_recon"]:
    sys.exit()


current_time = convert_time_to_utc(datetime.now(), timezone=pytz.timezone(config["local_timezone"])).replace(tzinfo=None)

recon_dir = f"{repo_path}{os.sep}" + f"{config['download_recon_flight_data_path']}"
check_for_dir_create(recon_dir)

recon_fls = [fl for fl in os.listdir(recon_dir) if ".csv" not in fl]

for fl in recon_fls:
    data = read_aircraft_recon_hdob_file(filename=f"{recon_dir}{os.sep}{fl}", current_time = current_time)
    data = data.round(2)
    data.to_csv(f"{recon_dir}{os.sep}{fl[:-4]}.csv", index=False)
    os.remove(f"{recon_dir}{os.sep}{fl}")
