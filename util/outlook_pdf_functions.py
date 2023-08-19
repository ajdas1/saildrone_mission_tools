
import os
import pytz
import re
import subprocess

from datetime import datetime, timedelta
from paths import repo_path

from conversions import convert_time_to_utc


class LatexFile:
    text = []
    title = ""
    author = ""
    date = ""

    def __init__(self, text=text, title=title, author=author, date=date):
        self.text = text
        self.title = title
        self.author = author
        self.date = date


    def clear_text(self):
        self.text = []

    def preamble(self):
        self.text.append(r"\documentclass[aspectration=169, 10pt]{beamer}")
        self.text.append(r"\usetheme{default}")
        self.text.append(r"\usecolortheme{dolphin}")
        self.text.append(r"\usepackage{animate}")
        self.text.append(r"\usepackage{multicol}")

    def begin_document(self):
        self.text.append(r"\begin{document}")

    def end_document(self):
        self.text.append(r"\end{document}")

    def begin_frame(self):
        self.text.append(r"\begin{frame}")

    def end_frame(self):
        self.text.append(r"\end{frame}")

    def begin_twocol(self):
        self.text.append(r"\begin{multicols}{2}")

    def end_twocol(self):
        self.text.append(r"\end{multicols}")

    def add_titlepage(self):
        self.text.append(r"\title{" + self.title + r"}")
        self.text.append(r"\author{" + self.author + r"}")
        self.text.append(r"\date{" + self.date.strftime('%Y-%m-%d %H:%M') + r"}")
        self.begin_frame()
        self.text.append(r"\titlepage")
        self.end_frame()

    def include_figure_if_exists(self, file: str, image_width: str, otherwise: str = ""):
        tmp = r"\IfFileExists{" + file + r"}{\includegraphics[width={" + image_width + r"}]{" + file + r"}}{" + otherwise + r"}"
        self.text.append(tmp)
    
    def add_text(self, text: str):
        self.text.append(text)

    def add_animation(self, file_match: str, number_of_figures: int):
        tmp = r"\begin{figure}\animategraphics[controls=all, width=\textwidth]{2}{" + file_match + r"}{01}{" + f"{number_of_figures:02d}" + r"}\end{figure}"
        self.text.append(tmp)

    def write_to_file(self, pdf_dir: str):
        filename = f"{self.date.strftime('%Y%m%d_%H%M')}.tex"
        
        with open(f"{pdf_dir}{os.sep}{filename}", "w") as file:
            for line in self.text:
                file.write(line + "\n")
        
        return filename




def write_latex_file(time: datetime, sd_data: dict, fig_dir_outlook: str, pdf_dir: str, config: dict, fig_dir_invest: str = None) -> str:

    fls_outlook = os.listdir(fig_dir_outlook)
    n_pages = int(len([fl for fl in fls_outlook if re.match("^.*area\d.png$", fl)]))


    latex = LatexFile(author=f"{config['document_author']}", title="TC Outlook Areas", date=time)
    latex.clear_text()
    latex.preamble()
    latex.begin_document()
    latex.add_titlepage()

    # outlook areas and sd positions
    latex.begin_frame()
    latex.include_figure_if_exists(file=f"{fig_dir_outlook}/outlook_areas.png", image_width=r".7\textwidth")
    latex.add_text(text=r"\\" + f"SD positions at {convert_time_to_utc(time=datetime.now(), timezone=pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M')} UTC (lon, lat, heading)" + r"\\")
    latex.begin_twocol()
    for sd in sd_data:
        latex.add_text(text=r"{\footnotesize" + f" SD{sd} ({sd_data[sd]['lon']:.2f}, {sd_data[sd]['lat']:.2f}, {sd_data[sd]['dir']:.2f}°)" + r"} \\")
    latex.end_twocol()
    latex.end_frame()

    # invest track and intensity
    if fig_dir_invest is not None:
        invests = config["invests_of_interest"].split(", ")
        n_invests = len(invests)
        for invest in range(n_invests):
            latex.begin_frame()
            latex.add_text(text=f"Invest {invests[invest]} Track and Intensity Forecasts" + r"\\")
            latex.begin_twocol()
            latex.include_figure_if_exists(file=f"{fig_dir_invest}/{invests[invest]}_track.png", image_width=r".5\textwidth")
            latex.include_figure_if_exists(file=f"{fig_dir_invest}/{invests[invest]}_intensity.png", image_width=r".5\textwidth")
            latex.end_twocol()
            latex.end_frame()



    # one page per outlook area - historical 34-kt winds
    for page in range(1, n_pages+1):
        latex.begin_frame()
        latex.add_text(text="For all storms that began in a given outlook area, colors represent the number of storms with 34+kt winds." + r"\\")
        latex.include_figure_if_exists(file=f"{fig_dir_outlook}/outlook_areas_btks_area{page}.png", image_width=r"\textwidth")
        latex.end_frame()

    for area in range(1, n_pages+1):
        figs = sorted([fl for fl in fls_outlook if f"outlook_areas_btks_area{area}_day" in fl])
        n_figs = len(figs)
        if n_figs > 0:
            latex.begin_frame()
            latex.add_text(text="For all storms that began in a given outlook area, colors represent the number of storms with 34+kt winds." + r"\\")
            latex.add_animation(file_match=f"{fig_dir_outlook}/outlook_areas_btks_area{area}_day", number_of_figures=n_figs)
            latex.end_frame()

    latex.end_document()

    filename = latex.write_to_file(pdf_dir=pdf_dir)

    return filename





