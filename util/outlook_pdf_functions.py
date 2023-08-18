


from datetime import datetime
from paths import check_for_dir_create








def create_figure_packet(time: datetime, figdir: str, remove_orig: bool = True) -> None:

    tmpdir = f"{figdir}/latest"
    figdir_current = create_directory_for_time(time=time, savedir=figdir)

    fls = os.listdir(tmpdir)
    for fl in fls:
        os.remove(f"{tmpdir}/{fl}")
    
    # move all files to latest directory
    fls = sorted(os.listdir(figdir_current))
    if remove_orig:
        for fl in fls:
            os.rename(f"{figdir_current}/{fl}", f"{tmpdir}/{fl}")
        os.rmdir(figdir_current)
    else:
        for fl in fls:
            _ = subprocess.check_call(["cp", f"{figdir_current}/{fl}", f"{tmpdir}/{fl}"])
    fls = fls[1:]

    figure_dims = [check_figure_dimensions(filename=fl, figdir=tmpdir) for fl in fls][1:]
    unique_dims = list(set(figure_dims))
    max_xdim = max([ud[0] for ud in unique_dims])
    max_ydim = max([ud[1] for ud in unique_dims])
    if len(unique_dims) > 1:
        _ = [match_max_image_dimensions(filename=fl, figdir=tmpdir, xdim=max_xdim, ydim=max_ydim) for fl in fls]

    # add colorbar
    _ = [append_colorbar_to_image(filename=fl, figdir=tmpdir) for fl in fls if fl != "outlook_areas.png"]

    # create animation
    fig_areas = []
    fl_areas = [fl for fl in fls if len(fl) == 28]
    for idx, area in enumerate(fl_areas):
        area_base = area[:-4]
        try:
            _ = subprocess.check_call(["convert", "-delay", "50", "-loop", "0", f"{tmpdir}/{area_base}_day*", f"{tmpdir}/{area_base}_anim.gif"])
        except:
            pass


