import os
import pandas as pd
import pytz
import sys

from conversions import convert_time_to_utc
from datetime import datetime
from paths import (
    check_for_dir_create,
    read_yaml_config,
    repo_path,
)
from read_file import combine_aircraft_recon_drop, combine_aircraft_recon_hdob, interpret_dropsonde_text_file

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_aircraft_recon"]:
    sys.exit()


current_time = convert_time_to_utc(datetime.now(), timezone=pytz.timezone(config["local_timezone"])).replace(tzinfo=None)

recon_flight_dir = f"{repo_path}{os.sep}" + f"{config['download_recon_flight_data_path']}"
recon_drop_dir = f"{repo_path}{os.sep}" + f"{config['download_recon_dropsonde_data_path']}"
check_for_dir_create(recon_flight_dir)
check_for_dir_create(recon_drop_dir)



recon_fls = sorted([fl for fl in os.listdir(recon_flight_dir) if ".csv" not in fl])
recon_fls_knhc = [fl for fl in recon_fls if "KNHC" in fl]
recon_fls_kwbc = [fl for fl in recon_fls if "KWBC" in fl]
recon_drops = sorted([fl for fl in os.listdir(recon_drop_dir) if ".csv" not in fl])

knhc_flight_data = []
for fl in recon_fls_knhc:
    with open(f"{recon_flight_dir}{os.sep}{fl}", "r") as file:
        data = file.readlines()
    data = [line.rstrip() for line in data]
    data = [line for line in data if len(line) > 2]
    knhc_flight_data.append(data)


for fl in recon_drops:
    with open(f"{recon_drop_dir}{os.sep}{fl}", "r") as file:
        data = file.readlines()
    
    drop_data = interpret_dropsonde_text_file(data=data, filename=fl)
    drop_data = drop_data.round(2)
    drop_data = drop_data[drop_data.pressure > 100]

    file_save = f"{recon_drop_dir}{os.sep}{fl[:-3]}csv"
    drop_data.to_csv(file_save, index=False)
    os.remove(f"{recon_drop_dir}{os.sep}{fl}")

recon_drops = sorted([fl for fl in os.listdir(recon_drop_dir) if ".csv" in fl])
recon_drops_knhc = [fl for fl in recon_drops if "KNHC" in fl]
recon_drops_kwbc = [fl for fl in recon_drops if "KWBC" in fl]

knhc_drop_data = []
for fl in recon_drops_knhc:
    knhc_drop_data.append(pd.read_csv(f"{recon_drop_dir}{os.sep}{fl}"))


knhc_flight = [fl[2].split("  ")[0] for fl in knhc_flight_data]
knhc_drop = [f"{df.aircraft.iloc[0]} {df.flight_id.iloc[0]} {df.storm.iloc[0]}" for df in knhc_drop_data]
knhc_flight_unique = sorted(list(set(knhc_flight)))
for flight in knhc_flight_unique:
    center = "KNHC"
    flight_data_ids = combine_aircraft_recon_hdob(data=knhc_flight_data, flight=flight, flight_list=knhc_flight, recon_dir=recon_flight_dir, center=center)
    for idx in flight_data_ids:
        os.remove(f"{recon_flight_dir}{os.sep}{recon_fls_knhc[idx]}")
    
    drop_data_ids, drop_data = combine_aircraft_recon_drop(data=knhc_drop_data, flight=flight, flight_list=knhc_drop, recon_dir=recon_drop_dir, center=center)
    
    if len(drop_data) > 0:    
        flight_date = datetime.strptime(recon_drops_knhc[drop_data_ids[0]].split(".")[1], "%Y%m%d%H%M")
        filename = f"{recon_drop_dir}{os.sep}{center}_{flight_date.strftime('%Y%m%d')}_{flight.replace(' ', '-')}.csv"
        drop_data.to_csv(filename, index=False)
        for idx in drop_data_ids:
            os.remove(f"{recon_drop_dir}{os.sep}{recon_drops_knhc[idx]}")



kwbc_flight_data = []
for fl in recon_fls_kwbc:
    with open(f"{recon_flight_dir}{os.sep}{fl}", "r") as file:
        data = file.readlines()
    data = [line.rstrip() for line in data]
    data = [line for line in data if len(line) > 2]
    kwbc_flight_data.append(data)

kwbc_drop_data = []
for fl in recon_drops_kwbc:
    kwbc_drop_data.append(pd.read_csv(f"{recon_drop_dir}{os.sep}{fl}"))


kwbc_flight = [fl[2].split("  ")[0] for fl in kwbc_flight_data]
kwbc_drop = [f"{df.aircraft.iloc[0]} {df.flight_id.iloc[0]} {df.storm.iloc[0]}" for df in kwbc_drop_data]
kwbc_flight_unique = sorted(list(set(kwbc_flight)))
for flight in kwbc_flight_unique:
    center = "KNHC"
    flight_data_ids = combine_aircraft_recon_hdob(data=kwbc_flight_data, flight=flight, flight_list=kwbc_flight, recon_dir=recon_flight_dir, center=center)
    for idx in flight_data_ids:
        os.remove(f"{recon_flight_dir}{os.sep}{recon_fls_kwbc[idx]}")

    drop_data_ids, drop_data = combine_aircraft_recon_drop(data=kwbc_drop_data, flight=flight, flight_list=kwbc_drop, recon_dir=recon_drop_dir, center=center)
    
    if len(drop_data) > 0:    
        flight_date = datetime.strptime(recon_drops_kwbc[drop_data_ids[0]].split(".")[1], "%Y%m%d%H%M")
        filename = f"{recon_drop_dir}{os.sep}{center}_{flight_date.strftime('%Y%m%d')}_{flight.replace(' ', '-')}.csv"
        drop_data.to_csv(filename, index=False)
        for idx in drop_data_ids:
            os.remove(f"{recon_drop_dir}{os.sep}{recon_drops_kwbc[idx]}")
