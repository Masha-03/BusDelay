import pandas as pd
from src.cleaning.geo_utils import haversine_distance_km


def match_arrival_to_stop(positions: pd.DataFrame, stop_times: pd.DataFrame, stops: pd.DataFrame, radius_m: float = 100) -> pd.DataFrame:
    stop_times_geo = stop_times.merge(stops[["stop_id", "stop_lat", "stop_lon"]], on="stop_id")

    records = []
    for trip_id, trip_positions in positions.groupby("trip_id"):
        trip_positions = trip_positions.sort_values("timestamp")
        trip_stops = stop_times_geo[stop_times_geo["trip_id"] == trip_id].sort_values("stop_sequence")

        for _, stop_row in trip_stops.iterrows():
            distances_m = trip_positions.apply(
                lambda row: haversine_distance_km(
                    row["latitude"], row["longitude"],
                    stop_row["stop_lat"], stop_row["stop_lon"]
                ) * 1000,
                axis=1
            )
            nearby = trip_positions[distances_m <= radius_m]
            if len(nearby) > 0:
                records.append({
                    "trip_id": trip_id,
                    "route_id": trip_positions["route_id"].iloc[0],
                    "stop_id": stop_row["stop_id"],
                    "scheduled_arrival": stop_row["arrival_time"],
                    "actual_arrival_ts": nearby["timestamp"].min(),
                })
    return pd.DataFrame(records)


def compute_delay(matched: pd.DataFrame) -> pd.DataFrame:
    matched["actual_arrival_dt"] = pd.to_datetime(matched["actual_arrival_ts"], unit="s", utc=True).dt.tz_convert("Asia/Kuala_Lumpur")
    matched["service_date"] = matched["actual_arrival_dt"].dt.date.astype(str)

    matched["scheduled_arrival_dt"] = pd.to_datetime(
        matched["service_date"] + " " + matched["scheduled_arrival"],
        errors="coerce"
    ).dt.tz_localize("Asia/Kuala_Lumpur")

    matched["delay_minutes"] = (
        matched["actual_arrival_dt"] - matched["scheduled_arrival_dt"]
    ).dt.total_seconds() / 60

    return matched