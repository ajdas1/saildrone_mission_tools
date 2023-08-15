import os

repo_name = "saildrone_mission_tools"


def repository_path():
    dir = os.getcwd().split(os.sep)
    repo_idx = dir.index(repo_name) + 1
    repo_path = f"{os.sep}".join(dir[:repo_idx])

    return repo_path

repo_path = repository_path()