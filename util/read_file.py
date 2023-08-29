import numpy as np
import os
import pandas as pd
import shapely.geometry as shp
import xarray as xr

from atcf_processing import (
    adecks_datadir,
    bdecks_datadir,
    column_names,
    column_types,
    fix_atcf_latitude,
    fix_atcf_longitude,
    get_atcf_files,
    get_info_from_filename,
)
from conversions import (
    convert_wind_radii_to_polygon,
    get_aircraft_recon_position,
    get_aircraft_recon_pressure,
)
from datetime import datetime, timedelta
from netCDF4 import Dataset
from typing import Any, List
from paths import repo_path


def decode_drop_position(value: str):
    lat = int(value[:4]) / 100.0
    lon = int(value[5:10]) / 100.0
    if value[4] == "S":
        lat *= -1
    if value[10] == "W":
        lon *= -1

    return lat, lon


def decode_temperature(value: str):
    if value[:2] in ["88", "77", "//"]:
        temp = np.nan
        dewpoint = np.nan
    else:
        temp = value[:3]
        dpd = value[3:]

        try:
            temp = int(temp) / 10.0
        except ValueError:
            temp = np.nan
        try:
            dpd = int(dpd) / 10.0
            dewpoint = temp - dpd
        except ValueError:
            dewpoint = np.nan

        if temp > 99:
            temp = np.nan
            dewpoint = np.nan

    return temp, dewpoint


def decode_wind(value: str):
    if value[:2] in ["88", "77", "//"]:
        u_wind = np.nan
        v_wind = np.nan

    else:
        try:
            dir = int(value[:3])
        except ValueError:
            dir = np.nan
        dir = (90 - dir) % 360

        try:
            spd = int(value[3:])
        except ValueError:
            spd = np.nan

        u_wind = spd * np.cos(np.deg2rad(dir))
        v_wind = spd * np.sin(np.deg2rad(dir))
    return u_wind, v_wind


def decode_pressure_geopotential(value: str, part: str):
    lev = value[:2]

    if lev == "00":
        if part == "a":
            p_level = 1000
            try:
                geo = int(value[2:])
            except ValueError:
                geo = np.nan
        elif part == "b":
            p_level = int(value[2:])
            geo = np.nan
            lev = "surface"
            if p_level < 100:
                p_level += 1000
    elif lev == "92":
        p_level = 925
        try:
            geo = int(value[2:])
        except ValueError:
            geo = np.nan

    elif lev == "85":
        p_level = 850
        try:
            geo = int(value[2:]) + 1000
        except ValueError:
            geo = np.nan
    elif lev == "70":
        p_level = 700
        try:
            geo = int(value[2:]) + 3000
        except ValueError:
            geo = np.nan
    elif lev == "99":
        try:
            p_level = int(value[2:])
        except ValueError:
            p_level = np.nan
        geo = 0
        lev = "surface"
        if p_level < 100:
            p_level += 1000

    elif lev in ["11", "22", "33", "44", "55", "66", "77", "88", "99"]:
        try:
            p_level = int(value[2:])
        except ValueError:
            p_level = np.nan
        geo = np.nan

    return lev, p_level, geo


def read_dropsonde_part_a_pgtw(data: List[str], drop_dict: dict) -> dict:
    part_a_pressure_indicators = ["99", "00", "92", "85", "70"]
    pressure_indices = {
        idx: aidx
        for idx in part_a_pressure_indicators
        for aidx, val in enumerate(data)
        if val[:2] == idx
    }

    pressure = []
    geopotential = []
    temperature = []
    dewpoint = []
    u_wind = []
    v_wind = []
    for lev in part_a_pressure_indicators:
        if lev in pressure_indices:
            _, p_level, geo = decode_pressure_geopotential(
                value=data[pressure_indices[lev]], part="a"
            )
            pressure.append(p_level)
            geopotential.append(geo)
            try:
                temp, dwpt = decode_temperature(value=data[pressure_indices[lev] + 1])
                temperature.append(temp)
                dewpoint.append(dwpt)
            except IndexError:
                temperature.append(np.nan)
                dewpoint.append(np.nan)
            try:
                u, v = decode_wind(value=data[pressure_indices[lev] + 2])
                u_wind.append(u)
                v_wind.append(v)
            except IndexError:
                u_wind.append(np.nan)
                v_wind.append(np.nan)

    drop_dict["pressure"] += pressure
    drop_dict["geopotential"] += geopotential
    drop_dict["temperature"] += temperature
    drop_dict["dewpoint"] += dewpoint
    drop_dict["u"] += u_wind
    drop_dict["v"] += v_wind

    return drop_dict


