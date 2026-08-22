import requests
from src.ingestion.weather import get_weather_data

RT_URL = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl"
STATIC_URL = "https://api.data.gov.my/gtfs-static/prasarana?category=rapid-bus-kl"

rt_response = requests.get(RT_URL)
static_response = requests.get(STATIC_URL)

weather_df = get_weather_data()

print(weather_df.head())