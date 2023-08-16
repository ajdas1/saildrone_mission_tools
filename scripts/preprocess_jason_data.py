
import os
import sys
import xarray as xr

from netCDF4 import Dataset
from paths import check_for_dir_create, read_yaml_config, repo_path


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
fls = [f"{jason_dir}/{fl}" for fl in os.listdir(jason_dir)]
print("Extracting lat, lon, and time from JASON-3 data.")
for fl in fls:
    try:
        with xr.open_dataset(fl, engine="netcdf4", group="data_20") as ds:
            ds.load()
        ds = ds[["time", "latitude", "longitude"]]
        ds.to_netcdf(fl, mode="w", engine="netcdf4")
    except OSError:
        continue
    