def read_dropsonde_part_a_position(
    data: List[str], drop_dict: dict, drop_date: datetime
) -> dict:
    data_orig = [el for el in data]

    data = " ".join(data).split(" ")
    possible_split_drop = ["R", "RE", "REL"]
    possible_split_splash = ["S", "SP", "SPG"]
    if any(x in data for x in possible_split_drop):
        try:
            data = data[data.index("REL") : -1]
        except ValueError:
            data = data_orig
            data = "".join(data).split(" ")
            data = data[data.index("REL") : -1]
    elif any(x in data for x in possible_split_splash):
        try:
            data = data[data.index("SPG") : -1]
        except ValueError:
            data = data_orig
            data = "".join(data).split(" ")
            data = data[data.index("SPG") : -1]

    if len(data) > 6:
        data = data_orig
        data = "".join(data).split(" ")
        data = data[data.index("REL") : -1]
    elif 3 < len(data) < 6:
        data = data_orig
        data = "".join(data).split(" ")
        try:
            data = data[data.index("SPG") : -1]
        except ValueError:
            data = data[data.index("REL") : -1]

    if len(data) == 3:
        if data[0] == "SPG":
            drop_dict["start_time"] = [np.datetime64("NaT")]
            drop_dict["end_time"] = [
                drop_date.replace(
                    hour=int(data[2][:2]),
                    minute=int(data[2][2:4]),
                    second=int(data[2][4:6]),
                )
            ]
            drop_lat, drop_lon = decode_drop_position(data[1])
            drop_dict["start_lon"] = [np.nan]
            drop_dict["start_lat"] = [np.nan]
            drop_dict["end_lon"] = [drop_lon]
            drop_dict["end_lat"] = [drop_lat]
        elif data[0] == "REL":
            drop_dict["start_time"] = [
                drop_date.replace(
                    hour=int(data[2][:2]),
                    minute=int(data[2][2:4]),
                    second=int(data[2][4:6]),
                )
            ]
            drop_dict["end_time"] = [np.datetime64("NaT")]
            drop_lat, drop_lon = decode_drop_position(data[1])
            drop_dict["start_lon"] = [drop_lon]
            drop_dict["start_lat"] = [drop_lat]
            drop_dict["end_lon"] = [np.nan]
            drop_dict["end_lat"] = [np.nan]
    elif len(data) == 6:
        drop_dict["start_time"] = [
            drop_date.replace(
                hour=int(data[2][:2]),
                minute=int(data[2][2:4]),
                second=int(data[2][4:6]),
            )
        ]
        drop_dict["end_time"] = [
            drop_date.replace(
                hour=int(data[5][:2]),
                minute=int(data[5][2:4]),
                second=int(data[5][4:6]),
            )
        ]
        drop_lat, drop_lon = decode_drop_position(data[1])
        drop_dict["start_lon"] = [drop_lon]
        drop_dict["start_lat"] = [drop_lat]
        drop_lat, drop_lon = decode_drop_position(data[4])
        drop_dict["end_lon"] = [drop_lon]
        drop_dict["end_lat"] = [drop_lat]
    else:
        print("something strange happened with drop position.")

    return drop_dict


