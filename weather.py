# Generate a command-line weather forecast tool using OpenWeatherMap API
# The tool should accept a city name and an optional temperature unit flag

from configparser import ConfigParser
import argparse
import json
import sys
from urllib import error, parse, request

PADDING=20
BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# non public function to get the API Key
def _get_api_key():
    config=ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


# parse the command line arguments
def read_user_cli_args():
    parser=argparse.ArgumentParser(
        description="get weather and temperature info for a city"
    )
    parser.add_argument(
        "city", nargs="+", type=str, help="enter the city name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="display the temperature in imperial units",
    )
    return parser.parse_args()

# build the query URL
def build_weather_query(city_input,imperial=False):
    api_key=_get_api_key()
    city_name=" ".join(city_input)
    url_encoded_city_name=parse.quote_plus(city_name)
    units="imperial" if imperial else "metric"
    url=(
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url

# get the weather data from the url using HTTP request
def get_weather_data(query_url):

    try:
        response=request.urlopen(query_url)
    # handle the HTTP errors
    except error.HTTPError as http_error:
        if http_error.code==401:
            sys.exit("Access denied. Check your API key.")
        elif http_error.code==404:
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong.. ({http_error.code})")
    data=response.read()

    # handle the JSON decode error
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")

def display_weather_info(weather_data, imperial=False):
    city=weather_data["name"]
    weather_description=weather_data["weather"][0]["description"]
    temperature=weather_data["main"]["temp"]
    print(f"{city:^PADDING}",end="")
    print(f"\t{weather_description.capitalize():^PADDING}",end=" ")
    print(f"({temperature}°{'F' if imperial else 'C'})")


if __name__=="__main__":
    user_args=read_user_cli_args()
    query_url=build_weather_query(user_args.city,user_args.imperial)
    weather_data=get_weather_data(query_url)
    display_weather_info(weather_data,user_args.imperial)
