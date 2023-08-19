
import os
import pandas as pd
import sys


from paths import check_for_dir_create, read_yaml_config, repo_path


import importlib
import plotting
importlib.reload(plotting)

from plotting import plot_invest_track, plot_invest_winds

# import pandas as pd
# import pytz
# import sys
# import warnings

# from atcf_processing import count_overlapping_features, download_outlook_shapefile, read_shapefile_areas, split_storms_into_wind_radii, subset_btk_in_region, unzip_shapefile
# from conversions import convert_time_to_utc
# from datetime import datetime
# from plotting import plot_shapefile, plot_shapefile_btkstart
# from read_file import read_all_btks, read_saildrone_latest_position

# warnings.filterwarnings('ignore')

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

invest_dir = f"{repo_path}{os.sep}{config['download_nhc_invest_data_path']}"
fig_dir = f"{repo_path}{os.sep}{config['figure_path']}{os.sep}" + f"{config['invest_figure_path']}{os.sep}latest"
check_for_dir_create(invest_dir)
check_for_dir_create(fig_dir)

fls = sorted(os.listdir(invest_dir))
if len(fls) == 0:
    print("There are no invests to summarize.")
    sys.exit()

invest_data_latest = []
for invest in fls:
    df = pd.read_csv(f"{invest_dir}{os.sep}{invest}", header=0, delimiter=",")
    df.Date = pd.to_datetime(df.Date)
    df["Valid"] = df.Date + pd.to_timedelta(df.FcstHour, unit="hr")
    # only consider the latest one.
    df_latest = df[df.Date == df.Date.max()].reset_index(drop=True)
    invest_data_latest.append(df_latest)



for invest in range(len(fls)):
    current_data = invest_data_latest[invest]
    filename = f"{fig_dir}{os.sep}AL{current_data.StormNumber.iloc[0]}_track.png"
    plot_invest_track(data=current_data, filename=filename)
    filename = f"{fig_dir}{os.sep}AL{current_data.StormNumber.iloc[0]}_intensity.png"
    plot_invest_winds(data=current_data, filename=filename)
