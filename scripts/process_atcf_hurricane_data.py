import numpy as np
import os
import pandas as pd

from forecast_processing import column_names, column_types, fix_latitude_from_atcf, fix_longitude_from_atcf

filedir_base = "/Users/asavarin/Desktop/saildrone/data/hurricane_forecasts/"

adecks_datadir = f"{filedir_base}atcf_a/original/"
bdecks_datadir = f"{filedir_base}atcf_b/original/"


preprocess_rename = False
preprocess_wind_radii = True

adecks_preprocessed = f"{filedir_base}atcf_a/preprocessed/"
bdecks_preprocessed = f"{filedir_base}atcf_b/preprocessed/"
adecks_fls = sorted(fl for fl in os.listdir(adecks_datadir) if ".dat" in fl and not "al_" in fl)
bdecks_fls = sorted(fl for fl in os.listdir(bdecks_datadir) if ".dat" in fl and not "al_" in fl)
if preprocess_rename:
    for fl in adecks_fls:
        df = pd.read_csv(f"{adecks_datadir}{fl}", header=None, names=column_names, dtype=column_types, delimiter=",", index_col=False, skipinitialspace=True, na_values=["Q"])
        df.Date =  pd.to_datetime(df.Date, format="%Y%m%d%H")
        df.Latitude = df.Latitude.apply(fix_latitude_from_atcf)
        df.Longitude = df.Longitude.apply(fix_longitude_from_atcf)
        df.to_csv(f"{adecks_preprocessed}{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat", index=False)

    for fl in bdecks_fls:
        df = pd.read_csv(f"{bdecks_datadir}{fl}", header=None, names=column_names, dtype=column_types, delimiter=",", index_col=False, skipinitialspace=True)
        df.Date =  pd.to_datetime(df.Date, format="%Y%m%d%H")
        df.Latitude = df.Latitude.apply(fix_latitude_from_atcf)
        df.Longitude = df.Longitude.apply(fix_longitude_from_atcf)
        df.to_csv(f"{bdecks_preprocessed}{fl[1:3]}_{fl[5:9]}-{fl[3:5]}.dat", index=False)


        # df["FcstValid"] = df.Date + pd.to_timedelta(df.FcstHour.astype(int), unit="hours")
        # df["FcstValid"] = df.Date + pd.to_timedelta(df.FcstHour.astype(int), unit="hours")


adecks_windradii = f"{filedir_base}atcf_a/wind_radii/"
bdecks_windradii = f"{filedir_base}atcf_b/wind_radii/"
adecks_fls = sorted(fl for fl in os.listdir(adecks_datadir) if ".dat" in fl and not "al_" in fl)
bdecks_fls = sorted(fl for fl in os.listdir(bdecks_datadir) if ".dat" in fl and not "al_" in fl)
if preprocess_wind_radii:
    for fl in adecks_fls:
        df = pd.read_csv(f"{adecks_datadir}{fl}", header=None, names=column_names, dtype=column_types, delimiter=",", index_col=False, skipinitialspace=True, na_values=["Q"])
        df.Date =  pd.to_datetime(df.Date, format="%Y%m%d%H")
        df.Latitude = df.Latitude.apply(fix_latitude_from_atcf)
        df.Longitude = df.Longitude.apply(fix_longitude_from_atcf)
        df = df.drop(columns=[
            "Technum", "MinSLP", "StormType", "WindCode", "PressureOfLastClosedIsobar", 
            "RadiusOfLastClosedIsobar", "RMW", "Gust", "EyeDiameter", "SubregionCode", 
            "MaxSeas", "ForecasterInitials", "StormDirection", "StormSpeed", "StormDepth", 
            "WaveHeightForRadius", "RadiusQuadrantCode", "SeasRadius1", "SeasRadius2", 
            "SeasRadius3", "SeasRadius4"
            ])
        df = df[df.FcstCenter == "OFCL"]
        df = df.reset_index(drop=True)
        wrs = df.WindIntensityForRadii.unique()
        for wr in wrs:
            df_sub = df[df.WindIntensityForRadii == wr]
            df_sub = df_sub.reset_index(drop=True)
            df_sub = df_sub.drop(columns=["WindIntensityForRadii"])
            if len(df_sub) > 0:
                df_sub.to_csv(f"{adecks_windradii}{fl[1:3]}_{fl[5:9]}-{fl[3:5]}_{wr}kt.dat", index=False)

    for fl in bdecks_fls:
        print(fl)
        df = pd.read_csv(f"{bdecks_datadir}{fl}", header=None, names=column_names, dtype=column_types, delimiter=",", index_col=False, skipinitialspace=True, na_values=["Q"])
        df.Date =  pd.to_datetime(df.Date, format="%Y%m%d%H")
        df.Latitude = df.Latitude.apply(fix_latitude_from_atcf)
        df.Longitude = df.Longitude.apply(fix_longitude_from_atcf)
        df = df.drop(columns=[
            "Technum", "MinSLP", "StormType", "WindCode", "PressureOfLastClosedIsobar", 
            "RadiusOfLastClosedIsobar", "RMW", "Gust", "EyeDiameter", "SubregionCode", 
            "MaxSeas", "ForecasterInitials", "StormDirection", "StormSpeed", "StormDepth", 
            "WaveHeightForRadius", "RadiusQuadrantCode", "SeasRadius1", "SeasRadius2", 
            "SeasRadius3", "SeasRadius4", "FcstCenter", "FcstHour"
            ])
        df = df.reset_index(drop=True)
        wrs = df.WindIntensityForRadii.unique()
        for wr in wrs:
            if not pd.isna(wr):
                if wr > 0:
                    df_sub = df[df.WindIntensityForRadii == wr]
                    df_sub = df_sub.reset_index(drop=True)
                    df_sub = df_sub.drop(columns=["WindIntensityForRadii"])
                    if len(df_sub) > 0:
                        df_sub.to_csv(f"{bdecks_windradii}{fl[1:3]}_{fl[5:9]}-{fl[3:5]}_{wr}kt.dat", index=False)