def read_dropsonde_part_b_pt(data: List[str], drop_dict: dict) -> dict:
    part_b_pressure_indicators = ["11", "22", "33", "44", "55", "66", "77", "88", "99"]
    pressure_indices = {
        idx: aidx
        for idx in part_b_pressure_indicators
        for aidx, val in enumerate(data)
        if val[:2] == idx
    }

    pressure = []
    geopotential = []
    temperature = []
    dewpoint = []
    u_wind = []
    v_wind = []
    for lev in part_b_pressure_indicators:
        if lev in pressure_indices:
            _, p_level, geo = decode_pressure_geopotential(
                value=data[pressure_indices[lev]], part="b"
            )
            pressure.append(p_level)
            geopotential.append(geo)
            try:
                temp, dwpt = decode_temperature(value=data[pressure_indices[lev] + 1])
                temperature.append(temp)
                dewpoint.append(dwpt)
            except IndexError:
                temperature.append(np.nan)
                dewpoint.append(np.nan)

            u_wind.append(np.nan)
            v_wind.append(np.nan)

    drop_dict["pressure"] += pressure
    drop_dict["geopotential"] += geopotential
    drop_dict["temperature"] += temperature
    drop_dict["dewpoint"] += dewpoint
    drop_dict["u"] += u_wind
    drop_dict["v"] += v_wind

    return drop_dict


def read_dropsonde_part_b_pw(data: List[str], drop_dict: dict) -> dict:
    part_b_pressure_indicators = ["11", "22", "33", "44", "55", "66", "77", "88", "99"]
    pressure_indices = {
        idx: aidx
        for idx in part_b_pressure_indicators
        for aidx, val in enumerate(data)
        if val[:2] == idx
    }

    pressure = []
    geopotential = []
    temperature = []
    dewpoint = []
    u_wind = []
    v_wind = []
    for lev in part_b_pressure_indicators:
        if lev in pressure_indices:
            _, p_level, geo = decode_pressure_geopotential(
                value=data[pressure_indices[lev]], part="b"
            )
            pressure.append(p_level)
            geopotential.append(geo)
            try:
                u, v = decode_wind(value=data[pressure_indices[lev] + 1])
                u_wind.append(u)
                v_wind.append(v)
            except IndexError:
                u_wind.append(np.nan)
                v_wind.append(np.nan)

            temperature.append(np.nan)
            dewpoint.append(np.nan)

    drop_dict["pressure"] += pressure
    drop_dict["geopotential"] += geopotential
    drop_dict["temperature"] += temperature
    drop_dict["dewpoint"] += dewpoint
    drop_dict["u"] += u_wind
    drop_dict["v"] += v_wind

    return drop_dict


