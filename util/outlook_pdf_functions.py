
import os
import pytz
import re
import subprocess

from datetime import datetime, timedelta
from paths import repo_path

from conversions import convert_time_to_utc




def clean_up_data(time: datetime, data_dir: str):

    datadir_current = f"{data_dir}{os.sep}{time.strftime('%Y%m%d%H%M')}"
    fls = os.listdir(datadir_current)
    _ = [os.remove(f"{datadir_current}/{fl}") for fl in fls]
    os.rmdir(datadir_current)





def compile_latex_file(filename: str, save_dir: str, remove_tex: bool = True):
  
    compile_pdf = [
        "pdflatex", "--shell-escape", "--file-line-error", 
        f"-output-directory={save_dir}", f"{save_dir}/{filename}"
        ]
    subprocess.check_call(compile_pdf, stdout=subprocess.DEVNULL)
    subprocess.check_call(compile_pdf, stdout=subprocess.DEVNULL)

    fls = os.listdir(save_dir)
    if remove_tex:
        fls = [fl for fl in fls if ".pdf" not in fl]
        _ = [os.remove(f"{save_dir}/{fl}") for fl in fls]




def write_latex_file(time: datetime, sd_data: dict, fig_dir: str, pdf_dir: str, config: dict) -> str:

    fls = os.listdir(fig_dir)


    document_title = r"\title{}" 
    document_author = r"\author{}"
    document_date = r"\date{}"
    document_begin_frame = r"\begin{frame}"
    document_end_frame = r"\end{frame}"
    document_exist_frame = r"\IfFileExists{}{\includegraphics[width={}]{}}{}"
    document_multicol_start = r"\begin{multicols}{2}"
    document_multicol_end = r"\end{multicols}"
    document_begin = r"\begin{document}"
    document_end = r"\end{document}"
    document_autoplay = r"\begin{figure}\animategraphics[controls=all, width=\textwidth]{2}{}{01}{}\end{figure}"
    document_header = r"\documentclass[aspectration=169, 10pt]{beamer}" + "\n" + r"\usetheme{default}" + "\n" + r"\usecolortheme{dolphin}" + "\n" + r"\usepackage{animate}" + "\n" + r"\usepackage{multicol}"
    title_page = r"\titlepage"

    new_document = []
    new_document.append(document_header)
    new_document.append(modify_latex_command(line=[document_title], insert=["TC Outlook Areas"]))
    new_document.append(modify_latex_command(line=[document_author], insert=[f"{config['document_author']}"]))
    new_document.append(modify_latex_command(line=[document_date], insert=[time.strftime('%Y-%m-%d %H:%M')]))
    new_document.append(document_begin)
    new_document.append(document_begin_frame)
    new_document.append(title_page)
    new_document.append(document_end_frame)

    # add frame for all outlook areas
    new_document.append(document_begin_frame)
    new_document.append(modify_latex_command(line=[document_exist_frame], insert=[f"{fig_dir}/outlook_areas.png", r".7\textwidth", f"{fig_dir}/outlook_areas.png", ""]))
    new_document.append(r"\\" + f"SD positions at {convert_time_to_utc(time=datetime.now(), timezone=pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M')} UTC (lon, lat, heading)" + r"\\")
    new_document.append(document_multicol_start)
    for sd in sd_data:
        new_document.append(r"{\footnotesize" + f" SD{sd} ({sd_data[sd]['lon']:.2f}, {sd_data[sd]['lat']:.2f}, {sd_data[sd]['dir']:.2f}°)" + r"} \\")
    new_document.append(document_multicol_end)
    new_document.append(document_end_frame)

    # add frame for individual outlook areas with ts winds - 4 areas per page
    n_areas = len([fl for fl in fls if re.match("^.*area\d.png$", fl)])

    n_pages = int(n_areas)
    for page in range(n_pages):
        new_document.append(document_begin_frame)
        new_document.append("For all storms that began in a given outlook area, colors represent the number of storms with 34+kt winds." + r"\\")
        new_document.append(modify_latex_command(line=[document_exist_frame], 
                                            insert=[f"{fig_dir}/outlook_areas_btks_area{page+1}.png", r"\textwidth", f"{fig_dir}/outlook_areas_btks_area{page+1}.png", ""]
                                            ))
        new_document.append(document_end_frame)

    # add frame for each animation
    for n in range(1, n_areas+1):
        figs = sorted([fl for fl in fls if f"outlook_areas_btks_area{n}_day" in fl])
        n_figs = len(figs)

        if n_figs > 0:
            new_document.append(document_begin_frame)
            new_document.append("For all storms that began in a given outlook area, colors represent the number of storms with 34+kt winds." + r"\\")
            new_document.append(modify_latex_command(line=[document_autoplay], 
                                                 insert=[f"{fig_dir}/outlook_areas_btks_area{n}_day", f"{n_figs:02d}"]
                                                 ))
            new_document.append(document_end_frame)

    new_document.append(document_end)

    new_filename = f"{time.strftime('%Y%m%d_%H%M')}.tex"
    with open(f"{pdf_dir}{os.sep}{new_filename}", "w") as file:
        _ = [file.write(line) for line in new_document]


    return new_filename



