import requests
import pandas as pd

WEATHER_URL = "https://api.data.gov.my/weather/forecast"

def get_weather_data():
    response = requests.get(
        WEATHER_URL,
        params={
            "limit": 1000
        }
    )

    response.raise_for_status()

    data = response.json()

    rows = []

    for item in data:
        rows.append({
            "location_id": item["location"]["location_id"],
            "location_name": item["location"]["location_name"],
            "date": item["date"],
            "morning_forecast": item["morning_forecast"],
            "afternoon_forecast": item["afternoon_forecast"],
            "night_forecast": item["night_forecast"],
            "min_temp": item["min_temp"],
            "max_temp": item["max_temp"]
        })

    df = pd.DataFrame(rows)

    df["date"] = pd.to_datetime(df["date"])

    return df

