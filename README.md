# saildrone_mission_tools
Helpful tools for Saildrone hurricane mission management.

To create an anaconda environment where the scripts should run smoothly:

```conda env create -f configs/environment.yml```

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

If `download_saildrone_data` is `True` in the config file:
- downloads the latest nc files for the saildrones specified in the config file.

## Predicting JASON ovelpass times
**bash/download_predic_jason_path.sh**

If `downlad_jason3_data` is `True` in the config file:
- downloads the last (4) cycles of JASON-3 satellite data.
- extracts latitude, longitude, and time data.

If `jason_predict_overpass_at_location` is `True`:
- for a given point, find the next (n) return times of the satellite overpass based on previous data.


## Comparing latest observations at a buoy to saildrone
**/bash/download_buoy_data.sh**

If `download_buoy_data` is `True` in the config file:
- downloads the latest data at the specified NDBC buoy locations.

### IN PROGRESS
## Downloading atcf forecast and best track data
**bash/download_and_process_atcf_hurricane_data.sh**
-  ```configs/download_and_process_hurricane_data.yml``` determines what to process and where to store it.
- downloads the atcf forecasts and best track data (default from 2001 to 2023).
- renames the files for easier comprehension: *basin_year-storm.dat*.

