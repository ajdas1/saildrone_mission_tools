import os
import sys

from paths import check_for_dir_create, jason3_archive, read_yaml_config, repo_path
from read_url import get_files_at_url, retrieve_url_file


config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_jason3_data"]:
    sys.exit()

jason_dir = f"{repo_path}{os.sep}" + f"{config['download_jason3_data_path']}"

check_for_dir_create(jason_dir)


all_records = get_files_at_url(url=jason3_archive)
all_records = [fl for fl in all_records if "/cycle" in fl]
all_records = all_records[-config["jason_number_most_recent_cycles_to_download"] :]
for record in range(config["jason_number_most_recent_cycles_to_download"]):
    current_record = all_records[record]
    print(f"Downloading JASON-3 data for cycle {current_record}")
    current_records = get_files_at_url(url=current_record)
    current_records = [fl for fl in current_records if fl[-3:] == ".nc"]
    for num, file in enumerate(current_records):
        filename = file.split("/")[-1]
        if not os.path.isfile(f"{jason_dir}{os.sep}{filename}"):
            retrieve_url_file(file, f"{jason_dir}{os.sep}{filename}")
