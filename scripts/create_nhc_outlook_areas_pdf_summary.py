


import importlib

import os


import paths
importlib.reload(paths)
import outlook_pdf_functions
importlib.reload(outlook_pdf_functions)

from datetime import datetime
from outlook_pdf_functions import clean_up_data, compile_latex_file, create_figure_packet, write_latex_file
from paths import check_for_dir_create, read_yaml_config, repo_path
from read_file import read_saildrone_latest_position



config_file = f"{repo_path}{os.sep}configs{os.sep}config.yml"
config = read_yaml_config(config_file)

data_dir = f"{repo_path}{os.sep}{config['download_nhc_outlook_data_path']}"
fig_dir = f"{repo_path}{os.sep}{config['figure_path']}{os.sep}" + f"{config['outlook_figure_path']}{os.sep}"
summary_dir = f"{fig_dir}{config['summary_figure_path']}"
check_for_dir_create(summary_dir, empty=True)
summary_pdf_dir = f"{repo_path}{os.sep}{config['summary_pdf_path']}"
check_for_dir_create(summary_pdf_dir)
sd_position = read_saildrone_latest_position()



fig_dirs = [fdir for fdir in os.listdir(fig_dir) if ("latest" not in fdir)]
fig_dir_times = [datetime.strptime(fl, "%Y%m%d%H%M") for fl in fig_dirs]
latest_outlook_time = max(fig_dir_times) 
fig_dir += fig_dirs[fig_dir_times.index(latest_outlook_time)]



print("     Creating figure packet and pdf output.")
create_figure_packet(time=latest_outlook_time, fig_dir=fig_dir, summary_dir=summary_dir, config=config, remove_orig=config["remove_original_figure_folder"])
latex_file = write_latex_file(time=datetime.now(), sd_data=sd_position, fig_dir=summary_dir, pdf_dir=summary_pdf_dir, config=config)
compile_latex_file(filename=latex_file, save_dir=summary_pdf_dir, remove_tex=True)
if config["remove_original_data_folder"]:
    clean_up_data(time=latest_outlook_time, data_dir=data_dir)

