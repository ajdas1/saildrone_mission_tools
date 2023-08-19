import importlib


import os
import sys


import paths
importlib.reload(paths)
import read_url
importlib.reload(read_url)


from paths import atcf_invest_archive, check_for_dir_create, read_yaml_config, repo_path
from read_url import get_files_at_url



config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

if not config["download_nhc_invest_data"]:
    sys.exit()


invest_dir = (
    f"{repo_path}{os.sep}"
    + f"{config['download_nhc_invest_data_path']}"
)
check_for_dir_create(invest_dir)

all_records = get_files_at_url(url=atcf_invest_archive)

# print(f"Downloading ATCF data for year {year}")
# current_url = f"{atcf_archive}{year}{os.sep}"
# page = requests.get(current_url).text
# soup = BeautifulSoup(page, "html.parser")
# all_records = [f"{current_url}/{node.get('href')}" for node in soup.find_all("a")]
# a_records = [rec for rec in all_records if "aal" in rec]
#    b_records = [rec for rec in all_records if "bal" in rec]
