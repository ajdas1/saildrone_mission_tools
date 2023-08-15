import os
import yaml

from typing import Dict

repo_name = "saildrone_mission_tools"
atcf_archive = "https://ftp.nhc.noaa.gov/atcf/archive/"


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


def check_for_dir_create(dirname: str):
    """
    Checks if directories along dirname exist, and if not, it creates them.
    """
    if not os.path.isdir(dirname):
        dirs = dirname.split(os.sep)
        repo_idx = dirs.index(repo_name) + 1
        for dir in range(repo_idx, len(dirs)):
            dir_path = f"{os.sep}".join(dirs[: dir + 1])
            print(dir_path)
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)
