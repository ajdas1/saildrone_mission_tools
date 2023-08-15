import pandas as pd
import urllib.request

from conversions import coordinate_degrees_minutes_to_decimal
from datetime import datetime, timedelta

### URLs for glider positions were provided by Catherine Edwards. 


print()
log_start_time = datetime.strptime("1970-01-01", "%Y-%m-%d")
# Franklin
url_glider = "http://dockserver.skio.uga.edu/images/franklin/franklin_wptlatlonDate.txt"
page = str(urllib.request.urlopen(url_glider).read())
tmp = page.split("\\n")
category = [tm.split(" ")[0][:-1].split("'")[-1] for tm in tmp if len(tm) > 5]


lat = [coordinate_degrees_minutes_to_decimal(tm.split(" ")[1]) for tm in tmp if len(tm) > 5]
lon = [coordinate_degrees_minutes_to_decimal(tm.split(" ")[2]) for tm in tmp if len(tm) > 5]
time = [log_start_time + timedelta(seconds=float(tm.split(" ")[3])) for tm in tmp if len(tm) > 5]

df = pd.DataFrame([], columns=["category", "lat", "lon", "time"])
df.category = category
df.lat = lat
df.lon = lon
df.time = time
df = df[df.category == "GPS"]

print(
    "Latest coordinates for Franklin (lat, lon) \n" + 
    f"({df[df.time == max(df.time)].lat.values[0]:.4f}, " + 
    f"{df[df.time == max(df.time)].lon.values[0]:.4f}) @ " + 
    f"{df[df.time == max(df.time)].time.dt.strftime('%Y-%m-%d %H:%M UTC').values[0]}" + 
    "\n"
    )

# Franklin
url_glider = "http://dockserver.skio.uga.edu/images/franklin/franklin_wptlatlonDate.txt"
page = str(urllib.request.urlopen(url_glider).read())
tmp = page.split("\\n")
category = [tm.split(" ")[0][:-1].split("'")[-1] for tm in tmp if len(tm) > 5]


lat = [coordinate_degrees_minutes_to_decimal(tm.split(" ")[1]) for tm in tmp if len(tm) > 5]
lon = [coordinate_degrees_minutes_to_decimal(tm.split(" ")[2]) for tm in tmp if len(tm) > 5]
time = [log_start_time + timedelta(seconds=float(tm.split(" ")[3])) for tm in tmp if len(tm) > 5]

df = pd.DataFrame([], columns=["category", "lat", "lon", "time"])
df.category = category
df.lat = lat
df.lon = lon
df.time = time
df = df[df.category == "GPS"]

print(
    "Latest coordinates for UNIT_1091 (lat, lon) \n" + 
    f"({df[df.time == max(df.time)].lat.values[0]:.4f}, " + 
    f"{df[df.time == max(df.time)].lon.values[0]:.4f}) @ " + 
    f"{df[df.time == max(df.time)].time.dt.strftime('%Y-%m-%d %H:%M UTC').values[0]}"
    + "\n"
    )