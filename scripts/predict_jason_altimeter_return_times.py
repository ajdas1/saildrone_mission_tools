import numpy as np
import os
import pandas as pd
import sys
import xarray as xr

from datetime import datetime, timedelta
from netCDF4 import Dataset
from paths import check_for_dir_create, read_yaml_config, repo_path
from projection import great_circle_distance

config_file = (
    f"{repo_path}{os.sep}configs{os.sep}download_predict_jason_path.yml"
)
config = read_yaml_config(config_file)

jason_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_jason3_data_path']}"
)

if not config["predict_overpass_at_location"]:
    sys.exit()


point_lat = config["predicted_point_lat"]
point_lon = config["predicted_point_lon"]

check_for_dir_create(jason_dir)
fls = sorted([f"{jason_dir}/{fl}" for fl in os.listdir(jason_dir)])

if len(fls) == 0:
    print("There is no data to establish a return period for a given location.")
    sys.exit()

print("Determining return period for chosen point.")
data = []
for fl in fls:
    with xr.open_dataset(fl, engine="netcdf4") as ds:
        tmp = ds.load().to_dataframe().reset_index()
        tmp.longitude = (tmp.longitude + 180) % 360 - 180
        tmp = tmp[(tmp.longitude >= point_lon-1.) & (tmp.longitude <= point_lon + 1.)]
        tmp = tmp[(tmp.latitude >= point_lat-1.) & (tmp.latitude <= point_lat + 1.)]
        data.append(tmp)

data = pd.concat(data, axis=0).reset_index(drop=True)
data["dt_days"] = ((data.time - data.time.iloc[0]).dt.total_seconds()/60/60/24).astype(int)
data["dist_point"] = data.apply(lambda x: great_circle_distance(x.longitude, x.latitude, point_lon, point_lat), axis=1)
nearest_dist = data.dist_point.min()
nearest_time = data[data.dist_point == nearest_dist].time.iloc[0]
nearest_lat = data[data.dist_point == nearest_dist].latitude.iloc[0]
nearest_lon = data[data.dist_point == nearest_dist].longitude.iloc[0]

print(f"Chosen location (lat, lon): ({point_lat}, {point_lon})")
print(f"The nearest point to the chosen location is {nearest_dist:.2f}" + f" km away at (lat, lon): ({nearest_lat:.4f}, " + f"{nearest_lon:.4f})")



data_return = data.loc[data.groupby("dt_days").dist_point.idxmin()].reset_index(drop=True)
data_return = data_return[data_return.dist_point <= 10]
data_return = data_return[["time", "latitude", "longitude", "dist_point"]]
avg_return_seconds = ((data_return.time - data_return.time.iloc[0]).dt.total_seconds()).diff().mean()


current_time = datetime.now()
return_times = [nearest_time + timedelta(seconds=avg_return_seconds*n) for n in range(100)]
return_times = [tm for tm in return_times if tm >= current_time][:config["number_of_future_overpasses"]]
return_times = [tm.strftime("%Y-%m-%d %H:%M:%S") for tm in return_times]
print("Return times for the chosen location: \n     " + "\n     ".join(return_times))
