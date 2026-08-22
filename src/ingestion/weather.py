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

    # clean data:
    # convert date
    df["date"] = pd.to_datetime(df["date"])

    # make sure temperatures are numeric
    df["min_temp"] = pd.to_numeric(df["min_temp"], errors="coerce")
    df["max_temp"] = pd.to_numeric(df["max_temp"], errors="coerce")

    # remove duplicate rows
    df = df.drop_duplicates()

    return df

def clean_weather_data(df):
    # Remove duplicates
    df = df.drop_duplicates()

    # Drop rows missing important identifiers
    df = df.dropna(
        subset=[
            "location_id",
            "location_name",
            "date"
        ]
    )

    # Fill missing temperatures using the median
    df["min_temp"] = df["min_temp"].fillna(
        df["min_temp"].median()
    )

    df["max_temp"] = df["max_temp"].fillna(
        df["max_temp"].median()
    )

    # Fill missing forecast text
    forecast_columns = [
        "morning_forecast",
        "afternoon_forecast",
        "night_forecast"
    ]

    df[forecast_columns] = df[forecast_columns].fillna("Unknown")

    return df

def validate_weather_data(df):
    print(df.isnull().sum())
    print("Duplicates:", df.duplicated().sum())
