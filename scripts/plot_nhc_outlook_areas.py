import os
import pandas as pd
import pytz
import sys
import warnings
import importlib
import plotting

importlib.reload(plotting)
import read_file

importlib.reload(read_file)
from atcf_processing import (
    count_overlapping_features,
    download_outlook_shapefile,
    read_shapefile_areas,
    split_storms_into_wind_radii,
    subset_btk_in_region,
    unzip_shapefile,
)
from conversions import convert_time_to_utc
from datetime import datetime
from paths import check_for_dir_create, read_yaml_config, repo_path
from plotting import (
    plot_system_track,
    plot_system_winds,
    plot_shapefile,
    plot_shapefile_with_btks,
    plot_shapefile_with_fcsts,
    plot_shapefile_with_btks_and_fcsts,
    plot_shapefile_btkstart,
)
from read_file import (
    read_all_btks,
    read_saildrone_latest_position,
    remove_atcf_duplicates,
)

warnings.filterwarnings("ignore")

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

outlook_dir = f"{repo_path}{os.sep}{config['download_nhc_outlook_data_path']}"
invest_dir = f"{repo_path}{os.sep}" + f"{config['download_nhc_invest_data_path']}"
storm_dir = f"{repo_path}{os.sep}" + f"{config['download_nhc_storm_data_path']}"
btk_dir = f"{repo_path}{os.sep}" + f"{config['download_nhc_btk_data_path']}"
check_for_dir_create(outlook_dir)
check_for_dir_create(invest_dir)
check_for_dir_create(storm_dir)
check_for_dir_create(btk_dir)


current_time = convert_time_to_utc(
    time=datetime.now(), timezone=pytz.timezone(config["local_timezone"])
)
outlook_fl, outlook_time = download_outlook_shapefile(
    time=current_time, savedir=outlook_dir
)

if outlook_time is None:
    print("There have been no updated outlooks in the past 24 hours.")
    sys.exit()

# get shapefiles and update saildrone positions
print(f"The current time is: {current_time.strftime('%Y-%m-%d %H:%M')} UTC.")
print(
    f"The latest update to outlook areas was made on: {outlook_time.strftime('%Y-%m-%d %H:%M')} UTC."
)
outlook_fls = unzip_shapefile(filename=outlook_fl, overwrite=True, remove=True)
sd_position = read_saildrone_latest_position()
shapes = read_shapefile_areas(directory=outlook_fls)
shapes = (
    shapes[shapes.BASIN == "Atlantic"].sort_values(by="AREA").reset_index(drop=True)
)
fig_dir = (
    f"{repo_path}{os.sep}{config['figure_path']}{os.sep}"
    + f"{config['outlook_figure_path']}{os.sep}"
    + f"{outlook_time.strftime('%Y%m%d%H%M')}"
)
check_for_dir_create(fig_dir)

print("     Plotting shapefiles.")

btk_fls = sorted(os.listdir(btk_dir))
btk_data = {}
for btk in btk_fls:
    df = pd.read_csv(f"{btk_dir}{os.sep}{btk}", header=0, delimiter=",")
    df.Valid = pd.to_datetime(df.Valid)
    btk_data[btk] = df
btk_data = remove_atcf_duplicates(data=btk_data)

fcst_data = {}
for fcst in btk_data:
    try:
        df = pd.read_csv(f"{storm_dir}{os.sep}{fcst}", header=0, delimiter=",")
    except FileNotFoundError:
        df = pd.read_csv(f"{invest_dir}{os.sep}{fcst}", header=0, delimiter=",")

    df = df[df.Date == df.Date.max()]
    df["Valid"] = pd.to_datetime(df.Date) + pd.to_timedelta(df.FcstHour, unit="hr")
    fcst_data[fcst] = df

plot_shapefile(
    shapefile_data=shapes, time=outlook_time, savedir=fig_dir, sd_data=sd_position
)
plot_shapefile_with_btks(
    shapefile_data=shapes,
    btk_data=btk_data,
    time=outlook_time,
    savedir=fig_dir,
    sd_data=sd_position,
)
plot_shapefile_with_fcsts(
    shapefile_data=shapes,
    fcst_data=fcst_data,
    time=outlook_time,
    savedir=fig_dir,
    sd_data=sd_position,
)
plot_shapefile_with_btks_and_fcsts(
    shapefile_data=shapes,
    btk_data=btk_data,
    fcst_data=fcst_data,
    time=outlook_time,
    savedir=fig_dir,
    sd_data=sd_position,
)


print("     Plotting forecasts for existing systems.")
for idx, system in enumerate(btk_data):
    current_btk = btk_data[system]
    current_fcst = fcst_data[system]
    current_fcst = current_fcst[current_fcst.FcstHour >= 0]

    filename = f"{fig_dir}{os.sep}storm{idx+1:02d}_track.png"
    plot_system_track(
        btk_data=current_btk,
        fcst_data=current_fcst,
        filename=filename,
        sd_data=sd_position,
    )
    filename = f"{fig_dir}{os.sep}storm{idx+1:02d}_intensity.png"
    plot_system_winds(btk_data=current_btk, fcst_data=current_fcst, filename=filename)


print("     Processing best track data.")
btks_ts = read_all_btks(wr=34)
btks_subset_regions_ts = []
for region in range(len(shapes)):
    tmp = subset_btk_in_region(
        btk=btks_ts, target_region=shapes.geometry.iloc[region], verbose=False
    )
    btks_subset_regions_ts.append(tmp)

print("     Plotting best track overlap - all time")
for region in range(len(shapes)):
    area_num = shapes.iloc[region].AREA
    btk_region = btks_subset_regions_ts[region]["start"]
    storm = split_storms_into_wind_radii(storm_wr=btk_region)
    storm_overlap = count_overlapping_features(geo_dataset=storm)
    storm_overlap["percentage"] = storm_overlap["count"] / len(btk_region) * 100

    plot_shapefile_btkstart(
        shapefile_data=shapes.iloc[region],
        wind_overlap=storm_overlap,
        n=area_num,
        n_storms=len(btk_region),
        time=outlook_time,
        sd_data=sd_position,
        savedir=fig_dir,
        percentage=False,
    )


print("     Plotting best_track overlap - one day at a time")
for region in range(len(shapes)):
    area_num = shapes.iloc[region].AREA
    btk_region = btks_subset_regions_ts[region]["start"]
    btk_region_tmp = []
    for storm in btk_region:
        storm["StormDay"] = (
            ((storm["Date"] - storm["Date"].iloc[0]) / pd.Timedelta(hours=1)) // 24
        ) + 1
        btk_region_tmp.append(storm)
    btk_region = btk_region_tmp

    if len(btk_region) > 0:
        n_days = [int(max(tmp.StormDay)) for tmp in btk_region]
        n_days_max = 10
        for day in range(1, n_days_max + 1):
            btk_sub = [
                storm for idx, storm in enumerate(btk_region) if day <= n_days[idx]
            ]
            btk_sub = [storm[storm.StormDay == day] for storm in btk_sub]
            storm = split_storms_into_wind_radii(storm_wr=btk_sub)
            storm_overlap = count_overlapping_features(geo_dataset=storm)
            storm_overlap["percentage"] = storm_overlap["count"] / len(btk_sub) * 100

            plot_shapefile_btkstart(
                shapefile_data=shapes.iloc[region],
                wind_overlap=storm_overlap,
                n=area_num,
                n_storms=len(btk_sub),
                time=outlook_time,
                sd_data=sd_position,
                savedir=fig_dir,
                title_save_add=f"_day{day:02d}",
                percentage=False,
            )
