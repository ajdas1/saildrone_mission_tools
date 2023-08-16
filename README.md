# saildrone_mission_tools
Helpful tools for Saildrone hurricane mission management.

To create an anaconda environment where the scripts should run smoothly:

```conda env create -f configs/environment.yml```

## Basic directory structure
- **bash**: contains shell scripts that describe the workflow. In a bash environment, you can run all the steps for a specific task in a row.
- **configs**: contains configuration .yml files for different tasks. The config file matches the script name in bash for easier identification.
- **data**: where data for processing will get stored. Might not be there at the beginning, but will get created the first time it is needed.
- **figures**: where images get stored. Might not be there at the beginin,g but will get created the first time it is needed.
- **scripts**: where working scripts are stored - gets called within bash scripts.
- **util**: custom functions.


## Updating glider positions
**bash/get_latest_glider_position.sh**
- retrieves the latest positions for Franklin and Unit_1091 gliders (courtesy of Catherine Edwards).


## Predicting JASON ovelpass times
**bash/download_predic_jason_path.sh**
If downlad_jason3_data is True in the config file:
- downloads the last (4) cycles of JASON-3 satellite data.
- extracts latitude, longitude, and time data.

If predict_overpass_at_location is True:
- for a given point, find the next (5) return times of the satellite overpass based on previous data.

## Downloading atcf forecast and best track data
**bash/download_and_process_atcf_hurricane_data.sh**
-  ```configs/download_and_process_hurricane_data.yml``` determines what to process and where to store it.
- downloads the atcf forecasts and best track data (default from 2001 to 2023).
- renames the files for easier comprehension: *basin_year-storm.dat*.

