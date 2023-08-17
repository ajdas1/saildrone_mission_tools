import os
import pandas as pd

import importlib
import atcf_processing

importlib.reload(atcf_processing)
from atcf_processing import (
    column_names,
    column_types,
    fix_atcf_latitude,
    fix_atcf_longitude,
    get_atcf_files,
)
from paths import check_for_dir_create, read_yaml_config, repo_path

config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

# forecasts
adecks_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_nhc_atcf_data_path']}{os.sep}"
    + f"adecks{os.sep}downloaded"
)
# best track
bdecks_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_nhc_atcf_data_path']}{os.sep}"
    + f"bdecks{os.sep}downloaded"
)
check_for_dir_create(adecks_dir)
check_for_dir_create(bdecks_dir)


preprocess_wind_radii = config["preprocess_atcf_wind_radii"]


if config["download_nhc_atcf_data"]:
    for fl in os.listdir(adecks_dir):
        if "aal" in fl:
            df = pd.read_csv(
                f"{adecks_dir}{os.sep}{fl}",
                header=None,
                names=column_names,
                dtype=column_types,
                delimiter=",",
                index_col=False,
                skipinitialspace=True,
                na_values=["Q"],
            )
            df.Date = pd.to_datetime(df.Date, format="%Y%m%d%H")
            df.Latitude = df.Latitude.apply(fix_atcf_latitude)
            df.Longitude = df.Longitude.apply(fix_atcf_longitude)
            df.to_csv(
                f"{adecks_dir}{os.sep}{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat", index=False
            )
            os.remove(f"{adecks_dir}{os.sep}{fl}")

    for fl in os.listdir(bdecks_dir):
        if "bal" in fl:
            df = pd.read_csv(
                f"{bdecks_dir}{os.sep}{fl}",
                header=None,
                names=column_names,
                dtype=column_types,
                delimiter=",",
                index_col=False,
                skipinitialspace=True,
            )
            df.Date = pd.to_datetime(df.Date, format="%Y%m%d%H")
            df.Latitude = df.Latitude.apply(fix_atcf_latitude)
            df.Longitude = df.Longitude.apply(fix_atcf_longitude)
            df.to_csv(
                f"{bdecks_dir}{os.sep}{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat", index=False
            )
            os.remove(f"{bdecks_dir}{os.sep}{fl}")


if preprocess_wind_radii:
    adecks_dir_windradii = (
        f"{f'{os.sep}'.join(adecks_dir.split(os.sep)[:-1])}{os.sep}" + f"wind_radii"
    )
    bdecks_dir_windradii = (
        f"{f'{os.sep}'.join(bdecks_dir.split(os.sep)[:-1])}{os.sep}" + f"wind_radii"
    )
    check_for_dir_create(adecks_dir_windradii)
    check_for_dir_create(bdecks_dir_windradii)
    fls = get_atcf_files()
    for fl in fls:
        df = pd.read_csv(f"{adecks_dir}{os.sep}{fl}")
        df.Date = pd.to_datetime(df.Date)
        df = df.drop(
            columns=[
                "Technum",
                "MinSLP",
                "StormType",
                "WindCode",
                "PressureOfLastClosedIsobar",
                "RadiusOfLastClosedIsobar",
                "RMW",
                "Gust",
                "EyeDiameter",
                "SubregionCode",
                "MaxSeas",
                "ForecasterInitials",
                "StormDirection",
                "StormSpeed",
                "StormDepth",
                "WaveHeightForRadius",
                "RadiusQuadrantCode",
                "SeasRadius1",
                "SeasRadius2",
                "SeasRadius3",
                "SeasRadius4",
                "x",
                "xx",
                "xxx",
                "xxxx",
                "xxxxx",
                "xxxxxx",
                "xxxxxxx",
                "xxxxxxxx",
                "xxxxxxxxx",
                "y",
                "yy",
            ]
        )

        wrs = sorted(df.WindIntensityForRadii.unique())
        for wr in wrs:
            if (not pd.isna(wr)) and (wr > 0):
                df_sub = df[df.WindIntensityForRadii == wr]
                df_sub = df_sub.reset_index(drop=True)
                df_sub = df_sub.drop(columns=["WindIntensityForRadii"])
                if len(df_sub) > 0:
                    df_sub.to_csv(
                        f"{adecks_dir_windradii}{os.sep}{fl[:-4]}_{wr}kt.dat",
                        index=False,
                    )

        df = pd.read_csv(f"{bdecks_dir}{os.sep}{fl}")
        df.Date = pd.to_datetime(df.Date)
        df = df.drop(
            columns=[
                "Technum",
                "MinSLP",
                "StormType",
                "WindCode",
                "PressureOfLastClosedIsobar",
                "RadiusOfLastClosedIsobar",
                "RMW",
                "Gust",
                "EyeDiameter",
                "SubregionCode",
                "MaxSeas",
                "ForecasterInitials",
                "StormDirection",
                "StormSpeed",
                "StormDepth",
                "WaveHeightForRadius",
                "RadiusQuadrantCode",
                "SeasRadius1",
                "SeasRadius2",
                "SeasRadius3",
                "SeasRadius4",
                "x",
                "xx",
                "xxx",
                "xxxx",
                "xxxxx",
                "xxxxxx",
                "xxxxxxx",
                "xxxxxxxx",
                "xxxxxxxxx",
                "y",
                "yy",
            ]
        )

        wrs = sorted(df.WindIntensityForRadii.unique())
        for wr in wrs:
            if (not pd.isna(wr)) and (wr > 0):
                df_sub = df[df.WindIntensityForRadii == wr]
                df_sub = df_sub.reset_index(drop=True)
                df_sub = df_sub.drop(columns=["WindIntensityForRadii"])
                if len(df_sub) > 0:
                    df_sub.to_csv(
                        f"{bdecks_dir_windradii}{os.sep}{fl[:-4]}_{wr}kt.dat",
                        index=False,
                    )
