# openweather_graphics.py updated for CircuitPython v7.1.0 2022-05-14
import time
import json
import board
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)

small_font = cwd+"/fonts/Arial-12.bdf"
medium_font = cwd+"/fonts/Arial-16.bdf"
large_font = cwd+"/fonts/Arial-Bold-24.bdf"

compass = ['North @', 'NE @', 'East @', 'SE @', 'South @', 'SW @', 'West @', 'NW @']

class OpenWeather_Graphics(displayio.Group):
    def __init__(self, root_group, *, am_pm=True, celsius=True):
        super().__init__()
        self.am_pm = am_pm
        self.celsius = celsius

        root_group.append(self)
        self._icon_group = displayio.Group()
        self.append(self._icon_group)
        self._text_group = displayio.Group()
        self.append(self._text_group)

        self._icon_sprite = None
        self._icon_file = None
        self.set_icon(cwd+"/weather_background.bmp")

        self.small_font = bitmap_font.load_font(small_font)
        self.medium_font = bitmap_font.load_font(medium_font)
        self.large_font = bitmap_font.load_font(large_font)

        # Glyph loading not required; speeds up initial screen loading
        glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
        self.small_font.load_glyphs(glyphs)
        self.small_font.load_glyphs(('°',))  # a non-ascii character we need
        self.medium_font.load_glyphs(glyphs)
        self.medium_font.load_glyphs(('°',))  # a non-ascii character we need
        self.large_font.load_glyphs(glyphs)
        self.large_font.load_glyphs(('°',))  # a non-ascii character we need

        self.city_text = None

        self.time_text = Label(self.medium_font)
        self.time_text.anchor_point = (1.0, 0.5)
        self.time_text.anchored_position = (board.DISPLAY.width - 10, 22)
        self.time_text.color = 0xFFFFFF
        self._text_group.append(self.time_text)

        self.sunrise_text = Label(self.small_font)
        self.sunrise_text.anchor_point = (1.0, 0.5)
        self.sunrise_text.anchored_position = (board.DISPLAY.width - 10, 46)
        self.sunrise_text.color = 0xFFFF00
        self._text_group.append(self.sunrise_text)

        self.sunset_text = Label(self.small_font)
        self.sunset_text.anchor_point = (1.0, 0.5)
        self.sunset_text.anchored_position = (board.DISPLAY.width - 10, 62)
        self.sunset_text.color = 0xFF8000
        self._text_group.append(self.sunset_text)

        self.windspeed_text = Label(self.medium_font)
        self.windspeed_text.x = 15
        self.windspeed_text.y = 48
        self.windspeed_text.color = 0xFFFFFF
        self._text_group.append(self.windspeed_text)

        self.windgust_text = Label(self.small_font)
        self.windgust_text.x = 15
        self.windgust_text.y = 74
        self.windgust_text.color = 0xFF0000
        self._text_group.append(self.windgust_text)

        self.temp_text = Label(self.large_font)
        self.temp_text.anchor_point = (1.0, 0.5)
        self.temp_text.anchored_position = (board.DISPLAY.width - 10, 190)
        self.temp_text.color = 0xFFFFFF
        self._text_group.append(self.temp_text)

        self.humid_text = Label(self.small_font)
        self.humid_text.anchor_point = (0, 0.5)
        self.humid_text.anchored_position = (15, 226)
        self.humid_text.color = 0xFF00FF
        self._text_group.append(self.humid_text)

        self.pressure_text = Label(self.small_font)
        self.pressure_text.anchor_point = (0.5, 0.5)
        self.pressure_text.anchored_position = (board.DISPLAY.width // 2, 226)
        self.pressure_text.color = 0xFF00FF
        self._text_group.append(self.pressure_text)

        self.dew_point_text = Label(self.small_font)
        self.dew_point_text.anchor_point = (1.0, 0.5)
        self.dew_point_text.anchored_position = (board.DISPLAY.width - 10, 226)
        self.dew_point_text.color = 0xFF00FF
        self._text_group.append(self.dew_point_text)

        self.main_text = Label(self.large_font)
        self.main_text.anchor_point = (0, 0.5)
        self.main_text.anchored_position = (15, 182)
        """self.main_text.x = 15
        self.main_text.y = 182"""
        self.main_text.color = 0xFFFFFF
        self._text_group.append(self.main_text)

        self.description_text = Label(self.small_font)
        self.description_text.anchor_point = (0, 0.5)
        self.description_text.anchored_position = (15, 206)
        """self.description_text.x = 15
        self.description_text.y = 207"""
        self.description_text.color = 0xFFFFFF
        self._text_group.append(self.description_text)

    def display_weather(self, weather):
        weather = json.loads(weather)

        # set the icon/background
        weather_icon = weather['weather'][0]['icon']
        self.set_icon(cwd+"/icons/"+weather_icon+".bmp")

        # city_name =  weather['name'] + ", " + weather['sys']['country']
        city_name =  weather['name']
        print(city_name)
        if not self.city_text:
            self.city_text = Label(self.medium_font, text=city_name)
            self.city_text.x = 15
            self.city_text.y = 22
            self.city_text.color = 0xFF00FF
            self._text_group.append(self.city_text)

        self.update_time()

        try:
            wind_dir = weather['wind']['deg']
            wind_dir_tx = compass[int(((wind_dir + 22.5) % 360) / 45)]
        except:
            wind_dir_tx = "----"

        try:
            wind_gust = weather['wind']['gust']
            print(f"{wind_gust:.0f} MPH Gusts")
            self.windgust_text.text = f"{wind_gust:.0f} MPH Gusts"
        except:
            self.windgust_text.text = " " * 15  # 15 spaces

        windspeed = weather['wind']['speed']
        if wind_dir_tx != "----":
            print(f"{wind_dir_tx} {windspeed:.0f} MPH")
            self.windspeed_text.text = f"{wind_dir_tx} {windspeed:.0f} MPH"
        else:
            print("No wind")
            self.windspeed_text.text = "No wind"

        sunrise = weather['sys']['sunrise']
        sunrise_hr = (time.localtime(sunrise).tm_hour - 7) % 24
        sunrise_min = time.localtime(sunrise).tm_min
        if self.am_pm:
            if sunrise_hr >= 12:
                sunrise_hr -= 12
                post_time = " PM"
            else:
                post_time = " AM"
            if sunrise_hr == 0: sunrise_hr = 12
        print(f"Rise {sunrise_hr}:{sunrise_min:02d}{post_time}")
        self.sunrise_text.text = f"Rise {sunrise_hr}:{sunrise_min:02d}{post_time}"

        sunset = weather['sys']['sunset']
        sunset_hr = (time.localtime(sunset).tm_hour -7) % 24
        sunset_min = time.localtime(sunset).tm_min
        if self.am_pm:
            if sunset_hr >= 12:
                sunset_hr -= 12
                post_time = " PM"
            else:
                post_time = " AM"
            if sunset_hr == 0: sunset_hr = 12
        print(f"Set {sunset_hr}:{sunset_min:02d}{post_time}")
        self.sunset_text.text = f"Set {sunset_hr}:{sunset_min:02d}{post_time}"

        main_text = weather['weather'][0]['main']
        print(main_text)
        self.main_text.text = main_text

        temperature = weather['main']['temp'] # its...in kelvin
        print(temperature)
        if self.celsius:
            self.temp_text.text = f"{temperature:.1f} °C"
        else:
            self.temp_text.text = f"{temperature:.0f} °F"

        description = weather['weather'][0]['description']
        description = description[0].upper() + description[1:]
        print(description)
        self.description_text.text = description
        # "thunderstorm with heavy drizzle"

        humidity = weather['main']['humidity']  # % humidity
        print(f"{humidity:.0f} %")
        self.humid_text.text = f"{humidity:.0f} %"

        pressure = weather['main']['pressure']  # kPa (kilo-Pascals)
        pressure = pressure * 0.0295300  # convert to in Hg
        print(f"{pressure:0.2f} inHg")
        self.pressure_text.text = f"{pressure:0.2f} inHg"

        if not self.celsius:
            dp_temp = (temperature - 32) * (5 / 9)  #convert to C
        else:
            dp_temp = temperature
        dew_point = ((humidity / 100) ** 0.125) * (112 + (0.9 * dp_temp)) + (0.1 * dp_temp) - 112
        dew_point = (dew_point * 1.8) + 32  # convert back to F
        print(f"DP {dew_point:.0f} °F")
        self.dew_point_text.text = f"DP {dew_point:.0f} °F"

    def update_time(self):
        """Fetch the time.localtime(), parse it out and update the display text"""
        now = time.localtime()
        hour = now[3]
        minute = now[4]
        format_str = "%d:%02d"
        if self.am_pm:
            if hour >= 12:
                hour -= 12
                format_str = format_str+" PM"
            else:
                format_str = format_str+" AM"
            if hour == 0:
                hour = 12
        time_str = format_str % (hour, minute)
        print(time_str)
        self.time_text.text = time_str

    def set_icon(self, filename):
        """The background image to a bitmap file.

        :param filename: The filename of the chosen icon
        """
        print("Set icon to ", filename)
        if self._icon_group:
            self._icon_group.pop()

        if not filename:
            return  # we're done, no icon desired
        if self._icon_file:
            self._icon_file.close()
        self._icon_file = open(filename, "rb")
        icon = displayio.OnDiskBitmap(self._icon_file)
        try:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter())
        except TypeError:
            self._icon_sprite = displayio.TileGrid(icon,
                                                   pixel_shader=displayio.ColorConverter(),
                                                   position=(0,0))
        self._icon_group.append(self._icon_sprite)
        board.DISPLAY.refresh()
