import requests
import pandas as pd
from google.transit import gtfs_realtime_pb2
from datetime import datetime
import os

def fetch_raw_feed(category: str) -> bytes : # returning realtime data in bytes
    response = requests.get(
        "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana",
        params = {"category" : category}
    )
    response.raise_for_status # throws an error if the request failed
    return response.content


def decode_feed(raw_bytes :  bytes) -> gtfs_realtime_pb2.FeedMessage :
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw_bytes)
    return feed


def feed_to_dataframe(feed: gtfs_realtime_pb2.FeedMessage) -> pd.DataFrame:
    rows = []
    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue  # skip entities that aren't vehicle position updates
        v = entity.vehicle
        rows.append({
            "vehicle_id": v.vehicle.id,
            "trip_id": v.trip.trip_id,
            "route_id": v.trip.route_id,
            "latitude": v.position.latitude,
            "longitude": v.position.longitude,
            "bearing": v.position.bearing,
            "timestamp": v.timestamp,
        })
    return pd.DataFrame(rows)


def save_snapshot(df: pd.DataFrame, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filepath = os.path.join(out_dir, f"positions_{now}.csv")
    df.to_csv(filepath, index=False)


