# saildrone_mission_tools
Helpful tools for Saildrone hurricane mission management.

To create an anaconda environment where the scripts should run smoothly:

```conda env create -f configs/environment.yml```

## Updating glider positions
**bash/get_latest_glider_position.sh**
- retrieves the latest positions for Franklin and Unit_1091 gliders (courtesy of Catherine Edwards).

## Downloading atcf forecast and best track data
**bash/download_and_process_atcf_hurricane_data.sh**
-  ```configs/download_and_process_hurricane_data.yml``` determines what to process and where to store it.
- downloads the atcf forecasts and best track data (default from 2001 to 2023).
- renames the files for easier comprehension: *basin_year-storm.dat*.