# def write_latex_file(time: datetime, sd_data: dict, fig_dir: str, pdf_dir: str, config: dict) -> str:

#     fls = os.listdir(fig_dir)


#     document_title = r"\title{}"  #
#     document_author = r"\author{}" #
#     document_date = r"\date{}" #
#     document_begin_frame = r"\begin{frame}" #
#     document_end_frame = r"\end{frame}" #
#     document_exist_frame = r"\IfFileExists{}{\includegraphics[width={}]{}}{}"
#     document_multicol_start = r"\begin{multicols}{2}" #
#     document_multicol_end = r"\end{multicols}" #
#     document_begin = r"\begin{document}" #
#     document_end = r"\end{document}" #
#     document_autoplay = r"\begin{figure}\animategraphics[controls=all, width=\textwidth]{2}{}{01}{}\end{figure}"
#     document_header = r"\documentclass[aspectration=169, 10pt]{beamer}" + "\n" + r"\usetheme{default}" + "\n" + r"\usecolortheme{dolphin}" + "\n" + r"\usepackage{animate}" + "\n" + r"\usepackage{multicol}" #
#     title_page = r"\titlepage" #

#     new_document = [] #
#     new_document.append(document_header) #
#     new_document.append(modify_latex_command(line=[document_title], insert=["TC Outlook Areas"])) #
#     new_document.append(modify_latex_command(line=[document_author], insert=[f"{config['document_author']}"])) #
#     new_document.append(modify_latex_command(line=[document_date], insert=[time.strftime('%Y-%m-%d %H:%M')])) #
#     new_document.append(document_begin) #
#     new_document.append(document_begin_frame) #
#     new_document.append(title_page) #
#     new_document.append(document_end_frame) #

#     # add frame for all outlook areas
#     new_document.append(document_begin_frame) #
#     new_document.append(modify_latex_command(line=[document_exist_frame], insert=[f"{fig_dir}/outlook_areas.png", r".7\textwidth", f"{fig_dir}/outlook_areas.png", ""])) #
#     new_document.append(r"\\" + f"SD positions at {convert_time_to_utc(time=datetime.now(), timezone=pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M')} UTC (lon, lat, heading)" + r"\\") #
#     new_document.append(document_multicol_start) #
#     for sd in sd_data:
#         new_document.append(r"{\footnotesize" + f" SD{sd} ({sd_data[sd]['lon']:.2f}, {sd_data[sd]['lat']:.2f}, {sd_data[sd]['dir']:.2f}°)" + r"} \\")
#     new_document.append(document_multicol_end)
#     new_document.append(document_end_frame)

#     # add frame for individual outlook areas with ts winds - 4 areas per page
#     n_areas = len([fl for fl in fls if re.match("^.*area\d.png$", fl)])

#     n_pages = int(n_areas)
#     for page in range(n_pages):
#         new_document.append(document_begin_frame)
#         new_document.append("For all storms that began in a given outlook area, colors represent the number of storms with 34+kt winds." + r"\\")
#         new_document.append(modify_latex_command(line=[document_exist_frame], 
#                                             insert=[f"{fig_dir}/outlook_areas_btks_area{page+1}.png", r"\textwidth", f"{fig_dir}/outlook_areas_btks_area{page+1}.png", ""]
#                                             ))
#         new_document.append(document_end_frame)

#     # add frame for each animation
#     for n in range(1, n_areas+1):
#         figs = sorted([fl for fl in fls if f"outlook_areas_btks_area{n}_day" in fl])
#         n_figs = len(figs)

#         if n_figs > 0:
#             new_document.append(document_begin_frame)
#             new_document.append("For all storms that began in a given outlook area, colors represent the number of storms with 34+kt winds." + r"\\")
#             new_document.append(modify_latex_command(line=[document_autoplay], 
#                                                  insert=[f"{fig_dir}/outlook_areas_btks_area{n}_day", f"{n_figs:02d}"]
#                                                  ))
#             new_document.append(document_end_frame)

#     new_document.append(document_end)

#     new_filename = f"{time.strftime('%Y%m%d_%H%M')}.tex"
#     with open(f"{pdf_dir}{os.sep}{new_filename}", "w") as file:
#         _ = [file.write(line) for line in new_document]


#     return new_filename




def clean_up_outlook_data(time: datetime, data_dir: str):

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





def create_figure_packet_outlook(fig_dir: str, summary_dir: str, config: dict, remove_orig: bool = True) -> None:

    
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