def interpret_dropsonde_text_file(data: List[str], filename: str) -> pd.DataFrame:
    drop_dict = {}
    drop_date = datetime.strptime(filename.split(".")[-2], "%Y%m%d%H%M")
    data = [line.rstrip() for line in data]
    data = [line for line in data if len(line) >= 2]
    section_idx = [idx for idx, line in enumerate(data) if "XX" in line]
    data_a = data[section_idx[0] : section_idx[1]]
    data_b = data[section_idx[1] :]

    data_a_sections = ["XXAA ", "31313", "61616", "62626"]
    section_idx = {
        sec: idx
        for sec in data_a_sections
        for idx, line in enumerate(data_a)
        if line[:5] == sec
    }

    data_a_pgtw = data_a[section_idx["XXAA "] : section_idx["31313"]]
    data_a_pgtw = " ".join(data_a_pgtw).split("  ")[1].split(" ")
    idx_start = [idx for idx, el in enumerate(data_a_pgtw) if el[:2] == "99"][-1]
    data_a_pgtw = data_a_pgtw[idx_start:]
    data_a_pgtw = [el for el in data_a_pgtw if el[:2] not in ["77", "88"]]
    drop_dict = {
        "pressure": [],
        "geopotential": [],
        "temperature": [],
        "dewpoint": [],
        "u": [],
        "v": [],
    }
    drop_dict = read_dropsonde_part_a_pgtw(data=data_a_pgtw, drop_dict=drop_dict)

    data_a_fl = data_a[section_idx["61616"] : section_idx["62626"]]
    data_a_fl = [el for el in " ".join(data_a_fl).split(" ") if len(el) > 0][1:]
    drop_dict["aircraft"] = [data_a_fl[0]]
    drop_dict["flight_id"] = [data_a_fl[1]]
    drop_dict["storm"] = [data_a_fl[2]]
    drop_dict["obs_id"] = [data_a_fl[4]]

    data_a_pos = data_a[section_idx["62626"] :]
    drop_dict = read_dropsonde_part_a_position(
        data=data_a_pos, drop_dict=drop_dict, drop_date=drop_date
    )

    data_b_sections = ["XXBB ", "21212", "31313", "61616", "62626"]
    section_idx = {
        sec: idx
        for sec in data_b_sections
        for idx, line in enumerate(data_b)
        if line[:5] == sec
    }

    data_b_pt = data_b[section_idx["XXBB "] : section_idx["21212"]]
    data_b_pt = " ".join(data_b_pt).split("  ")[1].split(" ")
    idx_start = [idx for idx, el in enumerate(data_b_pt) if el[:2] == "00"][-1]
    data_b_pt = data_b_pt[idx_start:]
    drop_dict = read_dropsonde_part_b_pt(data=data_b_pt, drop_dict=drop_dict)

    data_b_pw = data_b[section_idx["21212"] : section_idx["31313"]]
    data_b_pw = " ".join(data_b_pw).split(" ")[1:]
    drop_dict = read_dropsonde_part_b_pw(data=data_b_pw, drop_dict=drop_dict)

    drop_data = pd.DataFrame(
        [], columns=list(drop_dict.keys()), index=range(len(drop_dict["pressure"]))
    )

    for key in drop_dict:
        vals = drop_dict[key]
        if len(vals) == 1:
            vals = vals * len(drop_dict["pressure"])
        drop_data[key] = vals

    drop_data = drop_data.sort_values(by="pressure", ascending=False).reset_index(
        drop=True
    )

    return drop_data


def combine_aircraft_recon_drop(
    data: List[str],
    flight: str,
    flight_list: List[str],
    recon_dir: str,
    center: str = "KNHC",
) -> List:
    data_idx = [idx for idx, fl in enumerate(flight_list) if fl == flight]
    drop_data = [dat for idx, dat in enumerate(data) if idx in data_idx]
    if len(drop_data) > 0:
        drop_data = pd.concat(drop_data)

    return data_idx, drop_data


def combine_aircraft_recon_hdob(
    data: List[str],
    flight: str,
    flight_list: List[str],
    recon_dir: str,
    center: str = "KNHC",
) -> List:
    data_idx = [idx for idx, fl in enumerate(flight_list) if fl == flight]
    flight_data = [dat for idx, dat in enumerate(data) if idx in data_idx]
    flight_date = [
        datetime.strptime(dat[2].split(" ")[-1], "%Y%m%d") for dat in flight_data
    ]
    flight_data = [dat[3:] for dat in flight_data]
    flight_data = [
        read_aircraft_recon_hdob_file(dat, flight_date=flight_date[idx]).round(2)
        for idx, dat in enumerate(flight_data)
    ]
    flight_data = pd.concat(flight_data).sort_values(by="time").reset_index(drop=True)
    filename = f"{recon_dir}{os.sep}{center}_{flight_date[0].strftime('%Y%m%d')}_{flight.replace(' ', '-')}.csv"
    flight_data.to_csv(filename, index=False)

    return data_idx