def modify_latex_command(line: list[str], insert: list[str]) -> list[str]:

    line_text = line[0].split("{}")
    assert len(insert) == len(line_text)-1, "Incorrent number of insert strings."

    tmp = []
    for idx, el in enumerate(insert):
        if idx == 0:
            tmp.append(line_text[idx])
        tmp.append("{" + el + "}")
        tmp.append(line_text[idx+1])
    new_text = "".join(tmp)

    return new_text





def create_figure_packet(time: datetime, fig_dir: str, summary_dir: str, config: dict, remove_orig: bool = True) -> None:

    
    # move all files to latest directory
    fls = sorted(os.listdir(fig_dir))
    if remove_orig:
        for fl in fls:
            os.rename(f"{fig_dir}/{fl}", f"{summary_dir}/{fl}")
        os.rmdir(fig_dir)
    else:
        for fl in fls:
            _ = subprocess.check_call(["cp", f"{fig_dir}/{fl}", f"{summary_dir}/{fl}"])

    fls = [fl for fl in fls if (fl != "outlook_areas.png")]


    figure_dims = [check_figure_dimensions(filename=fl, fig_dir=summary_dir) for fl in fls]
    unique_dims = list(set(figure_dims))
    max_xdim = max([ud[0] for ud in unique_dims])
    max_ydim = max([ud[1] for ud in unique_dims])
    if len(unique_dims) > 1:
        _ = [match_max_image_dimensions(filename=fl, fig_dir=summary_dir, xdim=max_xdim, ydim=max_ydim) for fl in fls]

    # add colorbar
    _ = [append_colorbar_to_image(filename=fl, fig_dir=summary_dir, colorbar=f"{repo_path}{os.sep}{config['summary_figure_colorbar']}") for fl in fls if fl != "outlook_areas.png"]

    # create animation
    fl_areas = [fl for fl in fls if len(fl) == 28]
    for _, area in enumerate(fl_areas):
        area_base = area[:-4]
        try:
            _ = subprocess.check_call(["convert", "-delay", "50", "-loop", "0", f"{summary_dir}/{area_base}_day*", f"{summary_dir}/{area_base}_anim.gif"])
        except:
            pass



def append_colorbar_to_image(filename: str, fig_dir: str, colorbar: str) -> None:

    tmp_filename = f"{filename.split('.')[0]}_tmp.png"

    subprocess.check_call([
        "convert", "+append", 
        f"{fig_dir}/{filename}", colorbar, 
        f"{fig_dir}/{tmp_filename}"
    ])

    os.rename(f"{fig_dir}/{tmp_filename}", f"{fig_dir}/{filename}")
    return None




def match_max_image_dimensions(filename: str, fig_dir: str, xdim: int, ydim: int) -> None:

    tmp_filename = f"{filename.split('.')[0]}_tmp.png"

    subprocess.check_call([
        "magick", "-define", 
        f"png:size={xdim}x{ydim}", f"{fig_dir}/{filename}", 
        "-thumbnail", f"{xdim}x{ydim}>", 
        "-background", "white", "-gravity", "west", "-extent", f"{xdim}x{ydim}", 
        f"{fig_dir}/{tmp_filename}"])

    os.rename(f"{fig_dir}/{tmp_filename}", f"{fig_dir}/{filename}")

    return None




def check_figure_dimensions(filename: str, fig_dir: str) -> tuple:
    tmp = subprocess.check_output(["identify", f"{fig_dir}/{filename}"]).decode("utf-8")
    tmp = tmp.rstrip().split(" ")
    figsize = tmp[2].split("x")
    figsize_x = int(figsize[0])
    figsize_y = int(figsize[1])

    return (figsize_x, figsize_y)

