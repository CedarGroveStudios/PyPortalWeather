# PyPortal Weather Station
# Copyright 2018, 2019, 2020, 20221, 2022 by JG for Cedar Grove Maker Studios
#
# pyportal_weather_code.py 2022-07-11 v7.1.0711

import sys
import time
import board
import supervisor
from adafruit_pyportal import PyPortal
import openweather_graphics  # pylint: disable=wrong-import-position

print("running pyportal_weather_code.py")

# Reduce status neopixel brightness to help keep things cool on error exit
# TODO: reduce TFT backlight brightness upon exit
supervisor.set_rgb_status_brightness(16)

# Force a restart upon error exit to keep things alive when the eventual
#   internet error happens
supervisor.set_next_code_file(filename="code.py", reload_on_error=True)

cwd = ("/"+__file__).rsplit('/', 1)[0] # The current working directory
sys.path.append(cwd)

# Get wifi details and more from the secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("Secrets.py not found.")
    raise

# Use cityname, country code where countrycode is ISO3166 format.
#   e.g. "New York, US" or "London, GB"
LOCATION = "LosAngeles, CA, US"

UNITS = "imperial"  # Standard(SI units is default), imperial, or metric

# Set up where we'll be fetching data from
DATA_SOURCE = "http://api.openweathermap.org/data/2.5/weather?q=" + LOCATION + "&units=" + UNITS
DATA_SOURCE += "&appid=" + secrets["openweather_token"]

# The token from openweather.org; e.g. "b6907d289e10d714a6e88b30761fae22"
DATA_LOCATION = []

# Initialize the pyportal object with data source and location
pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=0x000000)

pyportal.set_backlight(0.75)
gfx = openweather_graphics.OpenWeather_Graphics(pyportal.splash, am_pm=True, celsius=False)

localtile_refresh = None
weather_refresh = None

# Play storm tracker welcome audio; True disables speaker after playing
pyportal.play_file("storm_tracker.wav", wait_to_finish=True)

while True:
    # Only query the online time once per hour (and on first run)
    if (not localtile_refresh) or (time.monotonic() - localtile_refresh) > 3600:
        try:
            print("Getting time from internet!")
            pyportal.get_local_time()
            localtile_refresh = time.monotonic()
        except (ValueError, RuntimeError) as e:
            # ValueError added from quote.py change
            print("Some error occured, retrying! -", e)
            continue

    # Only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        try:
            value = pyportal.fetch()
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
        except (ValueError, RuntimeError) as e:
            # ValueError added from quote.py change
            print("Some error occured, retrying! -", e)
            continue

    gfx.update_time()
    time.sleep(30)  # Wait 30 seconds before updating anything again