def read_aircraft_recon_hdob_file(
    data: List[str], flight_date: datetime
) -> pd.DataFrame:
    data = [line.rstrip().split(" ") for line in data]
    time = [
        flight_date.replace(
            hour=int(line[0][:2]),
            minute=int(line[0][2:4]),
            second=int(line[0][4:6]),
            microsecond=0,
        )
        for line in data
    ]
    lat = [get_aircraft_recon_position(value=line[1]) for line in data]
    lon = [get_aircraft_recon_position(value=line[2]) for line in data]
    pres = [get_aircraft_recon_pressure(value=line[3]) for line in data]
    temp = [int(line[6]) / 10.0 if line[6] != "////" else np.nan for line in data]
    dewp = [int(line[7]) / 10.0 if line[7] != "////" else np.nan for line in data]
    wdir = [int(line[8]) // 1000 if line[8] != "//////" else np.nan for line in data]
    wspd = [int(line[8]) % 1000 if line[8] != "//////" else np.nan for line in data]
    peak_wind = [int(line[9]) if line[9] != "///" else np.nan for line in data]
    peak_surf_wind = [int(line[10]) if line[10] != "///" else np.nan for line in data]
    rain_rate = [int(line[11]) if line[11] != "///" else np.nan for line in data]

    ids = [idx for idx, tm in enumerate(time) if tm < time[0]]
    for id in ids:
        time[id] = time[id] + timedelta(days=1)

    data = pd.DataFrame(
        [],
        columns=[
            "time",
            "lat",
            "lon",
            "pressure",
            "temperature",
            "dewpoint",
            "wind_direction",
            "wind_speed",
            "peak_wind",
            "peak_surface_wind",
            "rain_rate",
        ],
    )
    data.time = pd.to_datetime(time)
    data.lat = lat
    data.lon = lon
    data.pressure = pres
    data.temperature = temp
    data.dewpoint = dewp
    data.wind_direction = wdir
    data.wind_speed = wspd
    data.peak_wind = peak_wind
    data.peak_surface_wind = peak_surf_wind
    data.rain_rate = rain_rate

    return data


# def read_aircraft_recon_hdob_file(filename: str, current_time: datetime):

#     with open(filename) as file:
#         data = file.readlines()
#     data = data[5:]
#     data = [line.rstrip().split(" ") for line in data]
#     if data[0][0] >= current_time.strftime("%H%M%S"):
#         date = current_time - timedelta(days=1)
#     else:
#         date = current_time

#     time = [date.replace(hour=int(line[0][:2]), minute=int(line[0][2:4]), second=int(line[0][4:6]), microsecond=0) for line in data]
#     lat = [get_aircraft_recon_position(value=line[1]) for line in data]
#     lon = [get_aircraft_recon_position(value=line[2]) for line in data]
#     pres = [get_aircraft_recon_pressure(value=line[3]) for line in data]
#     geopotential = [int(line[4]) if line[4] != "/////" else np.nan for line in data]
#     psfc_extrap = [get_aircraft_recon_pressure(value=line[5]) if pres[idx] >= 550. else np.nan for idx, line in enumerate(data)]
#     temp = [int(line[6])/10. if line[6] != "////" else np.nan for line in data]
#     dewp = [int(line[7])/10. if line[7] != "////" else np.nan for line in data]
#     wdir = [int(line[8])//1000 if line[8] != "//////" else np.nan for line in data]
#     wspd = [int(line[8])%1000 if line[8] != "//////" else np.nan for line in data]
#     peak_wind = [int(line[9]) if line[9] != "///" else np.nan for line in data]
#     peak_surf_wind = [int(line[10]) if line[10] != "///" else np.nan for line in data]
#     rain_rate = [int(line[11]) if line[11] != "///" else np.nan for line in data]

#     data = pd.DataFrame([], columns=["time", "lat", "lon", "pressure", "temperature", "dewpoint", "wind_direction", "wind_speed", "peak_wind", "peak_surface_wind", "rain_rate"])
#     data.time = time
#     data.lat = lat
#     data.lon = lon
#     data.pressure = pres
#     data.temperature = temp
#     data.dewpoint = dewp
#     data.wind_direction = wdir
#     data.wind_speed = wspd
#     data.peak_wind = peak_wind
#     data.peak_surface_wind = peak_surf_wind
#     data.rain_rate = rain_rate

#     return data


def remove_atcf_duplicates(data: dict):
    data_clean = {}
    searched = []
    skip = []
    for btk_c in data:
        if btk_c not in skip:
            slon_c = data[btk_c].Longitude.iloc[0]
            slat_c = data[btk_c].Latitude.iloc[0]
            stime_c = data[btk_c].Valid.iloc[0]
            btk_others = [btk for btk in data if not btk in searched + [btk_c]]
            duplicates = [btk_c]
            for btk_o in btk_others:
                slon_o = data[btk_o].Longitude.iloc[0]
                slat_o = data[btk_o].Latitude.iloc[0]
                stime_o = data[btk_o].Valid.iloc[0]
                if (slon_o == slon_c) and (slat_o == slat_c) and (stime_o == stime_c):
                    duplicates.append(btk_o)

            if len(duplicates) == 1:
                data_clean[btk_c] = data[btk_c]
            elif len(duplicates) == 2:
                duplicates = sorted(duplicates)
                data_clean[btk_c] = data[duplicates[0]]
                skip = duplicates[1]

            searched.append(btk_c)

    return data_clean


def read_raw_atcf(filename: str) -> pd.DataFrame:
    df = pd.read_csv(
        filename,
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

    return df


def read_all_btks(wr: int = 0) -> list[pd.DataFrame]:
    fls = get_atcf_files()
    btks = []
    for fl in fls:
        _, _, btk = read_atcf_modified_wind_radii(
            filename=fl, wr=wr, fcst=False, btk=True
        )
        if btk is not None:
            btk["Center"] = btk[["Longitude", "Latitude"]].apply(shp.Point, axis=1)
            btk["WindRadii"] = btk.apply(convert_wind_radii_to_polygon, axis=1)
            btks.append(btk)

    return btks


def read_atcf_modified_wind_radii(
    filename: str, wr: int, fcst: bool = True, btk: bool = True
) -> List[Any]:
    storm_info = get_info_from_filename(filename=f"{adecks_datadir}{filename}")

    if fcst:
        current_filename = (
            f"{adecks_datadir}wind_radii/{filename[:-4]}_{wr}kt{filename[-4:]}"
        )
        if os.path.isfile(current_filename):
            df_fcst = pd.read_csv(current_filename, header=0, delimiter=",")
            df_fcst.Date = pd.to_datetime(df_fcst.Date)
            df_fcst["Valid"] = df_fcst.Date + pd.to_timedelta(
                df_fcst.FcstHour, unit="hr"
            )
        else:
            df_fcst = None
    else:
        df_fcst = None

    if btk:
        current_filename = (
            f"{bdecks_datadir}wind_radii/{filename[:-4]}_{wr}kt{filename[-4:]}"
        )
        if os.path.isfile(current_filename):
            df_btk = pd.read_csv(current_filename, header=0, delimiter=",")
            df_btk.Date = pd.to_datetime(df_btk.Date)
            df_btk["Valid"] = df_btk.Date + pd.to_timedelta(df_btk.FcstHour, unit="hr")
        else:
            df_btk = None
    else:
        df_btk = None

    return storm_info, df_fcst, df_btk


def read_saildrone_latest_position(config: dict):
    datadir = f"{repo_path}{os.sep}{config['download_saildrone_data_path']}"
    fls = sorted(os.listdir(datadir))

    sd_data = {}

    for fl in fls:
        sd_number = fl.split("_")[0][2:]
        data = Dataset(f"{datadir}/{fl}", "r")
        lat = np.array(data["latitude"])
        lon = np.array(data["longitude"])
        data.close()
        lat = lat[~np.isnan(lat)]
        lon = lon[~np.isnan(lon)]
        dlat = lat[-1] - lat[-2]
        dlon = lon[-1] - lon[-2]
        dir = (90 + (360 - (np.rad2deg(np.arctan2(dlat, dlon)) % 360))) % 360

        sd_data[sd_number] = {
            "lon": lon[-1],
            "lat": lat[-1],
            "dir": dir,
        }

    return sd_data


def read_ndbc_buoy_format(filename: str) -> pd.DataFrame:
    with open(filename, "r") as fl:
        data = fl.readlines()
    data = [line.rstrip().split() for line in data]

    header = data[:2]
    data = data[2:]
    date = [
        datetime.strptime(line[0] + line[1] + line[2] + line[3] + line[4], "%Y%m%d%H%M")
        for line in data
    ]
    wdir = [float(line[5]) if line[5] != "MM" else np.nan for line in data]
    wspd = [float(line[6]) if line[6] != "MM" else np.nan for line in data]
    gst = [float(line[7]) if line[7] != "MM" else np.nan for line in data]
    wvht = [float(line[8]) if line[8] != "MM" else np.nan for line in data]
    dpd = [float(line[9]) if line[9] != "MM" else np.nan for line in data]
    apd = [float(line[10]) if line[10] != "MM" else np.nan for line in data]
    mwd = [float(line[11]) if line[11] != "MM" else np.nan for line in data]
    pres = [float(line[12]) if line[12] != "MM" else np.nan for line in data]
    atmp = [float(line[13]) if line[13] != "MM" else np.nan for line in data]
    wtmp = [float(line[14]) if line[14] != "MM" else np.nan for line in data]
    dewp = [float(line[15]) if line[15] != "MM" else np.nan for line in data]
    vis = [float(line[16]) if line[16] != "MM" else np.nan for line in data]
    ptdy = [float(line[17]) if line[17] != "MM" else np.nan for line in data]
    tide = [float(line[18]) if line[18] != "MM" else np.nan for line in data]

    df = pd.DataFrame([])
    df["date"] = date
    df["wind_direction"] = wdir
    df["wind_speed"] = wspd
    df["wind_gust"] = gst
    df["significant_wave_height"] = wvht
    df["dominant_wave_period"] = dpd
    df["average_wave_period"] = apd
    df["dwpd_direction"] = mwd
    df["sea_level_pressure"] = pres
    df["air_temperature"] = atmp
    df["sea_surface_temperature"] = wtmp
    df["dewpoint_temperature"] = dewp
    df["visibility"] = vis
    df["pressure_tendency"] = ptdy
    df["tide_level"] = tide

    return df


def read_saildrone_format(filename: str) -> pd.DataFrame:
    data = (
        xr.open_dataset(filename, drop_variables=["trajectory", "obs", "rowSize"])
        .to_dataframe()
        .reset_index(drop=True)
    )

    try:
        data = data.rename(columns={"time": "date"})
    except:
        pass

    try:
        data = data.rename(columns={"WIND_FROM_MEAN": "wind_direction"})
    except:
        pass

    try:
        data = data.rename(columns={"WIND_SPEED_MEAN": "wind_speed"})
    except:
        pass

    try:
        data = data.rename(columns={"TEMP_AIR_MEAN": "air_temperature"})
    except:
        pass

    try:
        data = data.rename(columns={"RH_MEAN": "relative_humidity"})
    except:
        pass

    try:
        data = data.rename(columns={"BARO_PRES_MEAN": "sea_level_pressure"})
    except:
        pass

    try:
        data = data.rename(columns={"WAVE_DOMINANT_PERIOD": "dominant_wave_period"})
    except:
        pass

    try:
        data = data.rename(
            columns={"WAVE_SIGNIFICANT_HEIGHT": "significant_wave_height"}
        )
    except:
        pass

    try:
        data = data.rename(columns={"TEMP_SBE37_MEAN": "sea_surface_temperature"})
    except:
        pass

    try:
        data = data.rename(columns={"SAL_SBE37_MEAN": "sea_surface_salinity"})
    except:
        pass

    return data
