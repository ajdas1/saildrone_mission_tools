


# import importlib

import os
# import pandas as pd
# import pytz
# import sys

# from atcf_processing import count_overlapping_features, download_outlook_shapefile, read_shapefile_areas, split_storms_into_wind_radii, subset_btk_in_region, unzip_shapefile
# from conversions import convert_time_to_utc
# from datetime import datetime
from paths import check_for_dir_create, read_yaml_config, repo_path
# from plotting import plot_shapefile, plot_shapefile_btkstart
# from read_file import read_all_btks, read_saildrone_latest_position



config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

outlook_dir = f"{repo_path}{os.sep}{config['download_nhc_outlook_data_path']}"
check_for_dir_create(outlook_dir)






# print("     Creating figure packet and pdf output.")
# create_figure_packet(time=latest_time, remove_orig=True)
# latex_file = modify_latex_template(time=datetime.now(), n_areas=len(shapes["areas"]), sd_data=sd_data)
# compile_latex_file(filename=latex_file)
# clean_up_data(time=latest_time)

