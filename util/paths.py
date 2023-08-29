import os
import yaml

from typing import Dict

repo_name = "saildrone_mission_tools"
atcf_archive = "https://ftp.nhc.noaa.gov/atcf/archive"
atcf_storm_archive = "https://ftp.nhc.noaa.gov/atcf/aid_public"
atcf_btk_archive = "https://ftp.nhc.noaa.gov/atcf/btk"
buoy_archive = "https://www.ndbc.noaa.gov/data/realtime2/"
jason3_archive = "https://www.ncei.noaa.gov/data/oceans/jason3/gdr/gdr"
nhc_outlook_archive = "https://www.nhc.noaa.gov/archive/xgtwo/atl"
saildrone_archive = "https://data.pmel.noaa.gov/generic/erddap/tabledap/"
recon_mission_archive = "https://www.tropicaltidbits.com/data"
recon_mission_archive_high_density_obs = (
    "https://www.nhc.noaa.gov/archive/recon/2023/AHONT1"
)
recon_mission_archive_dropsonde = "https://www.nhc.noaa.gov/archive/recon/2023/REPNT3"

url_buoy_info = "https://www.ndbc.noaa.gov/station_page.php?station="
url_glider_franklin = (
    "http://dockserver.skio.uga.edu/images/franklin/franklin_wptlatlonDate.txt"
)
url_glider_unit1091 = (
    "http://dockserver.skio.uga.edu/images/unit_1091/unit_1091_wptlatlonDate.txt"
)


def repository_path() -> str:
    """
    Retrieves the path to the git repository

    Returns:
    - string
    """
    dir = os.getcwd().split(os.sep)
    repo_idx = dir.index(repo_name) + 1
    repo_path = f"{os.sep}".join(dir[:repo_idx])

    return repo_path


repo_path = repository_path()


def read_yaml_config(filename: str) -> Dict:
    """
    Reads the yaml config file.

    Returns:
    - dictionary of yaml contents
    """

    with open(filename, "r") as file:
        config = yaml.safe_load(file)

    return config


def check_for_dir_create(dirname: str, empty: bool = False):
    """
    Checks if directories along dirname exist, and if not, it creates them.
    """
    if not os.path.isdir(dirname):
        dirs = dirname.split(os.sep)
        repo_idx = dirs.index(repo_name) + 1
        for dir in range(repo_idx, len(dirs)):
            dir_path = f"{os.sep}".join(dirs[: dir + 1])
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)

    elif empty == True:
        fls = os.listdir(dirname)
        for fl in fls:
            os.remove(f"{dirname}{os.sep}{fl}")
