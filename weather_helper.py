import openmeteo_requests

import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=300)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "current": ["precipitation", "weather_code"],
}


# Create an info class to store the weather data
class WeatherInfo:
    rain_intensity = 0.0
    cloud_intensity = 0.0
    lightning = False
    skybox_color = (0, 0, 0)

    def __init__(self, rain_intensity, cloud_intensity, lightning, skybox_color):
        self.rain_intensity = rain_intensity
        self.cloud_intensity = cloud_intensity
        self.lightning = lightning
        self.skybox_color = skybox_color

    def __str__(self):
        return f"Rain: {self.rain_intensity}, Clouds: {self.cloud_intensity}, Lightning: {self.lightning} Skybox: {self.skybox_color}"


def get_weather_info():
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    precipitation = response.Current().Variables(0).Value()
    weather_code = response.Current().Variables(1).Value()
    # print(f"Precipitation: {precipitation}, Weather Code: {weather_code}")

    # https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM
    if weather_code // 10 == 5:
        # Drizzle
        rain_intensity = 0.05
    elif weather_code // 10 == 6:
        # Rain
        rain_intensity = 0.1
    else:
        rain_intensity = 0.0

    # Set cloud intensity
    if weather_code >= 50 and weather_code < 80 and weather_code % 10 in [4, 5]:
        cloud_intensity = 1.0
    elif weather_code // 10 == 4:
        cloud_intensity = 0.5
    elif weather_code == 3:
        cloud_intensity = 0.5
    elif weather_code > 80:
        cloud_intensity = 1.0
    else:
        cloud_intensity = 0.0

    # Set lightning
    if weather_code > 80:
        lightning = True
    else:
        lightning = False

    # Just leave skybox at a low white for now
    skybox_color = (10, 10, 10)
    return WeatherInfo(rain_intensity, cloud_intensity, lightning, skybox_color)


if __name__ == "__main__":
    print(get_weather_info())
