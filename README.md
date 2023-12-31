# saildrone_mission_tools
Helpful tools for Saildrone hurricane mission management.

To create an anaconda environment where the scripts should run smoothly, and activate it (this works on Linux/Mac):

```
conda update --all
conda env create -f configs/environment.yml
conda activate sd_mission_tools
```

The first time you run it, you will also need to add the util directory to the path
```
cd util
pwd -- will return a path (e.g., /Users/....../util)
conda develop /Users/....../util (insert the returned path instead of example)
```

See the Wiki for details on each of the tools: <https://github.com/ajdas1/saildrone_mission_tools/wiki>


## Basic directory structure
- **bash**: contains shell scripts that describe the workflow. In a bash environment, you can run all the steps for a specific task in a row.
- **configs**: contains configuration .yml file and the python conda environment that makes everything work.
- **scripts**: where working scripts are stored - gets called within bash scripts.
- **util**: custom functions.


## Updating glider positions
**bash/get_latest_glider_position.sh**
- retrieves the latest positions for Franklin and Unit_1091 gliders (courtesy of Catherine Edwards).

## Downloading the latest saildrone data (low-res)
**bash/download_saildrone_data.sh**

- downloads the latest nc files for the saildrones specified in the config file.

## Predicting JASON ovelpass times
**bash/download_predic_jason_path.sh**

- downloads the last (4) cycles of JASON-3 satellite data.
- extracts latitude, longitude, and time data.
- for a given point, find the next (n) return times of the satellite overpass based on previous data.


## Comparing latest observations at a buoy to saildrone
**/bash/download_buoy_data.sh**

- downloads the latest data at the specified NDBC buoy locations.


## Creating NHC 7-day outlook figures with historical storms
**bash/process_nhc_outlook_areas.sh**

- downloads the atcf forecasts and best track data (default from 2002 to 2023).
- renames the files for easier comprehension and cleans them up: *basin_year-storm.dat*.
- separates data into different wind speed radii (34-, 50, and 64-kt) products.
- downloads the latest NHC outlook advisories and compiles historical storms that started within the highlighted regions. Makes figures.
- downloads the current invest and storm best track and forecast data. Makes figures.
- create a PDF document with all the figures.

To create the pdf files, there's some additional software that needs to be installed: 
- *ImageMagick* <https://imagemagick.org/script/download.php>
- *pdflatex* <https://www.latex-project.org/get/>

## Real-time aircraft reconnaissance plotting
**/bash/download_plot_latest_aircraft_recon.sh**

- downloads and decodes the recon observations - flight level and dropsonde position
- plots on a map with saildrone locations

## Reconnaissance aircraft dropsondes in range of saildrone
**/bash/download_process_aircraft_dropsonde_saildrone.sh**

After all dropsondes are uploaded (a day or two after a flight):
- downloads the full dropsonde data
- given a saildrone, produces a list of dropsondes within a given distance of the saildrone